"use client"

import { useState } from "react"
import { Save, RefreshCw } from "lucide-react"

export default function HypothesesPage() {
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Hypothèses</h1>
          <p className="text-sm text-slate-500 mt-1">Paramétrez les scénarios et hypothèses de calcul</p>
        </div>
        <div className="flex gap-2 sm:gap-3 self-start">
          <button onClick={handleSave} className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
            <Save className="w-4 h-4" />
            {saved ? "Sauvegardé !" : "Sauvegarder"}
          </button>
          <button className="flex items-center gap-2 px-4 py-2.5 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors">
            <RefreshCw className="w-4 h-4" />
            Recalculer
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scénarios */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Ajustements par scénario</h2>
          <div className="space-y-4">
            {[
              { label: "Prudent", desc: "Retards clients, achats maintenus", retard: 15, conversion: -20, fournisseur: 0 },
              { label: "Central", desc: "Hypothèses standard", retard: 0, conversion: 0, fournisseur: 0 },
              { label: "Ambitieux", desc: "Encaissements rapides, décalages optimisés", retard: -5, conversion: 10, fournisseur: 5 },
            ].map((s) => (
              <div key={s.label} className="border border-slate-200 rounded-lg p-4">
                <h3 className="font-medium text-slate-900">{s.label}</h3>
                <p className="text-xs text-slate-500 mb-3">{s.desc}</p>
                <div className="grid grid-cols-3 gap-3">
                  <div>
                    <label className="text-xs text-slate-500">Retard clients (j)</label>
                    <input type="number" defaultValue={s.retard} className="w-full mt-1 px-3 py-2 border border-slate-200 rounded-lg text-sm" />
                  </div>
                  <div>
                    <label className="text-xs text-slate-500">Conversion (%)</label>
                    <input type="number" defaultValue={s.conversion} className="w-full mt-1 px-3 py-2 border border-slate-200 rounded-lg text-sm" />
                  </div>
                  <div>
                    <label className="text-xs text-slate-500">Avance fourn. (j)</label>
                    <input type="number" defaultValue={s.fournisseur} className="w-full mt-1 px-3 py-2 border border-slate-200 rounded-lg text-sm" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* TVA */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">TVA Polynésie Française</h2>
          <div className="space-y-4">
            {[
              { label: "Taux normal", value: 16 },
              { label: "Taux intermédiaire", value: 13 },
              { label: "Taux réduit", value: 5 },
            ].map((t) => (
              <div key={t.label} className="flex items-center justify-between">
                <label className="text-sm text-slate-700">{t.label}</label>
                <div className="flex items-center gap-2">
                  <input type="number" defaultValue={t.value} className="w-20 px-3 py-2 border border-slate-200 rounded-lg text-sm text-right" />
                  <span className="text-sm text-slate-500">%</span>
                </div>
              </div>
            ))}
          </div>

          <h2 className="text-lg font-semibold text-slate-900 mt-8 mb-4">Paramètres généraux</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm text-slate-700">Délai commande → facture (jours)</label>
              <input type="number" defaultValue={15} className="w-20 px-3 py-2 border border-slate-200 rounded-lg text-sm text-right" />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm text-slate-700">Horizon prévisionnel (mois)</label>
              <input type="number" defaultValue={12} className="w-20 px-3 py-2 border border-slate-200 rounded-lg text-sm text-right" />
            </div>
            <div className="flex items-center justify-between">
              <label className="text-sm text-slate-700">Trésorerie initiale (XPF)</label>
              <input type="number" defaultValue={5000000} className="w-40 px-3 py-2 border border-slate-200 rounded-lg text-sm text-right" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
