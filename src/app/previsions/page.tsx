"use client"

import { useState } from "react"
import { Plus, Trash2, X, Building2, TrendingUp, TrendingDown } from "lucide-react"
import { formatXPF } from "@/lib/utils"
import { useToast } from "@/components/ui/toast"
import { ConfirmModal } from "@/components/ui/confirm-modal"

interface PrevisionMetier {
  id: number
  type: "encaissement" | "decaissement"
  categorie: string
  client_fournisseur: string
  affaire: string
  libelle: string
  montant: number
  mois_prevu: string
  fiabilite: "certain" | "probable" | "incertain"
  commentaire: string
}

const CATEGORIES_ENC = [
  "Situation de travaux à facturer",
  "Acompte à recevoir",
  "Retenue de garantie à récupérer",
  "Solde de marché / DGD",
  "Subvention à recevoir",
  "Cession d'actif",
  "Autre encaissement",
]

const CATEGORIES_DEC = [
  "Achat chantier à engager",
  "Sous-traitance à venir",
  "Investissement / CAPEX",
  "Prime exceptionnelle",
  "Solde de tout compte",
  "Nouveau financement",
  "Régularisation fiscale",
  "Autre décaissement",
]

const FIABILITE_LABELS = {
  certain: { label: "Certain", color: "bg-emerald-50 text-emerald-800" },
  probable: { label: "Probable", color: "bg-blue-50 text-blue-800" },
  incertain: { label: "Incertain", color: "bg-amber-50 text-amber-800" },
}

const initialPrevisions: PrevisionMetier[] = [
  {
    id: 1, type: "encaissement", categorie: "Situation de travaux à facturer",
    client_fournisseur: "SCI Mahina", affaire: "Chantier Mahina",
    libelle: "Situation n°3 - Lot gros œuvre", montant: 4500000,
    mois_prevu: "2026-06", fiabilite: "certain", commentaire: "Situation prête, envoi fin mai",
  },
  {
    id: 2, type: "encaissement", categorie: "Acompte à recevoir",
    client_fournisseur: "SA Tahiti Nui", affaire: "Rénovation hôtel",
    libelle: "Acompte 30% sur commande", montant: 3000000,
    mois_prevu: "2026-07", fiabilite: "probable", commentaire: "En attente validation devis",
  },
  {
    id: 3, type: "decaissement", categorie: "Sous-traitance à venir",
    client_fournisseur: "Matériaux du Pacifique", affaire: "Chantier Mahina",
    libelle: "Commande béton lot 2", montant: 2200000,
    mois_prevu: "2026-06", fiabilite: "certain", commentaire: "Commande confirmée",
  },
  {
    id: 4, type: "decaissement", categorie: "Investissement / CAPEX",
    client_fournisseur: "", affaire: "",
    libelle: "Remplacement pelleteuse", montant: 8500000,
    mois_prevu: "2026-09", fiabilite: "incertain", commentaire: "Devis en cours, décision en juin",
  },
]

let nextId = 20

