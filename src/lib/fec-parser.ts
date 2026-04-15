/**
 * Parseur FEC (Fichier des Écritures Comptables)
 *
 * Format réglementaire (article A47 A-1 du LPF) :
 * - Fichier TXT, séparateur TAB ou pipe (|)
 * - 18 colonnes dans l'ordre :
 *   1. JournalCode     2. JournalLib      3. EcritureNum    4. EcritureDate
 *   5. CompteNum        6. CompteLib       7. CompAuxNum     8. CompAuxLib
 *   9. PieceRef        10. PieceDate      11. EcritureLib   12. Debit
 *  13. Credit          14. EcritureLet    15. DateLet       16. ValidDate
 *  17. Montantdevise   18. Idevise
 * - Dates : AAAAMMJJ
 * - Montants : virgule décimale, pas de séparateur de milliers
 */

import type {
  MonthForecast, KPIs, CompteResultat,
  BalanceAgeeLine, FluxTresorerie,
  OperationComptable, MouvementBanque, Echeance,
} from "./types"

// ── Types internes ──

export interface EcritureFEC {
  journalCode: string
  journalLib: string
  ecritureNum: string
  ecritureDate: string // YYYY-MM-DD après parsing
  compteNum: string
  compteLib: string
  compAuxNum: string
  compAuxLib: string
  pieceRef: string
  pieceDate: string
  ecritureLib: string
  debit: number
  credit: number
  ecritureLet: string
  dateLet: string
  validDate: string
  montantDevise: number
  iDevise: string
}

export interface FECData {
  ecritures: EcritureFEC[]
  compteResultat: CompteResultat
  kpis: KPIs
  balanceClients: BalanceAgeeLine[]
  balanceFournisseurs: BalanceAgeeLine[]
  fluxTresorerie: FluxTresorerie
  forecasts: Record<string, MonthForecast[]>
  operations: OperationComptable[]
  mouvementsBanque: MouvementBanque[]
  echeances: Echeance[]
  nbLignes: number
  nbErreurs: number
  erreurs: string[]
}

// ── Parsing ──

function detectSeparator(firstLine: string): string {
  if (firstLine.includes("\t")) return "\t"
  if (firstLine.includes("|")) return "|"
  return "\t"
}

function parseFECDate(raw: string): string {
  const s = raw.trim()
  if (!s) return ""
  // Format AAAAMMJJ → YYYY-MM-DD
  if (/^\d{8}$/.test(s)) {
    return `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}`
  }
  // Format JJ/MM/AAAA → YYYY-MM-DD
  if (/^\d{2}\/\d{2}\/\d{4}$/.test(s)) {
    return `${s.slice(6, 10)}-${s.slice(3, 5)}-${s.slice(0, 2)}`
  }
  // Format AAAA-MM-JJ → déjà bon
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s
  return ""
}

function parseFECAmount(raw: string): number {
  const s = raw.trim().replace(/\s/g, "").replace(/\u00a0/g, "")
  if (!s) return 0
  // Virgule décimale (format réglementaire) → point
  const normalized = s.replace(",", ".")
  const val = parseFloat(normalized)
  return isNaN(val) ? 0 : Math.round(val)
}

