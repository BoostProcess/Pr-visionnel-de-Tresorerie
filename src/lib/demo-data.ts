import type { MonthForecast, KPIs, CompteResultat, BalanceAgeeLine, FluxTresorerie } from "./types"

// Mois réalisés (historique comptable) — identiques pour les 3 scénarios
const moisRealises: MonthForecast[] = [
  { mois: "2026-01", tresorerie_debut: 4200000, encaissements: 2876500, decaissements: 2654300, solde: 222200, tresorerie_fin: 4422200, type: "realise" },
  { mois: "2026-02", tresorerie_debut: 4422200, encaissements: 3145800, decaissements: 2987600, solde: 158200, tresorerie_fin: 4580400, type: "realise" },
  { mois: "2026-03", tresorerie_debut: 4580400, encaissements: 3428700, decaissements: 3156400, solde: 272300, tresorerie_fin: 4852700, type: "realise" },
  { mois: "2026-04", tresorerie_debut: 4852700, encaissements: 3067200, decaissements: 2919900, solde: 147300, tresorerie_fin: 5000000, type: "realise" },
]

export const demoForecasts: Record<string, MonthForecast[]> = {
  prudent: [
    ...moisRealises,
    { mois: "2026-05", tresorerie_debut: 5000000, encaissements: 2843200, decaissements: 3218500, solde: -375300, tresorerie_fin: 4624700, type: "previsionnel" },
    { mois: "2026-06", tresorerie_debut: 4624700, encaissements: 3067400, decaissements: 3341800, solde: -274400, tresorerie_fin: 4350300 , type: "previsionnel" },
    { mois: "2026-07", tresorerie_debut: 4350300, encaissements: 2478600, decaissements: 3156200, solde: -677600, tresorerie_fin: 3672700 , type: "previsionnel" },
    { mois: "2026-08", tresorerie_debut: 3672700, encaissements: 1763500, decaissements: 2937800, solde: -1174300, tresorerie_fin: 2498400 , type: "previsionnel" },
    { mois: "2026-09", tresorerie_debut: 2498400, encaissements: 2215700, decaissements: 3187600, solde: -971900, tresorerie_fin: 1526500 , type: "previsionnel" },
    { mois: "2026-10", tresorerie_debut: 1526500, encaissements: 3487300, decaissements: 3092400, solde: 394900, tresorerie_fin: 1921400 , type: "previsionnel" },
    { mois: "2026-11", tresorerie_debut: 1921400, encaissements: 3812600, decaissements: 3243700, solde: 568900, tresorerie_fin: 2490300 , type: "previsionnel" },
    { mois: "2026-12", tresorerie_debut: 2490300, encaissements: 4187500, decaissements: 3478200, solde: 709300, tresorerie_fin: 3199600 , type: "previsionnel" },
    { mois: "2027-01", tresorerie_debut: 3199600, encaissements: 2956800, decaissements: 3412500, solde: -455700, tresorerie_fin: 2743900 , type: "previsionnel" },
    { mois: "2027-02", tresorerie_debut: 2743900, encaissements: 3287400, decaissements: 3178600, solde: 108800, tresorerie_fin: 2852700 , type: "previsionnel" },
    { mois: "2027-03", tresorerie_debut: 2852700, encaissements: 3594200, decaissements: 3267800, solde: 326400, tresorerie_fin: 3179100 , type: "previsionnel" },
    { mois: "2027-04", tresorerie_debut: 3179100, encaissements: 3378500, decaissements: 3124300, solde: 254200, tresorerie_fin: 3433300 , type: "previsionnel" },
  ],
  central: [
    ...moisRealises,
    { mois: "2026-05", tresorerie_debut: 5000000, encaissements: 3217800, decaissements: 2987400, solde: 230400, tresorerie_fin: 5230400 , type: "previsionnel" },
    { mois: "2026-06", tresorerie_debut: 5230400, encaissements: 3524600, decaissements: 3078200, solde: 446400, tresorerie_fin: 5676800 , type: "previsionnel" },
    { mois: "2026-07", tresorerie_debut: 5676800, encaissements: 2876300, decaissements: 3012500, solde: -136200, tresorerie_fin: 5540600 , type: "previsionnel" },
    { mois: "2026-08", tresorerie_debut: 5540600, encaissements: 2234700, decaissements: 2813400, solde: -578700, tresorerie_fin: 4961900 , type: "previsionnel" },
    { mois: "2026-09", tresorerie_debut: 4961900, encaissements: 3587200, decaissements: 2934600, solde: 652600, tresorerie_fin: 5614500 , type: "previsionnel" },
    { mois: "2026-10", tresorerie_debut: 5614500, encaissements: 3923400, decaissements: 3018700, solde: 904700, tresorerie_fin: 6519200 , type: "previsionnel" },
    { mois: "2026-11", tresorerie_debut: 6519200, encaissements: 4178500, decaissements: 3124800, solde: 1053700, tresorerie_fin: 7572900 , type: "previsionnel" },
    { mois: "2026-12", tresorerie_debut: 7572900, encaissements: 4823600, decaissements: 3287500, solde: 1536100, tresorerie_fin: 9109000 , type: "previsionnel" },
    { mois: "2027-01", tresorerie_debut: 9109000, encaissements: 3412800, decaissements: 3198600, solde: 214200, tresorerie_fin: 9323200 , type: "previsionnel" },
    { mois: "2027-02", tresorerie_debut: 9323200, encaissements: 3687500, decaissements: 3087400, solde: 600100, tresorerie_fin: 9923300 , type: "previsionnel" },
    { mois: "2027-03", tresorerie_debut: 9923300, encaissements: 4023400, decaissements: 3213600, solde: 809800, tresorerie_fin: 10733100 , type: "previsionnel" },
    { mois: "2027-04", tresorerie_debut: 10733100, encaissements: 3812700, decaissements: 3024500, solde: 788200, tresorerie_fin: 11521300 , type: "previsionnel" },
  ],
  ambitieux: [
    ...moisRealises,
    { mois: "2026-05", tresorerie_debut: 5000000, encaissements: 3627400, decaissements: 2812300, solde: 815100, tresorerie_fin: 5815100 , type: "previsionnel" },
    { mois: "2026-06", tresorerie_debut: 5815100, encaissements: 3934800, decaissements: 2923500, solde: 1011300, tresorerie_fin: 6826400 , type: "previsionnel" },
    { mois: "2026-07", tresorerie_debut: 6826400, encaissements: 2987600, decaissements: 2856200, solde: 131400, tresorerie_fin: 6957800 , type: "previsionnel" },
    { mois: "2026-08", tresorerie_debut: 6957800, encaissements: 2413500, decaissements: 2734800, solde: -321300, tresorerie_fin: 6636500 , type: "previsionnel" },
    { mois: "2026-09", tresorerie_debut: 6636500, encaissements: 3856700, decaissements: 2678400, solde: 1178300, tresorerie_fin: 7814800 , type: "previsionnel" },
    { mois: "2026-10", tresorerie_debut: 7814800, encaissements: 4312500, decaissements: 2812600, solde: 1499900, tresorerie_fin: 9314700 , type: "previsionnel" },
    { mois: "2026-11", tresorerie_debut: 9314700, encaissements: 4523800, decaissements: 2934200, solde: 1589600, tresorerie_fin: 10904300 , type: "previsionnel" },
    { mois: "2026-12", tresorerie_debut: 10904300, encaissements: 5387600, decaissements: 3078500, solde: 2309100, tresorerie_fin: 13213400 , type: "previsionnel" },
    { mois: "2027-01", tresorerie_debut: 13213400, encaissements: 3567200, decaissements: 3012400, solde: 554800, tresorerie_fin: 13768200 , type: "previsionnel" },
    { mois: "2027-02", tresorerie_debut: 13768200, encaissements: 4123600, decaissements: 2923700, solde: 1199900, tresorerie_fin: 14968100 , type: "previsionnel" },
    { mois: "2027-03", tresorerie_debut: 14968100, encaissements: 4378900, decaissements: 3012500, solde: 1366400, tresorerie_fin: 16334500 , type: "previsionnel" },
    { mois: "2027-04", tresorerie_debut: 16334500, encaissements: 4198700, decaissements: 2845300, solde: 1353400, tresorerie_fin: 17687900 , type: "previsionnel" },
  ],
}

