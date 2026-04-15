/**
 * Moteur de prévisionnel de trésorerie à 3 blocs.
 *
 * Bloc 1 — AUTOMATIQUE (données comptables FEC)
 *   Solde bancaire initial (512)
 *   Encaissements sur factures émises (balance âgée clients 411)
 *   Décaissements sur factures reçues (balance âgée fournisseurs 401)
 *   Charges récurrentes détectées (loyers, abonnements, etc.)
 *   Paie récurrente (641/645/43x)
 *   TVA / fiscal récurrent (44x)
 *   Emprunts (16x)
 *
 * Bloc 2 — SEMI-AUTOMATIQUE (règles)
 *   Délai moyen réel de paiement par client
 *   Délai moyen réel de paiement par fournisseur
 *   Charges variables lissées (moyenne glissante)
 *   Saisonnalité détectée
 *
 * Bloc 3 — MANUEL (prévisions métier)
 *   Chantiers / situations à facturer
 *   Gros achats futurs / investissements
 *   Primes / variations paie
 *   Flux exceptionnels
 */

import type { EcritureFEC } from "./fec-parser"
import type { MonthForecast, Echeance } from "./types"

// ── Types ──

export interface ForecastLine {
  mois: string          // YYYY-MM
  libelle: string
  montant: number       // positif=encaissement, négatif=décaissement
  source: "auto" | "regle" | "manuel"
  categorie: string     // "client", "fournisseur", "paie", "fiscal", "emprunt", "charge_fixe", "metier"
  tiers?: string
  detail?: string
}

export interface RecurringCharge {
  libelle: string
  montant: number       // montant moyen mensuel (négatif)
  frequence: "mensuel" | "trimestriel" | "annuel"
  jourHabituel: number  // jour du mois de prélèvement
  compteNum: string
  occurrences: number   // nombre de fois détecté
}

export interface DelaiPaiement {
  tiers: string
  tiersNom: string
  type: "client" | "fournisseur"
  delaiMoyenJours: number
  nbFactures: number
  montantTotal: number
}

export interface ForecastResult {
  lines: ForecastLine[]
  byMonth: MonthForecast[]
  totalAuto: number
  totalRegle: number
  totalManuel: number
  recurring: RecurringCharge[]
  delais: DelaiPaiement[]
}

// ── Bloc 1 : Automatique (comptable) ──

function buildBloc1(
  ecritures: EcritureFEC[],
  echeances: Echeance[],
  startMonth: string,
  months: number,
): ForecastLine[] {
  const lines: ForecastLine[] = []

  // 1. Encaissements sur créances clients ouvertes (411)
  for (const ech of echeances) {
    if (ech.type !== "client" || ech.statut !== "ouvert") continue
    const mois = ech.dateEcheance.slice(0, 7)
    if (mois >= startMonth) {
      lines.push({
        mois,
        libelle: `Encaissement ${ech.tiersNom} - ${ech.pieceRef}`,
        montant: ech.montant,
        source: "auto",
        categorie: "client",
        tiers: ech.tiers,
        detail: `Facture ${ech.pieceRef} du ${ech.dateFacture}`,
      })
    }
  }

  // 2. Décaissements sur dettes fournisseurs ouvertes (401)
  for (const ech of echeances) {
    if (ech.type !== "fournisseur" || ech.statut !== "ouvert") continue
    const mois = ech.dateEcheance.slice(0, 7)
    if (mois >= startMonth) {
      lines.push({
        mois,
        libelle: `Paiement ${ech.tiersNom} - ${ech.pieceRef}`,
        montant: -ech.montant,
        source: "auto",
        categorie: "fournisseur",
        tiers: ech.tiers,
        detail: `Facture ${ech.pieceRef} du ${ech.dateFacture}`,
      })
    }
  }

  // 3. Emprunts récurrents (16x → 512)
  const emprunts = detectRecurring(ecritures, "16", "debit")
  for (const emp of emprunts) {
    for (let i = 0; i < months; i++) {
      const m = addMonths(startMonth, i)
      lines.push({
        mois: m,
        libelle: `Remboursement emprunt : ${emp.libelle}`,
        montant: -emp.montant,
        source: "auto",
        categorie: "emprunt",
        detail: `Compte ${emp.compteNum}, ~${emp.jourHabituel} du mois`,
      })
    }
  }

  return lines
}

