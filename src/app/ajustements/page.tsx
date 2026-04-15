"use client"

import { useState } from "react"
import { Plus, Trash2, X } from "lucide-react"
import { formatXPF } from "@/lib/utils"
import { useToast } from "@/components/ui/toast"
import { ConfirmModal } from "@/components/ui/confirm-modal"

interface Adjustment {
  id: number
  date: string
  direction: "encaissement" | "decaissement"
  label: string
  amount: number
  category: string
}

const CATEGORIES = [
  "Subvention",
  "Investissement",
  "Emprunt",
  "Remboursement",
  "Cession",
  "Dividende",
  "Taxe / Impôt",
  "Autre",
]

const initialAdjustments: Adjustment[] = [
  { id: 1, date: "2026-06-15", direction: "encaissement", label: "Subvention Pays", amount: 2000000, category: "Subvention" },
  { id: 2, date: "2026-07-01", direction: "decaissement", label: "Investissement véhicule", amount: 3500000, category: "Investissement" },
  { id: 3, date: "2026-09-10", direction: "encaissement", label: "Remboursement caution", amount: 500000, category: "Remboursement" },
]

let nextId = 10

export default function AjustementsPage() {
  const [adjustments, setAdjustments] = useState<Adjustment[]>(initialAdjustments)
  const [showForm, setShowForm] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<Adjustment | null>(null)
  const { show: showToast, ToastComponent } = useToast()

  const [formDate, setFormDate] = useState("")
  const [formDirection, setFormDirection] = useState<"encaissement" | "decaissement">("encaissement")
  const [formLabel, setFormLabel] = useState("")
  const [formAmount, setFormAmount] = useState("")
  const [formCategory, setFormCategory] = useState(CATEGORIES[0])

  const resetForm = () => {
    setFormDate("")
    setFormDirection("encaissement")
    setFormLabel("")
    setFormAmount("")
    setFormCategory(CATEGORIES[0])
  }

  const addAdjustment = () => {
    if (!formDate || !formLabel || !formAmount || Number(formAmount) <= 0) {
      showToast("Veuillez remplir tous les champs correctement.", "error")
      return
    }
    setAdjustments((prev) => [{
      id: nextId++,
      date: formDate,
      direction: formDirection,
      label: formLabel,
      amount: Math.round(Number(formAmount)),
      category: formCategory,
    }, ...prev])
    resetForm()
    setShowForm(false)
    showToast("Ajustement ajouté avec succès.", "success")
  }

  const confirmDelete = () => {
    if (!deleteTarget) return
    setAdjustments((prev) => prev.filter((a) => a.id !== deleteTarget.id))
    showToast("Ajustement supprimé.", "success")
    setDeleteTarget(null)
  }

  const totalEnc = adjustments.filter((a) => a.direction === "encaissement").reduce((s, a) => s + a.amount, 0)
  const totalDec = adjustments.filter((a) => a.direction === "decaissement").reduce((s, a) => s + a.amount, 0)

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Ajustements manuels</h1>
          <p className="text-sm text-slate-600 mt-1">Corrections ponctuelles sur le prévisionnel</p>
        </div>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors self-start">
          <Plus className="w-4 h-4" />
          Nouvel ajustement
        </button>
      </div>

      {/* Résumé */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <p className="text-xs text-slate-600 font-medium">Total encaissements</p>
          <p className="text-lg font-bold text-emerald-700 mt-1">+{formatXPF(totalEnc)}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <p className="text-xs text-slate-600 font-medium">Total décaissements</p>
          <p className="text-lg font-bold text-red-700 mt-1">-{formatXPF(totalDec)}</p>
        </div>
      </div>

      {/* Formulaire */}
      {showForm && (
        <div className="bg-white rounded-xl border border-blue-200 p-5 shadow-sm mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-slate-900">Nouvel ajustement</h2>
            <button onClick={() => { setShowForm(false); resetForm() }} className="p-1 text-slate-400 hover:text-slate-600">
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Date</label>
              <input type="date" value={formDate} onChange={(e) => setFormDate(e.target.value)} className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Type</label>
              <select value={formDirection} onChange={(e) => setFormDirection(e.target.value as "encaissement" | "decaissement")} className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900 bg-white">
                <option value="encaissement">Encaissement (entrée)</option>
                <option value="decaissement">Décaissement (sortie)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Libellé</label>
              <input type="text" value={formLabel} onChange={(e) => setFormLabel(e.target.value)} placeholder="Ex: Subvention Pays" className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Catégorie</label>
              <select value={formCategory} onChange={(e) => setFormCategory(e.target.value)} className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900 bg-white">
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">Montant (XPF)</label>
              <input type="number" value={formAmount} onChange={(e) => setFormAmount(e.target.value)} min={1} placeholder="500000" className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900" />
            </div>
          </div>
          <div className="flex gap-3 mt-4 justify-end">
            <button onClick={() => { setShowForm(false); resetForm() }} className="px-4 py-2.5 text-sm font-medium text-slate-700 bg-slate-100 rounded-lg hover:bg-slate-200">Annuler</button>
            <button onClick={addAdjustment} className="px-4 py-2.5 text-sm font-medium text-white bg-emerald-600 rounded-lg hover:bg-emerald-700">Ajouter</button>
          </div>
        </div>
      )}

      {/* Liste */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
        {adjustments.length === 0 ? (
          <p className="text-center text-slate-500 py-12 text-sm">Aucun ajustement.</p>
        ) : (
          <div className="divide-y divide-slate-100">
            {adjustments.map((a) => (
              <div key={a.id} className="p-4 hover:bg-slate-50 transition-colors flex items-start gap-3">
                <div className={`mt-1.5 w-2.5 h-2.5 rounded-full shrink-0 ${a.direction === "encaissement" ? "bg-emerald-500" : "bg-red-500"}`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium text-slate-900 text-sm">{a.label}</span>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${a.direction === "encaissement" ? "bg-emerald-50 text-emerald-800" : "bg-red-50 text-red-800"}`}>
                      {a.direction === "encaissement" ? "Entrée" : "Sortie"}
                    </span>
                    <span className="px-2 py-0.5 bg-slate-100 rounded text-xs font-medium text-slate-700">{a.category}</span>
                  </div>
                  <div className="flex items-center gap-3 mt-1.5">
                    <span className="text-xs text-slate-600">{new Date(a.date).toLocaleDateString("fr-FR")}</span>
                    <span className={`font-bold text-sm ${a.direction === "encaissement" ? "text-emerald-700" : "text-red-700"}`}>
                      {a.direction === "encaissement" ? "+" : "-"}{formatXPF(a.amount)}
                    </span>
                  </div>
                </div>
                <button onClick={() => setDeleteTarget(a)} className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {deleteTarget && (
        <ConfirmModal
          title="Supprimer cet ajustement ?"
          message={`"${deleteTarget.label}" — ${formatXPF(deleteTarget.amount)}`}
          confirmLabel="Supprimer"
          danger
          onConfirm={confirmDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
      {ToastComponent}
    </div>
  )
}
