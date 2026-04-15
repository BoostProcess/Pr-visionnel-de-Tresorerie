"use client"

import { useState } from "react"
import { Save, RotateCcw, Info } from "lucide-react"
import { useToast } from "@/components/ui/toast"

interface CompteMapping {
  id: string
  label: string
  description: string
  prefixes: string[]
  categorie: "tresorerie" | "encaissement" | "decaissement" | "bilan" | "resultat"
}

const DEFAULT_MAPPINGS: CompteMapping[] = [
  // Trésorerie
  { id: "banque", label: "Comptes bancaires", description: "Mouvements de trésorerie réels (relevés bancaires)", prefixes: ["512", "514"], categorie: "tresorerie" },
  { id: "caisse", label: "Caisse", description: "Espèces en caisse", prefixes: ["53"], categorie: "tresorerie" },
  // Encaissements
  { id: "clients", label: "Créances clients", description: "Factures émises et encaissements attendus", prefixes: ["411"], categorie: "encaissement" },
  { id: "ventes", label: "Chiffre d'affaires", description: "Produits des ventes de biens et services", prefixes: ["70"], categorie: "encaissement" },
  { id: "subventions", label: "Subventions", description: "Subventions d'exploitation reçues", prefixes: ["74"], categorie: "encaissement" },
  { id: "produits_financiers", label: "Produits financiers", description: "Intérêts reçus, dividendes", prefixes: ["76"], categorie: "encaissement" },
  // Décaissements
  { id: "fournisseurs", label: "Dettes fournisseurs", description: "Factures reçues et paiements à effectuer", prefixes: ["401"], categorie: "decaissement" },
  { id: "achats", label: "Achats", description: "Achats de marchandises et matières premières", prefixes: ["60"], categorie: "decaissement" },
  { id: "charges_ext", label: "Charges externes", description: "Loyers, sous-traitance, honoraires, télécom", prefixes: ["61", "62"], categorie: "decaissement" },
  { id: "impots_taxes", label: "Impôts et taxes", description: "Taxes locales, patentes, contributions", prefixes: ["63"], categorie: "decaissement" },
  { id: "salaires", label: "Salaires nets", description: "Rémunérations nettes versées aux salariés", prefixes: ["641"], categorie: "decaissement" },
  { id: "charges_sociales", label: "Charges sociales / CPS", description: "CPS, CST, cotisations sociales patronales", prefixes: ["645", "43"], categorie: "decaissement" },
  { id: "charges_fin", label: "Charges financières", description: "Intérêts d'emprunts, agios bancaires", prefixes: ["66"], categorie: "decaissement" },
  { id: "dotations", label: "Dotations amortissements", description: "Amortissements et provisions (non-cash mais impacte le résultat)", prefixes: ["68"], categorie: "decaissement" },
  // Bilan
  { id: "emprunts", label: "Emprunts", description: "Remboursements d'emprunts bancaires", prefixes: ["16"], categorie: "bilan" },
  { id: "capital", label: "Capital / Comptes courants", description: "Apports en capital, comptes courants associés", prefixes: ["10", "455"], categorie: "bilan" },
  { id: "stocks", label: "Stocks", description: "Variation des stocks de marchandises et matières", prefixes: ["3"], categorie: "bilan" },
  { id: "tva_collectee", label: "TVA collectée", description: "TVA facturée aux clients (à reverser)", prefixes: ["4457"], categorie: "bilan" },
  { id: "tva_deductible", label: "TVA déductible", description: "TVA sur achats (récupérable)", prefixes: ["4456"], categorie: "bilan" },
  { id: "personnel", label: "Personnel (dettes)", description: "Salaires à payer, congés payés", prefixes: ["421", "428"], categorie: "bilan" },
  { id: "immo", label: "Immobilisations", description: "Investissements (terrains, matériel, véhicules)", prefixes: ["2"], categorie: "bilan" },
]

const CATEGORIE_LABELS: Record<string, { label: string; color: string }> = {
  tresorerie: { label: "Trésorerie", color: "bg-blue-50 text-blue-800 border-blue-200" },
  encaissement: { label: "Encaissements", color: "bg-emerald-50 text-emerald-800 border-emerald-200" },
  decaissement: { label: "Décaissements", color: "bg-red-50 text-red-800 border-red-200" },
  bilan: { label: "Bilan / TVA", color: "bg-slate-50 text-slate-800 border-slate-200" },
  resultat: { label: "Résultat", color: "bg-amber-50 text-amber-800 border-amber-200" },
}

