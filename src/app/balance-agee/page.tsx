"use client"

import { useState } from "react"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts"
import { useData } from "@/lib/data-context"
import { formatXPF } from "@/lib/utils"
import type { BalanceAgeeLine } from "@/lib/types"

const COLORS = ["#10b981", "#f59e0b", "#f97316", "#ef4444", "#b91c1c"]
const LABELS = ["Non échu", "0-30 j", "30-60 j", "60-90 j", "+90 j"]

function BalanceTable({ data }: { data: BalanceAgeeLine[] }) {
  const totals = {
    total: data.reduce((s, d) => s + d.total, 0),
    non_echu: data.reduce((s, d) => s + d.non_echu, 0),
    echu_0_30: data.reduce((s, d) => s + d.echu_0_30, 0),
    echu_30_60: data.reduce((s, d) => s + d.echu_30_60, 0),
    echu_60_90: data.reduce((s, d) => s + d.echu_60_90, 0),
    echu_plus_90: data.reduce((s, d) => s + d.echu_plus_90, 0),
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200">
            <th className="text-left py-3 px-2 text-slate-700 font-medium">Code</th>
            <th className="text-left py-3 px-2 text-slate-700 font-medium">Nom</th>
            <th className="text-right py-3 px-2 text-slate-700 font-medium">Total</th>
            <th className="text-right py-3 px-2 text-slate-700 font-medium">Non échu</th>
            <th className="text-right py-3 px-2 text-slate-700 font-medium">0-30 j</th>
            <th className="text-right py-3 px-2 text-slate-700 font-medium">30-60 j</th>
            <th className="text-right py-3 px-2 text-slate-700 font-medium">60-90 j</th>
            <th className="text-right py-3 px-2 text-slate-700 font-medium">+90 j</th>
          </tr>
        </thead>
        <tbody>
          {data.map((d) => (
            <tr key={d.code} className="border-b border-slate-50 hover:bg-slate-50">
              <td className="py-2.5 px-2 font-mono text-xs text-slate-700">{d.code}</td>
              <td className="py-2.5 px-2 font-medium text-slate-900">{d.nom}</td>
              <td className="py-2.5 px-2 text-right font-semibold text-slate-900">{formatXPF(d.total)}</td>
              <td className="py-2.5 px-2 text-right text-emerald-600">{d.non_echu ? formatXPF(d.non_echu) : "-"}</td>
              <td className="py-2.5 px-2 text-right text-amber-600">{d.echu_0_30 ? formatXPF(d.echu_0_30) : "-"}</td>
              <td className="py-2.5 px-2 text-right text-orange-600">{d.echu_30_60 ? formatXPF(d.echu_30_60) : "-"}</td>
              <td className="py-2.5 px-2 text-right text-red-600">{d.echu_60_90 ? formatXPF(d.echu_60_90) : "-"}</td>
              <td className="py-2.5 px-2 text-right text-red-700 font-medium">{d.echu_plus_90 ? formatXPF(d.echu_plus_90) : "-"}</td>
            </tr>
          ))}
          <tr className="bg-slate-100 font-bold">
            <td className="py-3 px-2" colSpan={2}>TOTAL</td>
            <td className="py-3 px-2 text-right">{formatXPF(totals.total)}</td>
            <td className="py-3 px-2 text-right text-emerald-600">{formatXPF(totals.non_echu)}</td>
            <td className="py-3 px-2 text-right text-amber-600">{formatXPF(totals.echu_0_30)}</td>
            <td className="py-3 px-2 text-right text-orange-600">{formatXPF(totals.echu_30_60)}</td>
            <td className="py-3 px-2 text-right text-red-600">{formatXPF(totals.echu_60_90)}</td>
            <td className="py-3 px-2 text-right text-red-700">{formatXPF(totals.echu_plus_90)}</td>
          </tr>
        </tbody>
      </table>
    </div>
  )
}

function AgeDonut({ data }: { data: BalanceAgeeLine[] }) {
  const pieData = [
    { name: "Non échu", value: data.reduce((s, d) => s + d.non_echu, 0) },
    { name: "0-30 j", value: data.reduce((s, d) => s + d.echu_0_30, 0) },
    { name: "30-60 j", value: data.reduce((s, d) => s + d.echu_30_60, 0) },
    { name: "60-90 j", value: data.reduce((s, d) => s + d.echu_60_90, 0) },
    { name: "+90 j", value: data.reduce((s, d) => s + d.echu_plus_90, 0) },
  ].filter((d) => d.value > 0)

  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} dataKey="value" label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}>
          {pieData.map((_, i) => (
            <Cell key={i} fill={COLORS[LABELS.indexOf(pieData[i].name)] ?? COLORS[0]} />
          ))}
        </Pie>
        <Tooltip formatter={(v) => formatXPF(Number(v ?? 0))} />
      </PieChart>
    </ResponsiveContainer>
  )
}

export default function BalanceAgeePage() {
  const [tab, setTab] = useState<"clients" | "fournisseurs">("clients")
  const { balanceClients, balanceFournisseurs } = useData()
  const data = tab === "clients" ? balanceClients : balanceFournisseurs

  return (
    <div>
      <h1 className="text-xl sm:text-2xl font-bold text-slate-900 mb-1">Balance âgée</h1>
      <p className="text-sm text-slate-700 mb-6">Analyse des créances et dettes par ancienneté</p>

      <div className="flex bg-white rounded-lg border border-slate-200 p-1 w-fit mb-6">
        {(["clients", "fournisseurs"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${tab === t ? "bg-blue-600 text-white shadow-sm" : "text-slate-600 hover:bg-slate-50"}`}
          >
            {t === "clients" ? "Clients" : "Fournisseurs"}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">
            {tab === "clients" ? "Créances clients" : "Dettes fournisseurs"}
          </h2>
          <BalanceTable data={data} />
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Répartition par ancienneté</h2>
          <AgeDonut data={data} />
        </div>
      </div>
    </div>
  )
}
