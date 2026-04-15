"use client"

import { useState } from "react"
import { Plus, Trash2 } from "lucide-react"
import { formatXPF } from "@/lib/utils"

interface Adjustment {
  id: number
  date: string
  direction: "encaissement" | "decaissement"
  label: string
  amount: number
  category: string
}

const initialAdjustments: Adjustment[] = [
  { id: 1, date: "2026-06-15", direction: "encaissement", label: "Subvention Pays", amount: 2000000, category: "Subvention" },
  { id: 2, date: "2026-07-01", direction: "decaissement", label: "Investissement véhicule", amount: 3500000, category: "Investissement" },
  { id: 3, date: "2026-09-10", direction: "encaissement", label: "Remboursement caution", amount: 500000, category: "Autre" },
]

export default function AjustementsPage() {
  const [adjustments, setAdjustments] = useState<Adjustment[]>(initialAdjustments)

  const removeAdjustment = (id: number) => {
    setAdjustments((prev) => prev.filter((a) => a.id !== id))
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Ajustements manuels</h1>
          <p className="text-sm text-slate-500 mt-1">Corrections ponctuelles sur le prévisionnel</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
          <Plus className="w-4 h-4" />
          Nouvel ajustement
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200">
              <th className="text-left py-3 text-slate-500 font-medium">Date</th>
              <th className="text-left py-3 text-slate-500 font-medium">Type</th>
              <th className="text-left py-3 text-slate-500 font-medium">Libellé</th>
              <th className="text-left py-3 text-slate-500 font-medium">Catégorie</th>
              <th className="text-right py-3 text-slate-500 font-medium">Montant</th>
              <th className="text-right py-3 text-slate-500 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {adjustments.map((a) => (
              <tr key={a.id} className="border-b border-slate-50 hover:bg-slate-50">
                <td className="py-3">{new Date(a.date).toLocaleDateString("fr-FR")}</td>
                <td className="py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    a.direction === "encaissement"
                      ? "bg-emerald-50 text-emerald-700"
                      : "bg-red-50 text-red-700"
                  }`}>
                    {a.direction === "encaissement" ? "Encaissement" : "Décaissement"}
                  </span>
                </td>
                <td className="py-3 font-medium">{a.label}</td>
                <td className="py-3 text-slate-500">{a.category}</td>
                <td className={`py-3 text-right font-semibold ${
                  a.direction === "encaissement" ? "text-emerald-600" : "text-red-500"
                }`}>
                  {a.direction === "encaissement" ? "+" : "-"}{formatXPF(a.amount)}
                </td>
                <td className="py-3 text-right">
                  <button onClick={() => removeAdjustment(a.id)} className="text-slate-400 hover:text-red-500 transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {adjustments.length === 0 && (
          <p className="text-center text-slate-400 py-8">Aucun ajustement manuel</p>
        )}
      </div>
    </div>
  )
}