export function parseFECFile(content: string): FECData {
  const lines = content.split(/\r?\n/).filter((l) => l.trim())
  if (lines.length < 2) {
    return emptyFECData(["Fichier vide ou invalide"])
  }

  const sep = detectSeparator(lines[0])
  const headers = lines[0].split(sep).map((h) => h.trim().replace(/^\uFEFF/, ""))

  // Vérifier les colonnes attendues
  const expectedCols = [
    "JournalCode", "JournalLib", "EcritureNum", "EcritureDate",
    "CompteNum", "CompteLib", "CompAuxNum", "CompAuxLib",
    "PieceRef", "PieceDate", "EcritureLib", "Debit", "Credit",
    "EcritureLet", "DateLet", "ValidDate", "Montantdevise", "Idevise",
  ]

  const colIndex: Record<string, number> = {}
  const erreurs: string[] = []

  for (const col of expectedCols) {
    const idx = headers.findIndex((h) => h.toLowerCase() === col.toLowerCase())
    if (idx === -1) {
      erreurs.push(`Colonne manquante : ${col}`)
    }
    colIndex[col] = idx
  }

  // Parser les écritures
  const ecritures: EcritureFEC[] = []
  let nbErreurs = 0

  for (let i = 1; i < lines.length; i++) {
    const cols = lines[i].split(sep)
    if (cols.length < 13) {
      nbErreurs++
      erreurs.push(`Ligne ${i + 1} : nombre de colonnes insuffisant (${cols.length})`)
      continue
    }

    const get = (col: string) => {
      const idx = colIndex[col]
      return idx >= 0 && idx < cols.length ? cols[idx].trim() : ""
    }

    ecritures.push({
      journalCode: get("JournalCode"),
      journalLib: get("JournalLib"),
      ecritureNum: get("EcritureNum"),
      ecritureDate: parseFECDate(get("EcritureDate")),
      compteNum: get("CompteNum"),
      compteLib: get("CompteLib"),
      compAuxNum: get("CompAuxNum"),
      compAuxLib: get("CompAuxLib"),
      pieceRef: get("PieceRef"),
      pieceDate: parseFECDate(get("PieceDate")),
      ecritureLib: get("EcritureLib"),
      debit: parseFECAmount(get("Debit")),
      credit: parseFECAmount(get("Credit")),
      ecritureLet: get("EcritureLet"),
      dateLet: parseFECDate(get("DateLet")),
      validDate: parseFECDate(get("ValidDate")),
      montantDevise: parseFECAmount(get("Montantdevise")),
      iDevise: get("Idevise"),
    })
  }

  // Construire les analyses
  const cr = buildCompteResultat(ecritures)
  const kpis = buildKPIs(ecritures, cr)
  const balanceClients = buildBalanceAgee(ecritures, "411")
  const balanceFournisseurs = buildBalanceAgee(ecritures, "401")
  const flux = buildFluxTresorerie(ecritures, cr)
  const forecasts = buildForecasts(ecritures, kpis)
  const operations = buildOperations(ecritures)
  const mouvementsBanque = buildMouvementsBanque(ecritures)
  const echeances = buildEcheances(ecritures)

  return {
    ecritures,
    compteResultat: cr,
    kpis,
    balanceClients,
    balanceFournisseurs,
    fluxTresorerie: flux,
    forecasts,
    operations,
    mouvementsBanque,
    echeances,
    nbLignes: ecritures.length,
    nbErreurs,
    erreurs,
  }
}

// ── Compte de résultat ──

