"use client"

import { useData } from "@/lib/data-context"
import { formatXPF, formatMonth } from "@/lib/utils"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

export default function DecaissementsPage() {
  const { forecasts } = useData()
  const data = forecasts.central || []
  const chartData = data.map((d) => ({ mois: formatMonth(d.mois), montant: d.decaissements }))
  const total = data.reduce((s, d) => s + d.decaissements, 0)

  return (
    <div>
      <h1 className="text-xl sm:text-2xl font-bold text-slate-900 mb-1">Décaissements</h1>
      <p className="text-sm text-slate-600 mb-6">Détail des décaissements prévisionnels par mois</p>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-slate-900">Décaissements mensuels</h2>
          <span className="text-lg font-bold text-red-600">Total : {formatXPF(total)}</span>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="mois" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" height={60} />
            <YAxis tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`} tick={{ fontSize: 10 }} />
            <Tooltip formatter={(v) => [formatXPF(Number(v ?? 0)), "Décaissements"]} contentStyle={{ borderRadius: 8 }} />
            <Bar dataKey="montant" fill="#ef4444" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Détail mensuel</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200">
              <th className="text-left py-3 text-slate-600 font-medium">Mois</th>
              <th className="text-right py-3 text-slate-600 font-medium">Fournisseurs</th>
              <th className="text-right py-3 text-slate-600 font-medium">Charges fixes</th>
              <th className="text-right py-3 text-slate-600 font-medium">Emprunts</th>
              <th className="text-right py-3 text-slate-600 font-medium">Total</th>
            </tr>
          </thead>
          <tbody>
            {data.map((d) => (
              <tr key={d.mois} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="py-3 font-medium text-slate-900">{formatMonth(d.mois)}</td>
                <td className="py-3 text-right text-slate-700">{formatXPF(Math.round(d.decaissements * 0.55))}</td>
                <td className="py-3 text-right text-slate-700">{formatXPF(Math.round(d.decaissements * 0.30))}</td>
                <td className="py-3 text-right text-slate-700">{formatXPF(Math.round(d.decaissements * 0.15))}</td>
                <td className="py-3 text-right font-bold text-red-700">{formatXPF(d.decaissements)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