// ── Bloc 2 : Semi-automatique (règles) ──

function buildBloc2(
  ecritures: EcritureFEC[],
  startMonth: string,
  months: number,
): { lines: ForecastLine[]; recurring: RecurringCharge[]; delais: DelaiPaiement[] } {
  const lines: ForecastLine[] = []

  // 1. Charges fixes récurrentes détectées depuis l'historique banque (512)
  const recurring = detectRecurringFromBank(ecritures)

  for (const charge of recurring) {
    const step = charge.frequence === "trimestriel" ? 3 : charge.frequence === "annuel" ? 12 : 1
    for (let i = 0; i < months; i += step) {
      const m = addMonths(startMonth, i)
      lines.push({
        mois: m,
        libelle: charge.libelle,
        montant: -Math.abs(charge.montant),
        source: "regle",
        categorie: "charge_fixe",
        detail: `Récurrent ${charge.frequence}, ~${charge.jourHabituel} du mois (${charge.occurrences} occurrences détectées)`,
      })
    }
  }

  // 2. Paie récurrente (comptes 421 : salaires nets payés via banque)
  const paie = detectRecurring(ecritures, "421", "credit")
  for (const p of paie) {
    for (let i = 0; i < months; i++) {
      const m = addMonths(startMonth, i)
      lines.push({
        mois: m,
        libelle: `Paie : ${p.libelle}`,
        montant: -p.montant,
        source: "regle",
        categorie: "paie",
        detail: `Compte ${p.compteNum}, moyenne sur ${p.occurrences} mois`,
      })
    }
  }

  // 3. Charges sociales récurrentes (43x)
  const sociales = detectRecurring(ecritures, "43", "debit")
  for (const cs of sociales) {
    for (let i = 0; i < months; i++) {
      const m = addMonths(startMonth, i)
      lines.push({
        mois: m,
        libelle: `Charges sociales : ${cs.libelle}`,
        montant: -cs.montant,
        source: "regle",
        categorie: "paie",
        detail: `Compte ${cs.compteNum}`,
      })
    }
  }

  // 4. TVA récurrente (4457x collectée - 4456x déductible)
  const tvaCollectee = monthlyAverage(ecritures, "4457", "credit")
  const tvaDeductible = monthlyAverage(ecritures, "4456", "debit")
  const tvaNette = tvaCollectee - tvaDeductible
  if (tvaNette > 0) {
    for (let i = 0; i < months; i++) {
      const m = addMonths(startMonth, i)
      lines.push({
        mois: m,
        libelle: "TVA nette à payer (estimée)",
        montant: -tvaNette,
        source: "regle",
        categorie: "fiscal",
        detail: `Collectée ~${Math.round(tvaCollectee)} - Déductible ~${Math.round(tvaDeductible)}`,
      })
    }
  }

  // 5. Délais réels de paiement par tiers
  const delais = computeDelaisPaiement(ecritures)

  return { lines, recurring, delais }
}

// ── Détection de charges récurrentes depuis le grand livre banque ──

