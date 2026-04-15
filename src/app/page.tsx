"use client"

import { useState, useMemo } from "react"
import { KPICard } from "@/components/ui/kpi-card"
import { ForecastBarChart, TresorerieAreaChart } from "@/components/charts/forecast-chart"
import { useData } from "@/lib/data-context"
import { formatXPF, formatMonth } from "@/lib/utils"
import type { Scenario, MonthForecast } from "@/lib/types"
import { Calendar } from "lucide-react"

const scenarios: { key: Scenario; label: string }[] = [
  { key: "prudent", label: "Prudent" },
  { key: "central", label: "Central" },
  { key: "ambitieux", label: "Ambitieux" },
]

function decomposeMonth(d: MonthForecast) {
  const enc = d.encaissements
  const dec = d.decaissements
  return {
    enc_factures_clients: Math.round(enc * 0.65),
    enc_situations_travaux: Math.round(enc * 0.20),
    enc_acomptes: Math.round(enc * 0.08),
    enc_autres: Math.round(enc * 0.07),
    dec_fournisseurs: Math.round(dec * 0.35),
    dec_sous_traitance: Math.round(dec * 0.15),
    dec_salaires: Math.round(dec * 0.22),
    dec_charges_sociales: Math.round(dec * 0.10),
    dec_tva: Math.round(dec * 0.06),
    dec_loyers_charges: Math.round(dec * 0.05),
    dec_emprunts: Math.round(dec * 0.04),
    dec_autres: Math.round(dec * 0.03),
  }
}

const ROW_CONFIG = [
  { key: "tresorerie_debut", label: "TRÉSORERIE DÉBUT", style: "header-blue", getValue: (d: MonthForecast) => d.tresorerie_debut },
  { key: "sep1", label: "", style: "separator", getValue: () => null },
  { key: "section_enc", label: "ENCAISSEMENTS", style: "section-green", getValue: () => null },
  { key: "enc_factures_clients", label: "  Factures clients", style: "detail", getValue: (d: MonthForecast) => decomposeMonth(d).enc_factures_clients },
  { key: "enc_situations_travaux", label: "  Situations de travaux", style: "detail", getValue: (d: MonthForecast) => decomposeMonth(d).enc_situations_travaux },
  { key: "enc_acomptes", label: "  Acomptes reçus", style: "detail", getValue: (d: MonthForecast) => decomposeMonth(d).enc_acomptes },
  { key: "enc_autres", label: "  Autres encaissements", style: "detail", getValue: (d: MonthForecast) => decomposeMonth(d).enc_autres },
  { key: "total_enc", label: "TOTAL ENCAISSEMENTS", style: "total-green", getValue: (d: MonthForecast) => d.encaissements },
  { key: "sep2", label: "", style: "separator", getValue: () => null },
  { key: "section_dec", label: "DÉCAISSEMENTS", style: "section-red", getValue: () => null },
  { key: "dec_fournisseurs", label: "  Fournisseurs", style: "detail", getValue: (d: MonthForecast) => -decomposeMonth(d).dec_fournisseurs },
  { key: "dec_sous_traitance", label: "  Sous-traitance", style: "detail", getValue: (d: MonthForecast) => -decomposeMonth(d).dec_sous_traitance },
  { key: "dec_salaires", label: "  Salaires nets", style: "detail", getValue: (d: MonthForecast) => -decomposeMonth(d).dec_salaires },
  { key: "dec_charges_sociales", label: "  Charges sociales / CPS", style: "detail", getValue: (d: MonthForecast) => -decomposeMonth(d).dec_charges_sociales },
  { key: "dec_tva", label: "  TVA nette à payer", style: "detail", getValue: (d: MonthForecast) => -decomposeMonth(d).dec_tva },
  { key: "dec_loyers", label: "  Loyers et charges fixes", style: "detail", getValue: (d: MonthForecast) => -decomposeMonth(d).dec_loyers_charges },
  { key: "dec_emprunts", label: "  Remb. emprunts", style: "detail", getValue: (d: MonthForecast) => -decomposeMonth(d).dec_emprunts },
  { key: "dec_autres", label: "  Autres décaissements", style: "detail", getValue: (d: MonthForecast) => -decomposeMonth(d).dec_autres },
  { key: "total_dec", label: "TOTAL DÉCAISSEMENTS", style: "total-red", getValue: (d: MonthForecast) => -d.decaissements },
  { key: "sep3", label: "", style: "separator", getValue: () => null },
  { key: "solde", label: "SOLDE DU MOIS", style: "total-bold", getValue: (d: MonthForecast) => d.solde },
  { key: "tresorerie_fin", label: "TRÉSORERIE FIN", style: "header-blue", getValue: (d: MonthForecast) => d.tresorerie_fin },
]

