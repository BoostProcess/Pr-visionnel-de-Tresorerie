export interface MonthForecast {
  mois: string
  tresorerie_debut: number
  encaissements: number
  decaissements: number
  solde: number
  tresorerie_fin: number
}

export interface KPIs {
  chiffre_affaires: number
  marge_brute: number
  taux_marge_brute: number
  valeur_ajoutee: number
  ebe: number
  taux_ebe: number
  resultat_net: number
  caf: number
  bfr: number
  creances_clients: number
  dettes_fournisseurs: number
  dso_jours: number
  dpo_jours: number
  tresorerie_nette: number
}

export interface CompteResultat {
  chiffre_affaires: number
  achats: number
  charges_externes: number
  charges_personnel: number
  impots_taxes: number
  dotations: number
  resultat_exploitation: number
  resultat_financier: number
  resultat_net: number
  marge_brute: number
  valeur_ajoutee: number
  ebe: number
  caf: number
}

export interface BalanceAgeeLine {
  code: string
  nom: string
  total: number
  non_echu: number
  echu_0_30: number
  echu_30_60: number
  echu_60_90: number
  echu_plus_90: number
}

export interface FluxTresorerie {
  flux_exploitation: number
  flux_investissement: number
  flux_financement: number
  variation_tresorerie: number
  resultat_net: number
  dotations: number
  variation_bfr: number
}

export interface ImportResult {
  filename: string
  status: "succes" | "partiel" | "echec"
  nb_lignes: number
  nb_importees: number
  nb_doublons: number
  nb_erreurs: number
}

export type Scenario = "prudent" | "central" | "ambitieux"
