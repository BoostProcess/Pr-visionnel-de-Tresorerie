"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from "recharts"
import { formatXPF } from "@/lib/utils"

interface WaterfallItem {
  name: string
  value: number
  isTotal?: boolean
}

interface WaterfallChartProps {
  data: WaterfallItem[]
  height?: number
}

export function WaterfallChart({ data, height = 280 }: WaterfallChartProps) {
  let running = 0
  const chartData = data.map((item) => {
    if (item.isTotal) {
      running = item.value
      return { name: item.name, value: item.value, base: 0, fill: "#3b82f6" }
    }
    const base = running
    running += item.value
    return {
      name: item.name,
      value: item.value,
      base: item.value >= 0 ? base : base + item.value,
      fill: item.value >= 0 ? "#10b981" : "#ef4444",
    }
  })

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={chartData} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="name" tick={{ fontSize: 10 }} />
        <YAxis tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`} tick={{ fontSize: 10 }} />
        <Tooltip
          formatter={(value, name) => {
            if (String(name) === "base") return [null, null]
            return [formatXPF(Number(value ?? 0)), "Montant"]
          }}
          contentStyle={{ borderRadius: 8, border: "1px solid #e2e8f0" }}
        />
        <ReferenceLine y={0} stroke="#94a3b8" />
        <Bar dataKey="base" stackId="stack" fill="transparent" />
        <Bar dataKey="value" stackId="stack" radius={[4, 4, 0, 0]}>
          {chartData.map((entry, index) => (
            <Cell key={index} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
