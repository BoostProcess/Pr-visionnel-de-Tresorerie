"use client"

import { demoForecasts } from "@/lib/demo-data"
import { formatXPF, formatMonth } from "@/lib/utils"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

export default function EncaissementsPage() {
  const data = demoForecasts.central
  const chartData = data.map((d) => ({ mois: formatMonth(d.mois), montant: d.encaissements }))
  const total = data.reduce((s, d) => s + d.encaissements, 0)

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-900 mb-1">Encaissements</h1>
      <p className="text-sm text-slate-500 mb-6">Détail des encaissements prévisionnels par mois</p>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-slate-900">Encaissements mensuels</h2>
          <span className="text-lg font-bold text-emerald-600">Total : {formatXPF(total)}</span>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="mois" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" height={60} />
            <YAxis tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`} tick={{ fontSize: 11 }} />
            <Tooltip formatter={(v) => [formatXPF(Number(v ?? 0)), "Encaissements"]} contentStyle={{ borderRadius: 8 }} />
            <Bar dataKey="montant" fill="#10b981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Détail mensuel</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200">
              <th className="text-left py-3 text-slate-500 font-medium">Mois</th>
              <th className="text-right py-3 text-slate-500 font-medium">Factures clients</th>
              <th className="text-right py-3 text-slate-500 font-medium">Commandes</th>
              <th className="text-right py-3 text-slate-500 font-medium">Total</th>
            </tr>
          </thead>
          <tbody>
            {data.map((d) => (
              <tr key={d.mois} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="py-3 font-medium text-slate-900">{formatMonth(d.mois)}</td>
                <td className="py-3 text-right text-slate-700">{formatXPF(Math.round(d.encaissements * 0.75))}</td>
                <td className="py-3 text-right text-slate-700">{formatXPF(Math.round(d.encaissements * 0.25))}</td>
                <td className="py-3 text-right font-bold text-emerald-700">{formatXPF(d.encaissements)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