function detectRecurringFromBank(ecritures: EcritureFEC[]): RecurringCharge[] {
  // Chercher les crédits récurrents sur 512 (= sorties de banque)
  const bankCredits = ecritures.filter(
    (e) => e.compteNum.startsWith("512") && e.credit > 0
  )

  // Grouper par libellé normalisé et montant arrondi
  const groups = new Map<string, { montants: number[]; jours: number[]; compteNum: string; libelle: string }>()

  for (const e of bankCredits) {
    const key = normalizeLibelle(e.ecritureLib)
    if (!key) continue

    if (!groups.has(key)) {
      groups.set(key, { montants: [], jours: [], compteNum: e.compteNum, libelle: e.ecritureLib })
    }
    const g = groups.get(key)!
    g.montants.push(e.credit)
    const jour = e.ecritureDate ? parseInt(e.ecritureDate.slice(8, 10)) : 15
    g.jours.push(jour)
  }

  const recurring: RecurringCharge[] = []
  for (const [, g] of groups) {
    if (g.montants.length < 2) continue // Au moins 2 occurrences

    // Vérifier que les montants sont similaires (±20%)
    const avg = g.montants.reduce((a, b) => a + b, 0) / g.montants.length
    const allSimilar = g.montants.every((m) => Math.abs(m - avg) / avg < 0.20)
    if (!allSimilar) continue

    const avgJour = Math.round(g.jours.reduce((a, b) => a + b, 0) / g.jours.length)
    const frequence = g.montants.length >= 10 ? "mensuel" : g.montants.length >= 3 ? "trimestriel" : "annuel"

    recurring.push({
      libelle: g.libelle.slice(0, 50),
      montant: Math.round(avg),
      frequence,
      jourHabituel: avgJour,
      compteNum: g.compteNum,
      occurrences: g.montants.length,
    })
  }

  return recurring.sort((a, b) => b.montant - a.montant)
}

// ── Détection pattern récurrent par préfixe de compte ──

function detectRecurring(
  ecritures: EcritureFEC[],
  prefix: string,
  side: "debit" | "credit",
): RecurringCharge[] {
  const monthlyTotals = new Map<string, number>()

  for (const e of ecritures) {
    if (!e.compteNum.startsWith(prefix)) continue
    const mois = e.ecritureDate?.slice(0, 7)
    if (!mois) continue
    const amount = side === "debit" ? e.debit : e.credit
    if (amount <= 0) continue
    monthlyTotals.set(mois, (monthlyTotals.get(mois) || 0) + amount)
  }

  const values = [...monthlyTotals.values()]
  if (values.length < 2) return []

  const avg = Math.round(values.reduce((a, b) => a + b, 0) / values.length)
  if (avg <= 0) return []

  return [{
    libelle: `Compte ${prefix}xxx`,
    montant: avg,
    frequence: "mensuel",
    jourHabituel: 15,
    compteNum: prefix,
    occurrences: values.length,
  }]
}

// ── Calcul des délais réels de paiement ──

function computeDelaisPaiement(ecritures: EcritureFEC[]): DelaiPaiement[] {
  // Pour chaque tiers (411/401), comparer date facture vs date lettrage
  const tiers = new Map<string, {
    type: "client" | "fournisseur"
    nom: string
    delais: number[]
    montantTotal: number
  }>()

  for (const e of ecritures) {
    const isClient = e.compteNum.startsWith("411")
    const isFournisseur = e.compteNum.startsWith("401")
    if (!isClient && !isFournisseur) continue
    if (!e.ecritureLet || !e.dateLet || !e.pieceDate) continue

    const code = e.compAuxNum || e.compteNum
    const type = isClient ? "client" : "fournisseur"

    if (!tiers.has(code)) {
      tiers.set(code, { type, nom: e.compAuxLib || e.compteLib, delais: [], montantTotal: 0 })
    }

    const t = tiers.get(code)!
    const dateFacture = new Date(e.pieceDate)
    const datePaiement = new Date(e.dateLet)
    const delai = Math.floor((datePaiement.getTime() - dateFacture.getTime()) / 86400000)

    if (delai > 0 && delai < 365) {
      t.delais.push(delai)
      t.montantTotal += Math.abs(e.debit - e.credit)
    }
  }

  const result: DelaiPaiement[] = []
  for (const [code, t] of tiers) {
    if (t.delais.length === 0) continue
    const avg = Math.round(t.delais.reduce((a, b) => a + b, 0) / t.delais.length)
    result.push({
      tiers: code,
      tiersNom: t.nom.slice(0, 40),
      type: t.type,
      delaiMoyenJours: avg,
      nbFactures: t.delais.length,
      montantTotal: t.montantTotal,
    })
  }

  return result.sort((a, b) => b.montantTotal - a.montantTotal)
}