export default function ParametresPage() {
  const [mappings, setMappings] = useState<CompteMapping[]>(DEFAULT_MAPPINGS)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editValue, setEditValue] = useState("")
  const { show: showToast, ToastComponent } = useToast()

  const startEdit = (mapping: CompteMapping) => {
    setEditingId(mapping.id)
    setEditValue(mapping.prefixes.join(", "))
  }

  const saveEdit = (id: string) => {
    const newPrefixes = editValue
      .split(",")
      .map((p) => p.trim())
      .filter((p) => p.length > 0 && /^\d+$/.test(p))

    if (newPrefixes.length === 0) {
      showToast("Au moins un préfixe de compte est requis.", "error")
      return
    }

    setMappings((prev) =>
      prev.map((m) => m.id === id ? { ...m, prefixes: newPrefixes } : m)
    )
    setEditingId(null)
    showToast("Préfixe mis à jour.", "success")
  }

  const resetAll = () => {
    setMappings(DEFAULT_MAPPINGS)
    setEditingId(null)
    showToast("Paramètres réinitialisés aux valeurs par défaut.", "info")
  }

  // Grouper par catégorie
  const grouped = new Map<string, CompteMapping[]>()
  for (const m of mappings) {
    if (!grouped.has(m.categorie)) grouped.set(m.categorie, [])
    grouped.get(m.categorie)!.push(m)
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Paramètres comptables</h1>
          <p className="text-sm text-slate-600 mt-1">Association des comptes du plan comptable aux catégories de trésorerie</p>
        </div>
        <div className="flex gap-2 self-start">
          <button onClick={resetAll} className="flex items-center gap-2 px-4 py-2.5 bg-slate-100 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-200 transition-colors">
            <RotateCcw className="w-4 h-4" />
            Réinitialiser
          </button>
        </div>
      </div>

      {/* Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6 flex gap-3">
        <Info className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <div className="text-sm text-blue-900">
          <p className="font-medium mb-1">Comment ça fonctionne</p>
          <p>L&apos;application analyse chaque écriture de votre FEC en regardant les <strong>premiers chiffres</strong> du numéro de compte. Par exemple, un compte commençant par <code className="bg-blue-100 px-1 rounded">411</code> est automatiquement classé en &quot;Créances clients&quot;.</p>
          <p className="mt-1">Si votre plan comptable utilise des numéros différents, modifiez les préfixes ci-dessous. Séparez les préfixes par des virgules.</p>
        </div>
      </div>

      {/* Mappings par catégorie */}
      {["tresorerie", "encaissement", "decaissement", "bilan"].map((cat) => {
        const catMappings = grouped.get(cat) || []
        const catInfo = CATEGORIE_LABELS[cat]
        return (
          <div key={cat} className="mb-6">
            <div className={`px-4 py-2 rounded-t-xl border ${catInfo.color} font-semibold text-sm`}>
              {catInfo.label}
            </div>
            <div className="bg-white rounded-b-xl border border-t-0 border-slate-200 divide-y divide-slate-100">
              {catMappings.map((m) => (
                <div key={m.id} className="p-4 hover:bg-slate-50 transition-colors">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-slate-900 text-sm">{m.label}</div>
                      <div className="text-xs text-slate-600 mt-0.5">{m.description}</div>
                    </div>
                    <div className="flex items-center gap-2">
                      {editingId === m.id ? (
                        <>
                          <input
                            type="text"
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            className="w-40 sm:w-48 px-3 py-2 border border-blue-300 rounded-lg text-sm text-slate-900 bg-white focus:ring-2 focus:ring-blue-500"
                            placeholder="411, 4111"
                            onKeyDown={(e) => { if (e.key === "Enter") saveEdit(m.id); if (e.key === "Escape") setEditingId(null) }}
                            autoFocus
                          />
                          <button onClick={() => saveEdit(m.id)} className="px-3 py-2 bg-emerald-600 text-white rounded-lg text-xs font-medium hover:bg-emerald-700">
                            <Save className="w-3.5 h-3.5" />
                          </button>
                          <button onClick={() => setEditingId(null)} className="px-3 py-2 bg-slate-100 text-slate-600 rounded-lg text-xs font-medium hover:bg-slate-200">
                            Annuler
                          </button>
                        </>
                      ) : (
                        <>
                          <div className="flex gap-1 flex-wrap">
                            {m.prefixes.map((p) => (
                              <code key={p} className="px-2 py-1 bg-slate-100 rounded text-xs font-mono text-slate-800 border border-slate-200">
                                {p}xxx
                              </code>
                            ))}
                          </div>
                          <button onClick={() => startEdit(m)} className="px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                            Modifier
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )
      })}

      {/* Résumé des préfixes */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 sm:p-6 shadow-sm">
        <h2 className="text-base font-semibold text-slate-900 mb-3">Résumé des associations</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2 text-xs">
          {mappings.map((m) => (
            <div key={m.id} className="flex items-center justify-between py-1.5 px-2 rounded bg-slate-50">
              <span className="text-slate-700">{m.label}</span>
              <span className="font-mono text-slate-900">{m.prefixes.join(", ")}</span>
            </div>
          ))}
        </div>
      </div>

      {ToastComponent}
    </div>
  )
}
