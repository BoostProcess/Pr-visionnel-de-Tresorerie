"use client"

import { useState } from "react"
import { KPICard } from "@/components/ui/kpi-card"
import { ForecastBarChart, TresorerieAreaChart } from "@/components/charts/forecast-chart"
import { demoForecasts } from "@/lib/demo-data"
import { formatXPF, formatMonth } from "@/lib/utils"
import type { Scenario } from "@/lib/types"

const scenarios: { key: Scenario; label: string }[] = [
  { key: "prudent", label: "Prudent" },
  { key: "central", label: "Central" },
  { key: "ambitieux", label: "Ambitieux" },
]

export default function Dashboard() {
  const [scenario, setScenario] = useState<Scenario>("central")
  const data = demoForecasts[scenario]
  const pointBas = data.reduce((min, d) => d.tresorerie_fin < min.tresorerie_fin ? d : min, data[0])
  const totalEnc = data.reduce((s, d) => s + d.encaissements, 0)
  const totalDec = data.reduce((s, d) => s + d.decaissements, 0)

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Synthèse du prévisionnel</h1>
          <p className="text-sm text-slate-600 mt-1">Vue sur 12 mois glissants</p>
        </div>
        <div className="flex bg-white rounded-lg border border-slate-200 p-1 self-start">
          {scenarios.map((s) => (
            <button
              key={s.key}
              onClick={() => setScenario(s.key)}
              className={`px-3 sm:px-4 py-2 rounded-md text-xs sm:text-sm font-medium transition-colors ${
                scenario === s.key
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-600 hover:bg-slate-50"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 mb-6 sm:mb-8">
        <KPICard label="Trésorerie actuelle" value={data[0].tresorerie_debut} />
        <KPICard label="Trésorerie fin" value={data[data.length - 1].tresorerie_fin} />
        <KPICard label="Point bas" value={pointBas.tresorerie_fin} delta={formatMonth(pointBas.mois)} trend={pointBas.tresorerie_fin < 0 ? "down" : "neutral"} />
        <KPICard label="Total encaissements" value={totalEnc} trend="up" />
        <KPICard label="Total décaissements" value={totalDec} trend="down" />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm mb-8">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Évolution mensuelle</h2>
        <ForecastBarChart data={data} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Courbe de trésorerie</h2>
          <TresorerieAreaChart data={data} />
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Comparaison des scénarios</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-3 text-slate-600 font-medium">Scénario</th>
                <th className="text-right py-3 text-slate-600 font-medium">Encaiss.</th>
                <th className="text-right py-3 text-slate-600 font-medium">Point bas</th>
                <th className="text-right py-3 text-slate-600 font-medium">Trés. fin</th>
              </tr>
            </thead>
            <tbody>
              {scenarios.map((s) => {
                const sData = demoForecasts[s.key]
                const sPb = Math.min(...sData.map((d) => d.tresorerie_fin))
                const sFin = sData[sData.length - 1].tresorerie_fin
                const sEnc = sData.reduce((sum, d) => sum + d.encaissements, 0)
                return (
                  <tr key={s.key} className="border-b border-slate-100">
                    <td className="py-3 font-medium text-slate-900">{s.label}</td>
                    <td className="py-3 text-right text-slate-700">{formatXPF(sEnc)}</td>
                    <td className={`py-3 text-right font-medium ${sPb < 0 ? "text-red-700" : "text-slate-700"}`}>{formatXPF(sPb)}</td>
                    <td className="py-3 text-right font-bold text-slate-900">{formatXPF(sFin)}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Détail mensuel — {scenarios.find((s) => s.key === scenario)?.label}</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-3 px-2 text-slate-600 font-medium">Mois</th>
                <th className="text-right py-3 px-2 text-slate-600 font-medium">Trés. début</th>
                <th className="text-right py-3 px-2 text-slate-600 font-medium">Encaissements</th>
                <th className="text-right py-3 px-2 text-slate-600 font-medium">Décaissements</th>
                <th className="text-right py-3 px-2 text-slate-600 font-medium">Solde</th>
                <th className="text-right py-3 px-2 text-slate-600 font-medium">Trés. fin</th>
              </tr>
            </thead>
            <tbody>
              {data.map((d) => (
                <tr key={d.mois} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="py-3 px-2 font-medium text-slate-900">{formatMonth(d.mois)}</td>
                  <td className="py-3 px-2 text-right text-slate-700">{formatXPF(d.tresorerie_debut)}</td>
                  <td className="py-3 px-2 text-right text-emerald-700 font-medium">{formatXPF(d.encaissements)}</td>
                  <td className="py-3 px-2 text-right text-red-600 font-medium">{formatXPF(d.decaissements)}</td>
                  <td className={`py-3 px-2 text-right font-semibold ${d.solde < 0 ? "text-red-700" : "text-emerald-700"}`}>{formatXPF(d.solde)}</td>
                  <td className={`py-3 px-2 text-right font-bold ${d.tresorerie_fin < 0 ? "text-red-700" : "text-slate-900"}`}>{formatXPF(d.tresorerie_fin)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