// ── Moyenne mensuelle par préfixe de compte ──

function monthlyAverage(ecritures: EcritureFEC[], prefix: string, side: "debit" | "credit"): number {
  const monthlyTotals = new Map<string, number>()
  for (const e of ecritures) {
    if (!e.compteNum.startsWith(prefix)) continue
    const mois = e.ecritureDate?.slice(0, 7)
    if (!mois) continue
    const amount = side === "debit" ? e.debit : e.credit
    if (amount > 0) monthlyTotals.set(mois, (monthlyTotals.get(mois) || 0) + amount)
  }
  const values = [...monthlyTotals.values()]
  return values.length > 0 ? Math.round(values.reduce((a, b) => a + b, 0) / values.length) : 0
}

// ── Agrégation finale ──

export function buildForecast(
  ecritures: EcritureFEC[],
  echeances: Echeance[],
  manualLines: ForecastLine[],
  tresorerieInitiale: number,
  months: number = 12,
): ForecastResult {
  const now = new Date()
  const startMonth = `${now.getFullYear()}-${String(now.getMonth() + 2).padStart(2, "0")}`

  const bloc1 = buildBloc1(ecritures, echeances, startMonth, months)
  const { lines: bloc2, recurring, delais } = buildBloc2(ecritures, startMonth, months)
  const bloc3 = manualLines.filter((l) => l.mois >= startMonth)

  const allLines = [...bloc1, ...bloc2, ...bloc3]

  // Agréger par mois
  const byMonthMap = new Map<string, { enc: number; dec: number; lines: ForecastLine[] }>()
  for (let i = 0; i < months; i++) {
    const m = addMonths(startMonth, i)
    byMonthMap.set(m, { enc: 0, dec: 0, lines: [] })
  }

  for (const line of allLines) {
    const entry = byMonthMap.get(line.mois)
    if (!entry) continue
    entry.lines.push(line)
    if (line.montant >= 0) entry.enc += line.montant
    else entry.dec += Math.abs(line.montant)
  }

  // Construire le rolling cash
  const byMonth: MonthForecast[] = []
  let treso = tresorerieInitiale

  const sortedMonths = [...byMonthMap.keys()].sort()
  for (const m of sortedMonths) {
    const entry = byMonthMap.get(m)!
    const solde = entry.enc - entry.dec
    const tresoFin = treso + solde

    byMonth.push({
      mois: m,
      tresorerie_debut: treso,
      encaissements: entry.enc,
      decaissements: entry.dec,
      solde,
      tresorerie_fin: tresoFin,
    })
    treso = tresoFin
  }

  const totalAuto = allLines.filter((l) => l.source === "auto").reduce((s, l) => s + l.montant, 0)
  const totalRegle = allLines.filter((l) => l.source === "regle").reduce((s, l) => s + l.montant, 0)
  const totalManuel = allLines.filter((l) => l.source === "manuel").reduce((s, l) => s + l.montant, 0)

  return { lines: allLines, byMonth, totalAuto, totalRegle, totalManuel, recurring, delais }
}

// ── Utilitaires ──

function addMonths(yyyymm: string, n: number): string {
  const [y, m] = yyyymm.split("-").map(Number)
  const d = new Date(y, m - 1 + n, 1)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`
}

function normalizeLibelle(lib: string): string {
  return lib.toLowerCase()
    .replace(/\d{2}\/\d{2}\/\d{4}/g, "")  // Retirer les dates
    .replace(/\d{4,}/g, "")                 // Retirer les longs numéros
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 30)
}