export const demoKPIs: KPIs = {
  chiffre_affaires: 42127450,
  marge_brute: 25276470,
  taux_marge_brute: 60.0,
  valeur_ajoutee: 18957350,
  ebe: 12641570,
  taux_ebe: 30.0,
  resultat_net: 8427680,
  caf: 10534600,
  bfr: 7218400,
  creances_clients: 12534700,
  dettes_fournisseurs: 5316300,
  dso_jours: 45,
  dpo_jours: 38,
  tresorerie_nette: 5000000,
}

export const demoCompteResultat: CompteResultat = {
  chiffre_affaires: 42127450,
  achats: 16850980,
  charges_externes: 6319120,
  charges_personnel: 6315780,
  impots_taxes: 2106370,
  dotations: 2106920,
  resultat_exploitation: 10534600,
  resultat_financier: -421380,
  resultat_net: 8427680,
  marge_brute: 25276470,
  valeur_ajoutee: 18957350,
  ebe: 12641570,
  caf: 10534600,
}

export const demoBalanceClients: BalanceAgeeLine[] = [
  { code: "CLI001", nom: "SCI Mahina", total: 3527400, non_echu: 2014200, echu_0_30: 812600, echu_30_60: 398400, echu_60_90: 203800, echu_plus_90: 98400 },
  { code: "CLI002", nom: "SARL Papeete Construction", total: 2843200, non_echu: 1523800, echu_0_30: 712400, echu_30_60: 407600, echu_60_90: 199400, echu_plus_90: 0 },
  { code: "CLI003", nom: "SA Tahiti Nui", total: 2213800, non_echu: 1812400, echu_0_30: 401400, echu_30_60: 0, echu_60_90: 0, echu_plus_90: 0 },
  { code: "CLI004", nom: "SAS Moorea Resort", total: 2087600, non_echu: 487200, echu_0_30: 612800, echu_30_60: 498400, echu_60_90: 312600, echu_plus_90: 176600 },
  { code: "CLI005", nom: "EURL Pacific Services", total: 1923400, non_echu: 1218600, echu_0_30: 398200, echu_30_60: 206800, echu_60_90: 99800, echu_plus_90: 0 },
  { code: "CLI006", nom: "SNC Bora Bora Logistics", total: 1456800, non_echu: 987400, echu_0_30: 312600, echu_30_60: 112400, echu_60_90: 44400, echu_plus_90: 0 },
  { code: "CLI007", nom: "SARL Raiatea Import", total: 1187200, non_echu: 623400, echu_0_30: 287600, echu_30_60: 176200, echu_60_90: 67400, echu_plus_90: 32600 },
  { code: "CLI008", nom: "SA Huahine Développement", total: 876400, non_echu: 654200, echu_0_30: 178400, echu_30_60: 43800, echu_60_90: 0, echu_plus_90: 0 },
]