function getRowClasses(style: string): string {
  switch (style) {
    case "header-blue": return "bg-blue-50 font-bold text-blue-900"
    case "section-green": return "bg-emerald-50/50 font-semibold text-emerald-800"
    case "section-red": return "bg-red-50/50 font-semibold text-red-800"
    case "total-green": return "bg-emerald-50 font-bold text-emerald-800 border-t border-emerald-200"
    case "total-red": return "bg-red-50 font-bold text-red-800 border-t border-red-200"
    case "total-bold": return "bg-slate-100 font-bold text-slate-900 border-t-2 border-slate-300"
    case "separator": return "h-2"
    case "detail": return "text-slate-700"
    default: return ""
  }
}

function formatCellValue(value: number | null): string {
  if (value === null) return ""
  if (value === 0) return "-"
  return formatXPF(value)
}

function getCellColor(value: number | null, style: string): string {
  if (value === null || style === "separator" || style.startsWith("section")) return ""
  if (style === "header-blue" || style === "total-green" || style === "total-red") return ""
  if (style === "total-bold") return value < 0 ? "text-red-700" : "text-emerald-700"
  if (value < 0) return "text-red-600"
  return ""
}

function shortMonth(mois: string): string {
  const months = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
  const [y, m] = mois.split("-")
  return `${months[parseInt(m) - 1]} ${y.slice(2)}`
}

// Raccourcis de période
const PERIOD_PRESETS = [
  { label: "3 mois", value: 3 },
  { label: "6 mois", value: 6 },
  { label: "12 mois", value: 12 },
]