function buildCompteResultat(ecritures: EcritureFEC[]): CompteResultat {
  let chiffre_affaires = 0
  let achats = 0
  let charges_externes = 0
  let charges_personnel = 0
  let impots_taxes = 0
  let dotations = 0
  let produits_financiers = 0
  let charges_financieres = 0
  let produits_exceptionnels = 0
  let charges_exceptionnelles = 0
  let impot_benefice = 0
  let autres_produits = 0

  for (const e of ecritures) {
    const c = e.compteNum
    if (!c) continue

    const prefix2 = c.slice(0, 2)

    // Classe 7 : Produits (crédit - débit)
    if (c.startsWith("70")) chiffre_affaires += (e.credit - e.debit)
    else if (c.startsWith("71") || c.startsWith("72")) autres_produits += (e.credit - e.debit)
    else if (prefix2 === "74" || prefix2 === "75") autres_produits += (e.credit - e.debit)
    else if (c.startsWith("76")) produits_financiers += (e.credit - e.debit)
    else if (c.startsWith("77")) produits_exceptionnels += (e.credit - e.debit)
    else if (c.startsWith("78")) dotations -= (e.credit - e.debit) // Reprises

    // Classe 6 : Charges (débit - crédit)
    else if (prefix2 === "60") achats += (e.debit - e.credit)
    else if (prefix2 === "61" || prefix2 === "62") charges_externes += (e.debit - e.credit)
    else if (prefix2 === "63") impots_taxes += (e.debit - e.credit)
    else if (prefix2 === "64") charges_personnel += (e.debit - e.credit)
    else if (prefix2 === "65") charges_externes += (e.debit - e.credit)
    else if (prefix2 === "66") charges_financieres += (e.debit - e.credit)
    else if (prefix2 === "67") charges_exceptionnelles += (e.debit - e.credit)
    else if (prefix2 === "68") dotations += (e.debit - e.credit)
    else if (prefix2 === "69") impot_benefice += (e.debit - e.credit)
  }

  const marge_brute = chiffre_affaires - achats
  const valeur_ajoutee = marge_brute - charges_externes + autres_produits
  const ebe = valeur_ajoutee - impots_taxes - charges_personnel
  const resultat_exploitation = ebe - dotations
  const resultat_financier = produits_financiers - charges_financieres
  const resultat_net = resultat_exploitation + resultat_financier
    + produits_exceptionnels - charges_exceptionnelles - impot_benefice
  const caf = resultat_net + dotations

  return {
    chiffre_affaires,
    achats,
    charges_externes,
    charges_personnel,
    impots_taxes,
    dotations,
    resultat_exploitation,
    resultat_financier,
    resultat_net,
    marge_brute,
    valeur_ajoutee,
    ebe,
    caf,
  }
}

// ── KPIs ──

function buildKPIs(ecritures: EcritureFEC[], cr: CompteResultat): KPIs {
  // Créances clients = solde débiteur des comptes 411
  let creances = 0
  let dettes = 0
  let tresorerie = 0

  // Regrouper par pièce+compte pour calculer les soldes ouverts
  const soldesClients = new Map<string, number>()
  const soldesFournisseurs = new Map<string, number>()

  for (const e of ecritures) {
    const c = e.compteNum
    if (c.startsWith("411")) {
      const key = `${e.compAuxNum || c}-${e.pieceRef}`
      soldesClients.set(key, (soldesClients.get(key) || 0) + e.debit - e.credit)
    } else if (c.startsWith("401")) {
      const key = `${e.compAuxNum || c}-${e.pieceRef}`
      soldesFournisseurs.set(key, (soldesFournisseurs.get(key) || 0) + e.debit - e.credit)
    } else if (c.startsWith("5")) {
      tresorerie += (e.debit - e.credit)
    }
  }

  // Créances = somme des soldes débiteurs positifs (non lettrés)
  for (const [, solde] of soldesClients) {
    if (solde > 0) creances += solde
  }
  // Dettes = somme des soldes créditeurs (négatifs = dette)
  for (const [, solde] of soldesFournisseurs) {
    if (solde < 0) dettes += Math.abs(solde)
  }

  const bfr = creances - dettes
  const ca = Math.max(cr.chiffre_affaires, 1)
  const dso = Math.round((creances / ca) * 365)
  const dpo = cr.achats > 0 ? Math.round((dettes / cr.achats) * 365) : 0
  const taux_marge = Math.round((cr.marge_brute / ca) * 1000) / 10
  const taux_ebe = Math.round((cr.ebe / ca) * 1000) / 10

  return {
    chiffre_affaires: cr.chiffre_affaires,
    marge_brute: cr.marge_brute,
    taux_marge_brute: taux_marge,
    valeur_ajoutee: cr.valeur_ajoutee,
    ebe: cr.ebe,
    taux_ebe: taux_ebe,
    resultat_net: cr.resultat_net,
    caf: cr.caf,
    bfr,
    creances_clients: creances,
    dettes_fournisseurs: dettes,
    dso_jours: dso,
    dpo_jours: dpo,
    tresorerie_nette: tresorerie,
  }
}

// ── Balance âgée ──

