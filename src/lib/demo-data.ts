import type { MonthForecast, KPIs, CompteResultat, BalanceAgeeLine, FluxTresorerie } from "./types"

export const demoForecasts: Record<string, MonthForecast[]> = {
  prudent: [
    { mois: "2026-05", tresorerie_debut: 5000000, encaissements: 2800000, decaissements: 3200000, solde: -400000, tresorerie_fin: 4600000 },
    { mois: "2026-06", tresorerie_debut: 4600000, encaissements: 3100000, decaissements: 3300000, solde: -200000, tresorerie_fin: 4400000 },
    { mois: "2026-07", tresorerie_debut: 4400000, encaissements: 2500000, decaissements: 3100000, solde: -600000, tresorerie_fin: 3800000 },
    { mois: "2026-08", tresorerie_debut: 3800000, encaissements: 1800000, decaissements: 2900000, solde: -1100000, tresorerie_fin: 2700000 },
    { mois: "2026-09", tresorerie_debut: 2700000, encaissements: 3200000, decaissements: 3000000, solde: 200000, tresorerie_fin: 2900000 },
    { mois: "2026-10", tresorerie_debut: 2900000, encaissements: 3500000, decaissements: 3100000, solde: 400000, tresorerie_fin: 3300000 },
    { mois: "2026-11", tresorerie_debut: 3300000, encaissements: 3800000, decaissements: 3200000, solde: 600000, tresorerie_fin: 3900000 },
    { mois: "2026-12", tresorerie_debut: 3900000, encaissements: 4200000, decaissements: 3500000, solde: 700000, tresorerie_fin: 4600000 },
    { mois: "2027-01", tresorerie_debut: 4600000, encaissements: 3000000, decaissements: 3400000, solde: -400000, tresorerie_fin: 4200000 },
    { mois: "2027-02", tresorerie_debut: 4200000, encaissements: 3300000, decaissements: 3200000, solde: 100000, tresorerie_fin: 4300000 },
    { mois: "2027-03", tresorerie_debut: 4300000, encaissements: 3600000, decaissements: 3300000, solde: 300000, tresorerie_fin: 4600000 },
    { mois: "2027-04", tresorerie_debut: 4600000, encaissements: 3400000, decaissements: 3100000, solde: 300000, tresorerie_fin: 4900000 },
  ],
  central: [
    { mois: "2026-05", tresorerie_debut: 5000000, encaissements: 3200000, decaissements: 3000000, solde: 200000, tresorerie_fin: 5200000 },
    { mois: "2026-06", tresorerie_debut: 5200000, encaissements: 3500000, decaissements: 3100000, solde: 400000, tresorerie_fin: 5600000 },
    { mois: "2026-07", tresorerie_debut: 5600000, encaissements: 2900000, decaissements: 3000000, solde: -100000, tresorerie_fin: 5500000 },
    { mois: "2026-08", tresorerie_debut: 5500000, encaissements: 2200000, decaissements: 2800000, solde: -600000, tresorerie_fin: 4900000 },
    { mois: "2026-09", tresorerie_debut: 4900000, encaissements: 3600000, decaissements: 2900000, solde: 700000, tresorerie_fin: 5600000 },
    { mois: "2026-10", tresorerie_debut: 5600000, encaissements: 3900000, decaissements: 3000000, solde: 900000, tresorerie_fin: 6500000 },
    { mois: "2026-11", tresorerie_debut: 6500000, encaissements: 4200000, decaissements: 3100000, solde: 1100000, tresorerie_fin: 7600000 },
    { mois: "2026-12", tresorerie_debut: 7600000, encaissements: 4800000, decaissements: 3300000, solde: 1500000, tresorerie_fin: 9100000 },
    { mois: "2027-01", tresorerie_debut: 9100000, encaissements: 3400000, decaissements: 3200000, solde: 200000, tresorerie_fin: 9300000 },
    { mois: "2027-02", tresorerie_debut: 9300000, encaissements: 3700000, decaissements: 3100000, solde: 600000, tresorerie_fin: 9900000 },
    { mois: "2027-03", tresorerie_debut: 9900000, encaissements: 4000000, decaissements: 3200000, solde: 800000, tresorerie_fin: 10700000 },
    { mois: "2027-04", tresorerie_debut: 10700000, encaissements: 3800000, decaissements: 3000000, solde: 800000, tresorerie_fin: 11500000 },
  ],
  ambitieux: [
    { mois: "2026-05", tresorerie_debut: 5000000, encaissements: 3600000, decaissements: 2800000, solde: 800000, tresorerie_fin: 5800000 },
    { mois: "2026-06", tresorerie_debut: 5800000, encaissements: 3900000, decaissements: 2900000, solde: 1000000, tresorerie_fin: 6800000 },
    { mois: "2026-07", tresorerie_debut: 6800000, encaissements: 3300000, decaissements: 2800000, solde: 500000, tresorerie_fin: 7300000 },
    { mois: "2026-08", tresorerie_debut: 7300000, encaissements: 2600000, decaissements: 2600000, solde: 0, tresorerie_fin: 7300000 },
    { mois: "2026-09", tresorerie_debut: 7300000, encaissements: 4000000, decaissements: 2700000, solde: 1300000, tresorerie_fin: 8600000 },
    { mois: "2026-10", tresorerie_debut: 8600000, encaissements: 4300000, decaissements: 2800000, solde: 1500000, tresorerie_fin: 10100000 },
    { mois: "2026-11", tresorerie_debut: 10100000, encaissements: 4700000, decaissements: 2900000, solde: 1800000, tresorerie_fin: 11900000 },
    { mois: "2026-12", tresorerie_debut: 11900000, encaissements: 5200000, decaissements: 3100000, solde: 2100000, tresorerie_fin: 14000000 },
    { mois: "2027-01", tresorerie_debut: 14000000, encaissements: 3800000, decaissements: 3000000, solde: 800000, tresorerie_fin: 14800000 },
    { mois: "2027-02", tresorerie_debut: 14800000, encaissements: 4100000, decaissements: 2900000, solde: 1200000, tresorerie_fin: 16000000 },
    { mois: "2027-03", tresorerie_debut: 16000000, encaissements: 4400000, decaissements: 3000000, solde: 1400000, tresorerie_fin: 17400000 },
    { mois: "2027-04", tresorerie_debut: 17400000, encaissements: 4200000, decaissements: 2800000, solde: 1400000, tresorerie_fin: 18800000 },
  ],
}