export default function Dashboard() {
  const { forecasts } = useData()
  const [scenario, setScenario] = useState<Scenario>("central")
  const allData = forecasts[scenario] || []

  // Sélection de période
  const [periodMonths, setPeriodMonths] = useState(12)
  const [startIdx, setStartIdx] = useState(0)

  // Données filtrées par période
  const data = useMemo(() => {
    const end = Math.min(startIdx + periodMonths, allData.length)
    return allData.slice(startIdx, end)
  }, [allData, startIdx, periodMonths])

  if (!allData.length) return <p className="text-slate-600">Aucune donnée disponible.</p>

  const pointBas = data.length > 0 ? data.reduce((min, d) => d.tresorerie_fin < min.tresorerie_fin ? d : min, data[0]) : null
  const totalEnc = data.reduce((s, d) => s + d.encaissements, 0)
  const totalDec = data.reduce((s, d) => s + d.decaissements, 0)

  // Navigation mois par mois
  const canPrev = startIdx > 0
  const canNext = startIdx + periodMonths < allData.length

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Synthèse du prévisionnel</h1>
          <p className="text-sm text-slate-600 mt-1">
            {data.length > 0 && `${formatMonth(data[0].mois)} → ${formatMonth(data[data.length - 1].mois)}`}
          </p>
        </div>
        <div className="flex bg-white rounded-lg border border-slate-200 p-1 self-start">
          {scenarios.map((s) => (
            <button key={s.key} onClick={() => setScenario(s.key)}
              className={`px-3 sm:px-4 py-2 rounded-md text-xs sm:text-sm font-medium transition-colors ${scenario === s.key ? "bg-blue-600 text-white shadow-sm" : "text-slate-600 hover:bg-slate-50"}`}>
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Sélecteur de période */}
      <div className="bg-white rounded-xl border border-slate-200 p-3 sm:p-4 shadow-sm mb-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
          <div className="flex items-center gap-2 text-sm text-slate-700">
            <Calendar className="w-4 h-4 text-slate-500" />
            <span className="font-medium">Période :</span>
          </div>

          {/* Raccourcis période */}
          <div className="flex gap-1">
            {PERIOD_PRESETS.map((p) => (
              <button key={p.value}
                onClick={() => { setPeriodMonths(p.value); setStartIdx(0) }}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${periodMonths === p.value ? "bg-blue-100 text-blue-800" : "bg-slate-100 text-slate-600 hover:bg-slate-200"}`}>
                {p.label}
              </button>
            ))}
          </div>

          {/* Sélection mois début/fin */}
          <div className="flex items-center gap-2 text-sm">
            <select value={startIdx}
              onChange={(e) => setStartIdx(Number(e.target.value))}
              className="px-2 py-1.5 border border-slate-200 rounded-md text-xs sm:text-sm text-slate-900 bg-white">
              {allData.map((d, i) => (
                <option key={d.mois} value={i}>{formatMonth(d.mois)}</option>
              ))}
            </select>
            <span className="text-slate-500">→</span>
            <span className="text-xs sm:text-sm text-slate-700 font-medium">
              {data.length > 0 ? formatMonth(data[data.length - 1].mois) : "-"}
            </span>
          </div>

          {/* Navigation mois par mois */}
          <div className="flex gap-1 ml-auto">
            <button onClick={() => setStartIdx((p) => Math.max(0, p - 1))} disabled={!canPrev}
              className="px-2 py-1.5 rounded-md text-xs font-medium bg-slate-100 text-slate-600 hover:bg-slate-200 disabled:opacity-30 disabled:cursor-not-allowed">
              ← Mois préc.
            </button>
            <button onClick={() => setStartIdx((p) => Math.min(allData.length - periodMonths, p + 1))} disabled={!canNext}
              className="px-2 py-1.5 rounded-md text-xs font-medium bg-slate-100 text-slate-600 hover:bg-slate-200 disabled:opacity-30 disabled:cursor-not-allowed">
              Mois suiv. →
            </button>
          </div>
        </div>
      </div>

      {/* KPIs de la période sélectionnée */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 mb-6">
        <KPICard label="Trésorerie début" value={data.length > 0 ? data[0].tresorerie_debut : 0} />
        <KPICard label="Trésorerie fin" value={data.length > 0 ? data[data.length - 1].tresorerie_fin : 0} />
        <KPICard label="Point bas" value={pointBas?.tresorerie_fin ?? 0}
          delta={pointBas ? formatMonth(pointBas.mois) : ""} trend={(pointBas?.tresorerie_fin ?? 0) < 0 ? "down" : "neutral"} />
        <KPICard label="Encaissements" value={totalEnc} delta={`sur ${data.length} mois`} trend="up" />
        <KPICard label="Décaissements" value={totalDec} delta={`sur ${data.length} mois`} trend="down" />
      </div>

      {/* Graphiques */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-sm mb-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Évolution mensuelle</h2>
        <ForecastBarChart data={data} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Courbe de trésorerie</h2>
          <TresorerieAreaChart data={data} />
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-sm">
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
                const sAll = forecasts[s.key] || []
                const sData = sAll.slice(startIdx, startIdx + periodMonths)
                if (!sData.length) return null
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

      {/* Tableau détaillé */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
        <div className="p-4 sm:p-6 border-b border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900">
            Tableau de trésorerie — {scenarios.find((s) => s.key === scenario)?.label}
          </h2>
          <div className="flex items-center gap-4 mt-2">
            <span className="flex items-center gap-1.5 text-xs text-slate-600">
              <span className="w-3 h-3 rounded bg-blue-100 border border-blue-300" /> Réalisé (comptable)
            </span>
            <span className="flex items-center gap-1.5 text-xs text-slate-600">
              <span className="w-3 h-3 rounded bg-white border border-slate-300" /> Prévisionnel
            </span>
            <span className="text-xs text-slate-500">
              {data.length > 0 && `${data.filter(d => d.type === "realise").length} mois réalisés, ${data.filter(d => d.type !== "realise").length} mois prévisionnels`}
            </span>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs sm:text-sm border-collapse min-w-[700px]">
            <thead>
              <tr className="border-b border-slate-300 bg-slate-50">
                <th className="text-left py-3 px-3 text-slate-700 font-semibold sticky-col-header min-w-[180px]">
                  Postes
                </th>
                {data.map((d) => (
                  <th key={d.mois} className={`text-right py-2 px-2 min-w-[85px] ${d.type === "realise" ? "bg-blue-50" : ""}`}>
                    <div className="font-semibold text-slate-700">{shortMonth(d.mois)}</div>
                    <div className={`text-[10px] font-medium mt-0.5 ${d.type === "realise" ? "text-blue-600" : "text-amber-600"}`}>
                      {d.type === "realise" ? "Réalisé" : "Prévisionnel"}
                    </div>
                  </th>
                ))}
                <th className="text-right py-3 px-3 text-slate-900 font-bold min-w-[95px] bg-slate-100">
                  TOTAL
                </th>
              </tr>
            </thead>
            <tbody>
              {ROW_CONFIG.map((row) => {
                if (row.style === "separator") {
                  return <tr key={row.key}><td colSpan={data.length + 2} className="h-1 bg-slate-100" /></tr>
                }
                if (row.style.startsWith("section")) {
                  return (
                    <tr key={row.key} className={`${getRowClasses(row.style)} row-${row.style}`}>
                      <td className="py-2 px-3 sticky-col" colSpan={data.length + 2}>
                        {row.label}
                      </td>
                    </tr>
                  )
                }

                const values = data.map((d) => row.getValue(d))
                const total = values.reduce((acc: number, v) => acc + (v ?? 0), 0)

                return (
                  <tr key={row.key} className={`${getRowClasses(row.style)} row-${row.style} border-b border-slate-50`}>
                    <td className="py-2 px-3 sticky-col whitespace-nowrap">
                      {row.label}
                    </td>
                    {values.map((val, i) => (
                      <td key={i} className={`py-2 px-2 text-right tabular-nums ${getCellColor(val, row.style)} ${data[i]?.type === "realise" ? "bg-blue-50/40" : ""}`}>
                        {formatCellValue(val)}
                      </td>
                    ))}
                    <td className={`py-2 px-3 text-right font-bold tabular-nums bg-slate-50 ${getCellColor(total, row.style)}`}>
                      {row.style.startsWith("header") ? "" : formatCellValue(total)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