function buildBalanceAgee(ecritures: EcritureFEC[], prefixCompte: string): BalanceAgeeLine[] {
  const today = new Date()
  const todayStr = today.toISOString().slice(0, 10)

  // Regrouper par tiers (CompAuxNum)
  const parTiers = new Map<string, {
    code: string
    nom: string
    pieces: Map<string, { debit: number; credit: number; date: string; lettre: boolean }>
  }>()

  for (const e of ecritures) {
    if (!e.compteNum.startsWith(prefixCompte)) continue

    const code = e.compAuxNum || e.compteNum
    const nom = e.compAuxLib || e.compteLib || code

    if (!parTiers.has(code)) {
      parTiers.set(code, { code, nom, pieces: new Map() })
    }

    const tiers = parTiers.get(code)!
    const pieceKey = e.pieceRef
    if (!tiers.pieces.has(pieceKey)) {
      tiers.pieces.set(pieceKey, { debit: 0, credit: 0, date: e.pieceDate || e.ecritureDate, lettre: false })
    }
    const piece = tiers.pieces.get(pieceKey)!
    piece.debit += e.debit
    piece.credit += e.credit
    if (e.ecritureLet) piece.lettre = true
  }

  const result: BalanceAgeeLine[] = []

  for (const [, tiers] of parTiers) {
    const ligne: BalanceAgeeLine = {
      code: tiers.code,
      nom: tiers.nom.slice(0, 40),
      total: 0,
      non_echu: 0,
      echu_0_30: 0,
      echu_30_60: 0,
      echu_60_90: 0,
      echu_plus_90: 0,
    }

    for (const [, piece] of tiers.pieces) {
      if (piece.lettre) continue // Lettré = soldé

      // Solde de la pièce
      let solde: number
      if (prefixCompte === "411") {
        solde = piece.debit - piece.credit // Créance client (débiteur)
      } else {
        solde = piece.credit - piece.debit // Dette fournisseur (créditeur)
      }

      if (solde <= 0) continue // Pas de solde ouvert

      ligne.total += solde

      // Ancienneté
      const pieceDate = piece.date || todayStr
      const diff = Math.floor((today.getTime() - new Date(pieceDate).getTime()) / 86400000)

      if (diff <= 0) ligne.non_echu += solde
      else if (diff <= 30) ligne.echu_0_30 += solde
      else if (diff <= 60) ligne.echu_30_60 += solde
      else if (diff <= 90) ligne.echu_60_90 += solde
      else ligne.echu_plus_90 += solde
    }

    if (ligne.total > 0) result.push(ligne)
  }

  return result.sort((a, b) => b.total - a.total)
}

// ── Flux de trésorerie ──

function buildFluxTresorerie(ecritures: EcritureFEC[], cr: CompteResultat): FluxTresorerie {
  let variation_stocks = 0
  let variation_creances = 0
  let variation_dettes = 0
  let acquisitions_immo = 0
  let cessions_immo = 0
  let emprunts_nouveaux = 0
  let remboursements_emprunts = 0
  let apports_capital = 0

  for (const e of ecritures) {
    const c = e.compteNum
    const mouvement = e.debit - e.credit

    if (c.startsWith("3")) variation_stocks += mouvement
    else if (c.startsWith("41")) variation_creances += mouvement
    else if (c.startsWith("40")) variation_dettes -= mouvement
    else if (c.startsWith("2") && !c.startsWith("28")) {
      if (mouvement > 0) acquisitions_immo += mouvement
      else cessions_immo += Math.abs(mouvement)
    } else if (c.startsWith("16")) {
      if (mouvement < 0) emprunts_nouveaux += Math.abs(mouvement)
      else remboursements_emprunts += mouvement
    } else if (c.startsWith("10")) {
      apports_capital -= mouvement
    }
  }

  const flux_exploitation = cr.resultat_net + cr.dotations
    - variation_stocks - variation_creances + variation_dettes
  const flux_investissement = cessions_immo - acquisitions_immo
  const flux_financement = emprunts_nouveaux - remboursements_emprunts + apports_capital

  return {
    flux_exploitation,
    flux_investissement,
    flux_financement,
    variation_tresorerie: flux_exploitation + flux_investissement + flux_financement,
    resultat_net: cr.resultat_net,
    dotations: cr.dotations,
    variation_bfr: variation_creances - variation_dettes + variation_stocks,
  }
}