export default function PrevisionsPage() {
  const [previsions, setPrevisions] = useState<PrevisionMetier[]>(initialPrevisions)
  const [showForm, setShowForm] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<PrevisionMetier | null>(null)
  const [filterType, setFilterType] = useState<"tous" | "encaissement" | "decaissement">("tous")
  const { show: showToast, ToastComponent } = useToast()

  // Form
  const [formType, setFormType] = useState<"encaissement" | "decaissement">("encaissement")
  const [formCategorie, setFormCategorie] = useState(CATEGORIES_ENC[0])
  const [formClient, setFormClient] = useState("")
  const [formAffaire, setFormAffaire] = useState("")
  const [formLibelle, setFormLibelle] = useState("")
  const [formMontant, setFormMontant] = useState("")
  const [formMois, setFormMois] = useState("")
  const [formFiabilite, setFormFiabilite] = useState<"certain" | "probable" | "incertain">("probable")
  const [formCommentaire, setFormCommentaire] = useState("")

  const resetForm = () => {
    setFormType("encaissement")
    setFormCategorie(CATEGORIES_ENC[0])
    setFormClient("")
    setFormAffaire("")
    setFormLibelle("")
    setFormMontant("")
    setFormMois("")
    setFormFiabilite("probable")
    setFormCommentaire("")
  }

  const addPrevision = () => {
    if (!formLibelle || !formMontant || !formMois || Number(formMontant) <= 0) {
      showToast("Veuillez remplir le libellé, le montant et le mois.", "error")
      return
    }
    setPrevisions((prev) => [{
      id: nextId++,
      type: formType,
      categorie: formCategorie,
      client_fournisseur: formClient,
      affaire: formAffaire,
      libelle: formLibelle,
      montant: Math.round(Number(formMontant)),
      mois_prevu: formMois,
      fiabilite: formFiabilite,
      commentaire: formCommentaire,
    }, ...prev])
    resetForm()
    setShowForm(false)
    showToast("Prévision ajoutée.", "success")
  }

  const confirmDelete = () => {
    if (!deleteTarget) return
    setPrevisions((prev) => prev.filter((p) => p.id !== deleteTarget.id))
    showToast("Prévision supprimée.", "success")
    setDeleteTarget(null)
  }

  const filtered = previsions.filter((p) => filterType === "tous" || p.type === filterType)
  const totalEnc = previsions.filter((p) => p.type === "encaissement").reduce((s, p) => s + p.montant, 0)
  const totalDec = previsions.filter((p) => p.type === "decaissement").reduce((s, p) => s + p.montant, 0)

  const categories = formType === "encaissement" ? CATEGORIES_ENC : CATEGORIES_DEC

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Prévisions métier</h1>
          <p className="text-sm text-slate-600 mt-1">Flux futurs non encore comptabilisés (Bloc 3 - Manuel)</p>
        </div>
        <button onClick={() => setShowForm(true)} className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors self-start">
          <Plus className="w-4 h-4" />
          Nouvelle prévision
        </button>
      </div>

      {/* Info */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-6">
        <p className="text-sm text-slate-700">
          <strong>Ce que la compta ne sait pas :</strong> situations de travaux à émettre, acomptes attendus, gros achats décidés, investissements prévus, variations de paie.
          Saisissez ici tout ce qui va impacter votre trésorerie et qui n&apos;est pas encore dans votre comptabilité.
        </p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <p className="text-xs text-slate-600 font-medium">Encaissements prévus</p>
          <p className="text-lg font-bold text-emerald-700 mt-1">+{formatXPF(totalEnc)}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <p className="text-xs text-slate-600 font-medium">Décaissements prévus</p>
          <p className="text-lg font-bold text-red-700 mt-1">-{formatXPF(totalDec)}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm col-span-2 sm:col-span-1">
          <p className="text-xs text-slate-600 font-medium">Impact net</p>
          <p className={`text-lg font-bold mt-1 ${totalEnc - totalDec >= 0 ? "text-emerald-700" : "text-red-700"}`}>
            {formatXPF(totalEnc - totalDec)}
          </p>
        </div>
      </div>

      {/* Filtres */}
      <div className="flex bg-white rounded-lg border border-slate-200 p-1 w-fit mb-6">
        {([["tous", "Tous"], ["encaissement", "Encaissements"], ["decaissement", "Décaissements"]] as const).map(([key, label]) => (
          <button key={key} onClick={() => setFilterType(key)}
            className={`px-3 py-2 rounded-md text-xs sm:text-sm font-medium transition-colors ${filterType === key ? "bg-blue-600 text-white" : "text-slate-600 hover:bg-slate-50"}`}>
            {label}
          </button>
        ))}
      </div>

      {/* Formulaire */}
      {showForm && (
        <div className="bg-white rounded-xl border border-blue-200 p-5 shadow-sm mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-slate-900">Nouvelle prévision</h2>
            <button onClick={() => { setShowForm(false); resetForm() }} className="p-1 text-slate-600 hover:text-slate-800"><X className="w-5 h-5" /></button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Type</label>
              <select value={formType} onChange={(e) => { setFormType(e.target.value as "encaissement" | "decaissement"); setFormCategorie(e.target.value === "encaissement" ? CATEGORIES_ENC[0] : CATEGORIES_DEC[0]) }}
                className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900 bg-white">
                <option value="encaissement">Encaissement (entrée)</option>
                <option value="decaissement">Décaissement (sortie)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Catégorie</label>
              <select value={formCategorie} onChange={(e) => setFormCategorie(e.target.value)}
                className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900 bg-white">
                {categories.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Client / Fournisseur</label>
              <input type="text" value={formClient} onChange={(e) => setFormClient(e.target.value)} placeholder="SCI Mahina" className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Affaire / Chantier</label>
              <input type="text" value={formAffaire} onChange={(e) => setFormAffaire(e.target.value)} placeholder="Chantier Mahina" className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Libellé</label>
              <input type="text" value={formLibelle} onChange={(e) => setFormLibelle(e.target.value)} placeholder="Situation n°3 gros œuvre" className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Montant (XPF)</label>
              <input type="number" value={formMontant} onChange={(e) => setFormMontant(e.target.value)} min={1} placeholder="4500000" className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Mois prévu</label>
              <input type="month" value={formMois} onChange={(e) => setFormMois(e.target.value)} className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Fiabilité</label>
              <select value={formFiabilite} onChange={(e) => setFormFiabilite(e.target.value as "certain" | "probable" | "incertain")}
                className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900 bg-white">
                <option value="certain">Certain</option>
                <option value="probable">Probable</option>
                <option value="incertain">Incertain</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Commentaire</label>
              <input type="text" value={formCommentaire} onChange={(e) => setFormCommentaire(e.target.value)} placeholder="Situation prête, envoi fin mai" className="w-full px-3 py-2.5 border border-slate-300 rounded-lg text-sm text-slate-900" />
            </div>
          </div>
          <div className="flex gap-3 mt-4 justify-end">
            <button onClick={() => { setShowForm(false); resetForm() }} className="px-4 py-2.5 text-sm font-medium text-slate-700 bg-slate-100 rounded-lg hover:bg-slate-200">Annuler</button>
            <button onClick={addPrevision} className="px-4 py-2.5 text-sm font-medium text-white bg-emerald-600 rounded-lg hover:bg-emerald-700">Ajouter</button>
          </div>
        </div>
      )}

      {/* Liste */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
        {filtered.length === 0 ? (
          <p className="text-center text-slate-600 py-12 text-sm">Aucune prévision métier.</p>
        ) : (
          <div className="divide-y divide-slate-100">
            {filtered.map((p) => (
              <div key={p.id} className="p-4 hover:bg-slate-50 transition-colors">
                <div className="flex items-start gap-3">
                  <div className="mt-1">
                    {p.type === "encaissement"
                      ? <TrendingUp className="w-5 h-5 text-emerald-600" />
                      : <TrendingDown className="w-5 h-5 text-red-600" />
                    }
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-slate-900 text-sm">{p.libelle}</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${FIABILITE_LABELS[p.fiabilite].color}`}>
                        {FIABILITE_LABELS[p.fiabilite].label}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-1 flex-wrap text-xs text-slate-600">
                      {p.client_fournisseur && <span className="font-medium">{p.client_fournisseur}</span>}
                      {p.affaire && <><span>•</span><span>{p.affaire}</span></>}
                      <span>•</span>
                      <span>{p.categorie}</span>
                      <span>•</span>
                      <span>{p.mois_prevu}</span>
                    </div>
                    {p.commentaire && <p className="text-xs text-slate-500 mt-1 italic">{p.commentaire}</p>}
                    <p className={`text-sm font-bold mt-1 ${p.type === "encaissement" ? "text-emerald-700" : "text-red-700"}`}>
                      {p.type === "encaissement" ? "+" : "-"}{formatXPF(p.montant)}
                    </p>
                  </div>
                  <button onClick={() => setDeleteTarget(p)} className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors shrink-0">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {deleteTarget && (
        <ConfirmModal title="Supprimer cette prévision ?" message={`"${deleteTarget.libelle}" — ${formatXPF(deleteTarget.montant)}`}
          confirmLabel="Supprimer" danger onConfirm={confirmDelete} onCancel={() => setDeleteTarget(null)} />
      )}
      {ToastComponent}
    </div>
  )
}