export const demoKPIs: KPIs = {
  chiffre_affaires: 42000000,
  marge_brute: 25200000,
  taux_marge_brute: 60.0,
  valeur_ajoutee: 18900000,
  ebe: 12600000,
  taux_ebe: 30.0,
  resultat_net: 8400000,
  caf: 10500000,
  bfr: 7200000,
  creances_clients: 12500000,
  dettes_fournisseurs: 5300000,
  dso_jours: 45,
  dpo_jours: 38,
  tresorerie_nette: 5000000,
}

export const demoCompteResultat: CompteResultat = {
  chiffre_affaires: 42000000,
  achats: 16800000,
  charges_externes: 6300000,
  charges_personnel: 6300000,
  impots_taxes: 2100000,
  dotations: 2100000,
  resultat_exploitation: 10500000,
  resultat_financier: -420000,
  resultat_net: 8400000,
  marge_brute: 25200000,
  valeur_ajoutee: 18900000,
  ebe: 12600000,
  caf: 10500000,
}

export const demoBalanceClients: BalanceAgeeLine[] = [
  { code: "CLI001", nom: "SCI Mahina", total: 3500000, non_echu: 2000000, echu_0_30: 800000, echu_30_60: 400000, echu_60_90: 200000, echu_plus_90: 100000 },
  { code: "CLI002", nom: "SARL Papeete Construction", total: 2800000, non_echu: 1500000, echu_0_30: 700000, echu_30_60: 400000, echu_60_90: 200000, echu_plus_90: 0 },
  { code: "CLI003", nom: "SA Tahiti Nui", total: 2200000, non_echu: 1800000, echu_0_30: 400000, echu_30_60: 0, echu_60_90: 0, echu_plus_90: 0 },
  { code: "CLI004", nom: "SAS Moorea Resort", total: 2100000, non_echu: 500000, echu_0_30: 600000, echu_30_60: 500000, echu_60_90: 300000, echu_plus_90: 200000 },
  { code: "CLI005", nom: "EURL Pacific Services", total: 1900000, non_echu: 1200000, echu_0_30: 400000, echu_30_60: 200000, echu_60_90: 100000, echu_plus_90: 0 },
]

export const demoBalanceFournisseurs: BalanceAgeeLine[] = [
  { code: "FOU001", nom: "Matériaux du Pacifique", total: 1800000, non_echu: 1200000, echu_0_30: 400000, echu_30_60: 200000, echu_60_90: 0, echu_plus_90: 0 },
  { code: "FOU002", nom: "Transport Polynésien", total: 1200000, non_echu: 800000, echu_0_30: 300000, echu_30_60: 100000, echu_60_90: 0, echu_plus_90: 0 },
  { code: "FOU003", nom: "Electricité de Tahiti", total: 950000, non_echu: 950000, echu_0_30: 0, echu_30_60: 0, echu_60_90: 0, echu_plus_90: 0 },
  { code: "FOU004", nom: "Assurances Océan", total: 750000, non_echu: 750000, echu_0_30: 0, echu_30_60: 0, echu_60_90: 0, echu_plus_90: 0 },
]

export const demoFluxTresorerie: FluxTresorerie = {
  flux_exploitation: 10500000,
  flux_investissement: -3200000,
  flux_financement: -1800000,
  variation_tresorerie: 5500000,
  resultat_net: 8400000,
  dotations: 2100000,
  variation_bfr: 0,
}