// ── Prévisionnel (projection sur 12 mois depuis les données FEC) ──

function buildForecasts(ecritures: EcritureFEC[], kpis: KPIs): Record<string, MonthForecast[]> {
  // Calculer le CA mensuel moyen depuis les écritures
  const caMensuel = new Map<string, number>()
  const decMensuel = new Map<string, number>()

  for (const e of ecritures) {
    if (!e.ecritureDate) continue
    const mois = e.ecritureDate.slice(0, 7) // YYYY-MM
    const c = e.compteNum

    if (c.startsWith("70")) {
      caMensuel.set(mois, (caMensuel.get(mois) || 0) + (e.credit - e.debit))
    }
    if (c.startsWith("40") || c.startsWith("6")) {
      decMensuel.set(mois, (decMensuel.get(mois) || 0) + (e.debit - e.credit))
    }
  }

  // Moyenne mensuelle
  const moisCA = [...caMensuel.values()]
  const moisDec = [...decMensuel.values()]
  const avgCA = moisCA.length > 0 ? Math.round(moisCA.reduce((a, b) => a + b, 0) / moisCA.length) : 0
  const avgDec = moisDec.length > 0 ? Math.round(moisDec.reduce((a, b) => a + b, 0) / moisDec.length) : 0

  const tresoInitiale = kpis.tresorerie_nette || 0

  // Générer 12 mois pour chaque scénario
  const now = new Date()
  const startMonth = new Date(now.getFullYear(), now.getMonth() + 1, 1)

  function generateScenario(
    encMultiplier: number,
    decMultiplier: number,
    delayDays: number,
  ): MonthForecast[] {
    const months: MonthForecast[] = []
    let treso = tresoInitiale

    for (let i = 0; i < 12; i++) {
      const m = new Date(startMonth.getFullYear(), startMonth.getMonth() + i, 1)
      const moisStr = m.toISOString().slice(0, 7)

      // Variation saisonnière simple
      const monthIdx = m.getMonth()
      const seasonality = [0.85, 0.90, 1.0, 1.05, 1.1, 1.0, 0.8, 0.7, 0.95, 1.1, 1.15, 1.2]
      const factor = seasonality[monthIdx]

      const enc = Math.round(avgCA * encMultiplier * factor)
      const dec = Math.round(avgDec * decMultiplier * factor * 0.95)
      const solde = enc - dec
      const tresoFin = treso + solde

      months.push({
        mois: moisStr,
        tresorerie_debut: treso,
        encaissements: enc,
        decaissements: dec,
        solde,
        tresorerie_fin: tresoFin,
      })
      treso = tresoFin
    }
    return months
  }

  return {
    prudent: generateScenario(0.85, 1.05, 15),
    central: generateScenario(1.0, 1.0, 0),
    ambitieux: generateScenario(1.15, 0.95, -5),
  }
}

// ── Classification comptable de chaque écriture ──

