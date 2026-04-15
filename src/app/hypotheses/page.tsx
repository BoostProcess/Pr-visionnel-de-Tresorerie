"use client"

import { useState } from "react"
import { Save, RefreshCw } from "lucide-react"
import { useToast } from "@/components/ui/toast"

interface ScenarioValues {
  retard: number
  conversion: number
  fournisseur: number
}

interface TvaValues {
  normal: number
  intermediaire: number
  reduit: number
}

export default function HypothesesPage() {
  const { show, ToastComponent } = useToast()

  const [scenarios, setScenarios] = useState<Record<string, ScenarioValues>>({
    Prudent: { retard: 15, conversion: -20, fournisseur: 0 },
    Central: { retard: 0, conversion: 0, fournisseur: 0 },
    Ambitieux: { retard: -5, conversion: 10, fournisseur: 5 },
  })

  const [tva, setTva] = useState<TvaValues>({
    normal: 16,
    intermediaire: 13,
    reduit: 5,
  })

  const [delaiFacture, setDelaiFacture] = useState(15)
  const [horizon, setHorizon] = useState(12)
  const [tresorerieInitiale, setTresorerieInitiale] = useState(5000000)

  const scenarioMeta: Record<string, string> = {
    Prudent: "Retards clients, achats maintenus",
    Central: "Hypotheses standard",
    Ambitieux: "Encaissements rapides, decalages optimises",
  }

  const clampDelay = (v: number) => Math.max(-90, Math.min(90, v))
  const clampTva = (v: number) => Math.max(0, Math.min(50, v))
  const clampHorizon = (v: number) => Math.max(1, Math.min(60, v))
  const clampTresorerie = (v: number) => Math.max(0, Math.min(999999999, v))

  const handleScenarioChange = (label: string, field: keyof ScenarioValues, raw: string) => {
    const parsed = raw === "" || raw === "-" ? 0 : Number(raw)
    if (isNaN(parsed)) return
    setScenarios((prev) => ({
      ...prev,
      [label]: { ...prev[label], [field]: clampDelay(parsed) },
    }))
  }

  const handleSave = () => {
    show("Hypotheses sauvegardees", "success")
  }

  const handleRecalc = () => {
    show("Previsionnel recalcule", "info")
  }

  return (
    <div>
      {ToastComponent}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Hypotheses</h1>
          <p className="text-sm text-slate-600 mt-1">Parametrez les scenarios et hypotheses de calcul</p>
        </div>
        <div className="flex gap-2 sm:gap-3 self-start">
          <button onClick={handleSave} className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
            <Save className="w-4 h-4" />
            Sauvegarder
          </button>
          <button onClick={handleRecalc} className="flex items-center gap-2 px-4 py-2.5 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors">
            <RefreshCw className="w-4 h-4" />
            Recalculer
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scenarios */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Ajustements par scenario</h2>
          <div className="space-y-4">
            {Object.entries(scenarios).map(([label, values]) => (
              <div key={label} className="border border-slate-200 rounded-lg p-4">
                <h3 className="font-medium text-slate-900">{label}</h3>
                <p className="text-xs text-slate-600 mb-3">{scenarioMeta[label]}</p>
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="text-xs text-slate-600">Retard clients (j)</label>
                    <input
                      type="number"
                      min={-90}
                      max={90}
                      value={values.retard}
                      onChange={(e) => handleScenarioChange(label, "retard", e.target.value)}
                      className="w-full mt-1 px-3 py-2 border border-slate-200 rounded-lg text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-600">Conversion (%)</label>
                    <input
                      type="number"
                      min={-90}
                      max={90}
                      value={values.conversion}
                      onChange={(e) => handleScenarioChange(label, "conversion", e.target.value)}
                      className="w-full mt-1 px-3 py-2 border border-slate-200 rounded-lg text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-600">Avance fourn. (j)</label>
                    <input
                      type="number"
                      min={-90}
                      max={90}
                      value={values.fournisseur}
                      onChange={(e) => handleScenarioChange(label, "fournisseur", e.target.value)}
                      className="w-full mt-1 px-3 py-2 border border-slate-200 rounded-lg text-sm"
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* TVA */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">TVA Polynesie Francaise</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm text-slate-700">Taux normal</label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  min={0}
                  max={50}
                  value={tva.normal}
                  onChange={(e) => setTva((prev) => ({ ...prev, normal: clampTva(Number(e.target.value) || 0) }))}
                  className="w-20 px-3 py-2 border border-slate-200 rounded-lg text-sm text-right"
                />
                <span className="text-sm text-slate-600">%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm text-slate-700">Taux intermediaire</label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  min={0}
                  max={50}
                  value={tva.intermediaire}
                  onChange={(e) => setTva((prev) => ({ ...prev, intermediaire: clampTva(Number(e.target.value) || 0) }))}
                  className="w-20 px-3 py-2 border border-slate-200 rounded-lg text-sm text-right"
                />
                <span className="text-sm text-slate-600">%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm text-slate-700">Taux reduit</label>
              <div className="flex items-center gap-2">
                <input
                  type="number"
                  min={0}
                  max={50}
                  value={tva.reduit}
                  onChange={(e) => setTva((prev) => ({ ...prev, reduit: clampTva(Number(e.target.value) || 0) }))}
                  className="w-20 px-3 py-2 border border-slate-200 rounded-lg text-sm text-right"
                />
                <span className="text-sm text-slate-600">%</span>
              </div>
            </div>
          </div>

          <h2 className="text-lg font-semibold text-slate-900 mt-8 mb-4">Parametres generaux</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm text-slate-700">Delai commande - facture (jours)</label>
              <input
                type="number"
                min={-90}
                max={90}
                value={delaiFacture}
                onChange={(e) => setDelaiFacture(clampDelay(Number(e.target.value) || 0))}
                className="w-20 px-3 py-2 border border-slate-200 rounded-lg text-sm text-right"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm text-slate-700">Horizon previsionnel (mois)</label>
              <input
                type="number"
                min={1}
                max={60}
                value={horizon}
                onChange={(e) => setHorizon(clampHorizon(Number(e.target.value) || 1))}
                className="w-20 px-3 py-2 border border-slate-200 rounded-lg text-sm text-right"
              />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm text-slate-700">Tresorerie initiale (XPF)</label>
              <input
                type="number"
                min={0}
                max={999999999}
                value={tresorerieInitiale}
                onChange={(e) => setTresorerieInitiale(clampTresorerie(Number(e.target.value) || 0))}
                className="w-40 px-3 py-2 border border-slate-200 rounded-lg text-sm text-right"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
