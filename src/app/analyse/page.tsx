"use client"

import { KPICard } from "@/components/ui/kpi-card"
import { WaterfallChart } from "@/components/charts/waterfall-chart"
import { useData } from "@/lib/data-context"
import { formatXPF } from "@/lib/utils"

export default function AnalysePage() {
  const { kpis, compteResultat: cr } = useData()

  const sigData = [
    { name: "CA", value: cr.chiffre_affaires, isTotal: false },
    { name: "Achats", value: -cr.achats },
    { name: "Chg. ext.", value: -cr.charges_externes },
    { name: "Personnel", value: -cr.charges_personnel },
    { name: "EBE", value: cr.ebe, isTotal: true },
    { name: "Amort.", value: -cr.dotations },
    { name: "Financier", value: cr.resultat_financier },
    { name: "Rés. net", value: cr.resultat_net, isTotal: true },
  ]

  const sigTable = [
    { label: "Chiffre d'affaires", montant: cr.chiffre_affaires, type: "produit" },
    { label: "- Achats consommés", montant: -cr.achats, type: "charge" },
    { label: "= Marge brute", montant: cr.marge_brute, type: "solde" },
    { label: "- Charges externes", montant: -cr.charges_externes, type: "charge" },
    { label: "= Valeur ajoutée", montant: cr.valeur_ajoutee, type: "solde" },
    { label: "- Impôts et taxes", montant: -cr.impots_taxes, type: "charge" },
    { label: "- Charges de personnel", montant: -cr.charges_personnel, type: "charge" },
    { label: "= EBE", montant: cr.ebe, type: "solde" },
    { label: "- Dotations amortissements", montant: -cr.dotations, type: "charge" },
    { label: "= Résultat d'exploitation", montant: cr.resultat_exploitation, type: "solde" },
    { label: "+ Résultat financier", montant: cr.resultat_financier, type: "produit" },
    { label: "= Résultat net", montant: cr.resultat_net, type: "solde" },
    { label: "CAF", montant: cr.caf, type: "solde" },
  ]

  return (
    <div>
      <h1 className="text-xl sm:text-2xl font-bold text-slate-900 mb-1">Analyse financière</h1>
      <p className="text-sm text-slate-600 mb-6">Reconstitution automatique depuis le FEC</p>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6 sm:mb-8">
        <KPICard label="Chiffre d'affaires" value={kpis.chiffre_affaires} />
        <KPICard label="Marge brute" value={kpis.marge_brute} delta={`${kpis.taux_marge_brute}%`} trend="up" />
        <KPICard label="EBE" value={kpis.ebe} delta={`${kpis.taux_ebe}%`} trend="up" />
        <KPICard label="Résultat net" value={kpis.resultat_net} />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6 sm:mb-8">
        <KPICard label="CAF" value={kpis.caf} />
        <KPICard label="BFR" value={kpis.bfr} />
        <KPICard label="DSO (délai clients)" value={kpis.dso_jours} format="days" />
        <KPICard label="DPO (délai fournisseurs)" value={kpis.dpo_jours} format="days" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6 mb-6 sm:mb-8">
        {/* Waterfall SIG */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Du CA au Résultat Net</h2>
          <WaterfallChart data={sigData} />
        </div>

        {/* Tableau SIG */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Soldes Intermédiaires de Gestion</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2 text-slate-600 font-medium">Indicateur</th>
                <th className="text-right py-2 text-slate-600 font-medium">Montant (XPF)</th>
              </tr>
            </thead>
            <tbody>
              {sigTable.map((row, i) => (
                <tr key={i} className={`border-b border-slate-50 ${row.type === "solde" ? "bg-slate-50 font-semibold" : ""}`}>
                  <td className={`py-2.5 ${row.type === "solde" ? "text-blue-700" : ""}`}>{row.label}</td>
                  <td className={`py-2.5 text-right ${row.montant < 0 ? "text-red-600" : ""}`}>{formatXPF(row.montant)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
