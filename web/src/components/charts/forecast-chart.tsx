"use client"

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer, Line, ComposedChart, Area,
} from "recharts"
import type { MonthForecast } from "@/lib/types"
import { formatXPF, formatMonth } from "@/lib/utils"

interface ForecastChartProps {
  data: MonthForecast[]
}

export function ForecastBarChart({ data }: ForecastChartProps) {
  const chartData = data.map((d) => ({
    mois: formatMonth(d.mois),
    Encaissements: d.encaissements,
    Décaissements: d.decaissements,
    "Trésorerie fin": d.tresorerie_fin,
  }))

  return (
    <ResponsiveContainer width="100%" height={380}>
      <ComposedChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="mois" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" height={60} />
        <YAxis tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`} tick={{ fontSize: 11 }} />
        <Tooltip
          formatter={(value, name) => [formatXPF(Number(value ?? 0)), String(name)]}
          contentStyle={{ borderRadius: 8, border: "1px solid #e2e8f0" }}
        />
        <Legend />
        <Bar dataKey="Encaissements" fill="#10b981" radius={[4, 4, 0, 0]} />
        <Bar dataKey="Décaissements" fill="#ef4444" radius={[4, 4, 0, 0]} />
        <Line
          type="monotone"
          dataKey="Trésorerie fin"
          stroke="#3b82f6"
          strokeWidth={2.5}
          dot={{ r: 4, fill: "#3b82f6" }}
        />
      </ComposedChart>
    </ResponsiveContainer>
  )
}

export function TresorerieAreaChart({ data }: ForecastChartProps) {
  const chartData = data.map((d) => ({
    mois: formatMonth(d.mois),
    trésorerie: d.tresorerie_fin,
  }))

  return (
    <ResponsiveContainer width="100%" height={250}>
      <ComposedChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="mois" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" height={60} />
        <YAxis tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`} tick={{ fontSize: 11 }} />
        <Tooltip formatter={(value) => [formatXPF(Number(value ?? 0)), "Trésorerie"]}
          contentStyle={{ borderRadius: 8, border: "1px solid #e2e8f0" }}
        />
        <Area type="monotone" dataKey="trésorerie" stroke="#3b82f6" fill="#3b82f680" strokeWidth={2} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