function classifyCompte(compteNum: string): { categorie: OperationComptable["categorie"]; sousCategorie: string } {
  const c = compteNum
  // Classe 1 : Capitaux
  if (c.startsWith("10")) return { categorie: "bilan", sousCategorie: "capital" }
  if (c.startsWith("16")) return { categorie: "bilan", sousCategorie: "emprunt" }
  if (c.startsWith("1")) return { categorie: "bilan", sousCategorie: "capitaux" }
  // Classe 2 : Immobilisations
  if (c.startsWith("2")) return { categorie: "bilan", sousCategorie: "immobilisation" }
  // Classe 3 : Stocks
  if (c.startsWith("3")) return { categorie: "bilan", sousCategorie: "stock" }
  // Classe 4 : Tiers
  if (c.startsWith("411")) return { categorie: "client", sousCategorie: "créance client" }
  if (c.startsWith("401")) return { categorie: "fournisseur", sousCategorie: "dette fournisseur" }
  if (c.startsWith("421")) return { categorie: "bilan", sousCategorie: "personnel" }
  if (c.startsWith("43")) return { categorie: "bilan", sousCategorie: "charges sociales" }
  if (c.startsWith("44")) return { categorie: "bilan", sousCategorie: "état / TVA" }
  if (c.startsWith("4")) return { categorie: "bilan", sousCategorie: "tiers divers" }
  // Classe 5 : Trésorerie
  if (c.startsWith("512")) return { categorie: "banque", sousCategorie: "banque" }
  if (c.startsWith("53")) return { categorie: "tresorerie", sousCategorie: "caisse" }
  if (c.startsWith("5")) return { categorie: "tresorerie", sousCategorie: "trésorerie" }
  // Classe 6 : Charges
  if (c.startsWith("60")) return { categorie: "charge", sousCategorie: "achats" }
  if (c.startsWith("61") || c.startsWith("62")) return { categorie: "charge", sousCategorie: "charges externes" }
  if (c.startsWith("63")) return { categorie: "charge", sousCategorie: "impôts et taxes" }
  if (c.startsWith("641")) return { categorie: "charge", sousCategorie: "salaires" }
  if (c.startsWith("645")) return { categorie: "charge", sousCategorie: "charges sociales" }
  if (c.startsWith("64")) return { categorie: "charge", sousCategorie: "personnel" }
  if (c.startsWith("66")) return { categorie: "charge", sousCategorie: "charges financières" }
  if (c.startsWith("68")) return { categorie: "charge", sousCategorie: "dotations" }
  if (c.startsWith("6")) return { categorie: "charge", sousCategorie: "autres charges" }
  // Classe 7 : Produits
  if (c.startsWith("70")) return { categorie: "produit", sousCategorie: "ventes" }
  if (c.startsWith("74")) return { categorie: "produit", sousCategorie: "subventions" }
  if (c.startsWith("76")) return { categorie: "produit", sousCategorie: "produits financiers" }
  if (c.startsWith("77")) return { categorie: "produit", sousCategorie: "produits exceptionnels" }
  if (c.startsWith("7")) return { categorie: "produit", sousCategorie: "autres produits" }

  return { categorie: "autre", sousCategorie: "non classé" }
}

function buildOperations(ecritures: EcritureFEC[]): OperationComptable[] {
  return ecritures.map((e) => {
    const { categorie, sousCategorie } = classifyCompte(e.compteNum)
    return {
      date: e.ecritureDate,
      pieceRef: e.pieceRef,
      journal: `${e.journalCode} - ${e.journalLib}`,
      libelle: e.ecritureLib,
      compteNum: e.compteNum,
      compteLib: e.compteLib,
      tiers: e.compAuxNum,
      tiersNom: e.compAuxLib || e.compteLib,
      debit: e.debit,
      credit: e.credit,
      solde: e.debit - e.credit,
      lettrage: e.ecritureLet,
      categorie,
      sousCategorie,
    }
  })
}

// ── Mouvements bancaires (compte 512) ──

function buildMouvementsBanque(ecritures: EcritureFEC[]): MouvementBanque[] {
  // Filtrer les écritures sur comptes 512 (banque)
  const bankEntries = ecritures
    .filter((e) => e.compteNum.startsWith("512"))
    .sort((a, b) => a.ecritureDate.localeCompare(b.ecritureDate))

  let solde = 0
  return bankEntries.map((e) => {
    const enc = e.debit  // Débit sur 512 = entrée d'argent (encaissement)
    const dec = e.credit // Crédit sur 512 = sortie d'argent (décaissement)
    solde += enc - dec
    return {
      date: e.ecritureDate,
      libelle: e.ecritureLib,
      pieceRef: e.pieceRef,
      tiers: e.compAuxLib || e.compAuxNum || "",
      encaissement: enc,
      decaissement: dec,
      solde_cumule: solde,
    }
  })
}