export const demoBalanceFournisseurs: BalanceAgeeLine[] = [
  { code: "FOU001", nom: "Matériaux du Pacifique", total: 1823400, non_echu: 1212600, echu_0_30: 398400, echu_30_60: 212400, echu_60_90: 0, echu_plus_90: 0 },
  { code: "FOU002", nom: "Transport Polynésien", total: 1218600, non_echu: 812400, echu_0_30: 298200, echu_30_60: 108000, echu_60_90: 0, echu_plus_90: 0 },
  { code: "FOU003", nom: "Electricité de Tahiti", total: 967400, non_echu: 967400, echu_0_30: 0, echu_30_60: 0, echu_60_90: 0, echu_plus_90: 0 },
  { code: "FOU004", nom: "Assurances Océan", total: 756200, non_echu: 756200, echu_0_30: 0, echu_30_60: 0, echu_60_90: 0, echu_plus_90: 0 },
  { code: "FOU005", nom: "Informatique Pacifique", total: 534800, non_echu: 412600, echu_0_30: 87400, echu_30_60: 34800, echu_60_90: 0, echu_plus_90: 0 },
  { code: "FOU006", nom: "Nettoyage Fenua", total: 387200, non_echu: 312400, echu_0_30: 54200, echu_30_60: 20600, echu_60_90: 0, echu_plus_90: 0 },
]

export const demoFluxTresorerie: FluxTresorerie = {
  flux_exploitation: 10534600,
  flux_investissement: -3218400,
  flux_financement: -1812600,
  variation_tresorerie: 5503600,
  resultat_net: 8427680,
  dotations: 2106920,
  variation_bfr: 0,
}