// ── Échéances clients / fournisseurs ──

function buildEcheances(ecritures: EcritureFEC[]): Echeance[] {
  // Regrouper par pièce et tiers pour les comptes 411 et 401
  const pieces = new Map<string, {
    tiers: string
    tiersNom: string
    pieceRef: string
    dateFacture: string
    debit: number
    credit: number
    type: "client" | "fournisseur"
    lettrage: boolean
  }>()

  for (const e of ecritures) {
    const c = e.compteNum
    let type: "client" | "fournisseur" | null = null
    if (c.startsWith("411")) type = "client"
    else if (c.startsWith("401")) type = "fournisseur"
    if (!type) continue

    const key = `${type}-${e.compAuxNum || c}-${e.pieceRef}`
    if (!pieces.has(key)) {
      pieces.set(key, {
        tiers: e.compAuxNum || c,
        tiersNom: e.compAuxLib || e.compteLib,
        pieceRef: e.pieceRef,
        dateFacture: e.pieceDate || e.ecritureDate,
        debit: 0,
        credit: 0,
        type,
        lettrage: false,
      })
    }
    const p = pieces.get(key)!
    p.debit += e.debit
    p.credit += e.credit
    if (e.ecritureLet) p.lettrage = true
  }

  const echeances: Echeance[] = []

  for (const [, p] of pieces) {
    // Calculer le solde ouvert
    let montant: number
    if (p.type === "client") {
      montant = p.debit - p.credit // Débiteur = créance
    } else {
      montant = p.credit - p.debit // Créditeur = dette
    }

    if (montant <= 0) continue // Soldé ou lettré
    if (p.lettrage) continue    // Lettré = payé

    // Estimer la date d'échéance : date facture + 30 jours (par défaut)
    let dateEcheance = p.dateFacture
    if (p.dateFacture) {
      const d = new Date(p.dateFacture)
      d.setDate(d.getDate() + 30) // Hypothèse 30 jours net
      dateEcheance = d.toISOString().slice(0, 10)
    }

    echeances.push({
      tiers: p.tiers,
      tiersNom: p.tiersNom.slice(0, 40),
      pieceRef: p.pieceRef,
      dateFacture: p.dateFacture,
      dateEcheance,
      montant,
      type: p.type,
      statut: "ouvert",
    })
  }

  return echeances.sort((a, b) => a.dateEcheance.localeCompare(b.dateEcheance))
}

function emptyFECData(erreurs: string[]): FECData {
  return {
    ecritures: [],
    compteResultat: {
      chiffre_affaires: 0, achats: 0, charges_externes: 0, charges_personnel: 0,
      impots_taxes: 0, dotations: 0, resultat_exploitation: 0, resultat_financier: 0,
      resultat_net: 0, marge_brute: 0, valeur_ajoutee: 0, ebe: 0, caf: 0,
    },
    kpis: {
      chiffre_affaires: 0, marge_brute: 0, taux_marge_brute: 0, valeur_ajoutee: 0,
      ebe: 0, taux_ebe: 0, resultat_net: 0, caf: 0, bfr: 0,
      creances_clients: 0, dettes_fournisseurs: 0, dso_jours: 0, dpo_jours: 0,
      tresorerie_nette: 0,
    },
    balanceClients: [],
    balanceFournisseurs: [],
    fluxTresorerie: {
      flux_exploitation: 0, flux_investissement: 0, flux_financement: 0,
      variation_tresorerie: 0, resultat_net: 0, dotations: 0, variation_bfr: 0,
    },
    forecasts: { prudent: [], central: [], ambitieux: [] },
    operations: [],
    mouvementsBanque: [],
    echeances: [],
    nbLignes: 0,
    nbErreurs: erreurs.length,
    erreurs,
  }
}
