"use client"

import { useState } from "react"
import { Upload, FileText, CheckCircle, AlertCircle, XCircle, Trash2, ArrowRight, Database } from "lucide-react"
import { useData } from "@/lib/data-context"
import { useToast } from "@/components/ui/toast"
import { ConfirmModal } from "@/components/ui/confirm-modal"
import { formatXPF } from "@/lib/utils"

interface ImportEntry {
  id: number
  filename: string
  type: "FEC" | "Sage CSV"
  status: "en_attente" | "succes" | "partiel" | "echec"
  validated: boolean
  lignes: number
  importees: number
  erreurs: number
  details: string[]
}

let nextId = 1

export default function ImportsPage() {
  const { isDemo, importFEC, reset, kpis } = useData()
  const { show: showToast, ToastComponent } = useToast()
  const [dragActive, setDragActive] = useState(false)
  const [imports, setImports] = useState<ImportEntry[]>([])
  const [deleteTarget, setDeleteTarget] = useState<ImportEntry | null>(null)
  const [processing, setProcessing] = useState(false)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(false)
    const files = Array.from(e.dataTransfer.files)
    processFiles(files)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      processFiles(Array.from(e.target.files))
      e.target.value = ""
    }
  }

  const processFiles = async (files: File[]) => {
    setProcessing(true)

    for (const file of files) {
      const isFEC = file.name.toLowerCase().endsWith(".txt") ||
        file.name.toLowerCase().includes("fec")

      if (isFEC) {
        try {
          const content = await file.text()
          const result = importFEC(content, file.name)

          setImports((prev) => [{
            id: nextId++,
            filename: file.name,
            type: "FEC",
            status: result.nbErreurs === 0 ? "succes" : result.nbLignes > 0 ? "partiel" : "echec",
            validated: result.nbLignes > 0,
            lignes: result.nbLignes,
            importees: result.nbLignes - result.nbErreurs,
            erreurs: result.nbErreurs,
            details: result.erreurs.slice(0, 10),
          }, ...prev])

          if (result.nbLignes > 0) {
            showToast(
              `FEC importé : ${result.nbLignes.toLocaleString("fr-FR")} écritures. Les données sont maintenant disponibles sur toutes les pages.`,
              "success"
            )
          } else {
            showToast("Erreur lors de l'import du FEC. Vérifiez le format du fichier.", "error")
          }
        } catch (err) {
          setImports((prev) => [{
            id: nextId++,
            filename: file.name,
            type: "FEC",
            status: "echec",
            validated: false,
            lignes: 0,
            importees: 0,
            erreurs: 1,
            details: [`Erreur de lecture : ${err instanceof Error ? err.message : "inconnu"}`],
          }, ...prev])
          showToast("Impossible de lire le fichier.", "error")
        }
      } else {
        // Fichier non-FEC (CSV/Excel) — pas encore traité
        setImports((prev) => [{
          id: nextId++,
          filename: file.name,
          type: "Sage CSV",
          status: "en_attente",
          validated: false,
          lignes: 0,
          importees: 0,
          erreurs: 0,
          details: ["Import CSV/Excel non encore implémenté. Utilisez le format FEC."],
        }, ...prev])
        showToast("Seul le format FEC (.txt) est traité pour le moment.", "info")
      }
    }
    setProcessing(false)
  }

  const removeImport = (id: number) => {
    setImports((prev) => prev.filter((imp) => imp.id !== id))
    setDeleteTarget(null)
  }

  const handleReset = () => {
    reset()
    setImports([])
    showToast("Données réinitialisées en mode démonstration.", "info")
  }

  const statusIcon = (status: string) => {
    if (status === "succes") return <CheckCircle className="w-5 h-5 text-emerald-600" />
    if (status === "partiel") return <AlertCircle className="w-5 h-5 text-amber-600" />
    if (status === "en_attente") return <div className="w-5 h-5 rounded-full border-2 border-slate-300" />
    return <XCircle className="w-5 h-5 text-red-600" />
  }

  const statusLabel = (entry: ImportEntry) => {
    if (entry.validated) return <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-1 rounded">Intégré</span>
    if (entry.status === "en_attente") return <span className="text-xs font-medium text-slate-600 bg-slate-100 px-2 py-1 rounded">Non traité</span>
    if (entry.status === "echec") return <span className="text-xs font-medium text-red-700 bg-red-50 px-2 py-1 rounded">Échec</span>
    return null
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Import des données</h1>
          <p className="text-sm text-slate-600 mt-1">Importez votre fichier FEC pour alimenter l&apos;application</p>
        </div>
        {!isDemo && (
          <button onClick={handleReset} className="flex items-center gap-2 px-4 py-2.5 bg-slate-200 text-slate-700 rounded-lg text-sm font-medium hover:bg-slate-300 transition-colors self-start">
            Réinitialiser (démo)
          </button>
        )}
      </div>

      {/* État actuel */}
      {!isDemo && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 mb-6 flex items-center gap-3">
          <Database className="w-5 h-5 text-emerald-600 shrink-0" />
          <div className="text-sm text-emerald-900">
            <strong>Données FEC actives</strong> — CA : {formatXPF(kpis.chiffre_affaires)} | Créances : {formatXPF(kpis.creances_clients)} | Dettes : {formatXPF(kpis.dettes_fournisseurs)}
          </div>
        </div>
      )}

      {/* Zone de drop */}
      <div
        className={`bg-white rounded-xl border-2 border-dashed p-8 sm:p-12 text-center transition-colors mb-6 ${
          dragActive ? "border-blue-500 bg-blue-50" : "border-slate-300 hover:border-slate-400"
        } ${processing ? "opacity-50 pointer-events-none" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
      >
        <Upload className="w-10 h-10 text-slate-600 mx-auto mb-3" />
        <p className="text-base font-medium text-slate-800 mb-2">
          {processing ? "Traitement en cours..." : "Glissez votre fichier FEC ici"}
        </p>
        <p className="text-sm text-slate-600 mb-4">
          Fichier TXT au format réglementaire (18 colonnes, séparateur TAB ou pipe)
        </p>
        <label className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg font-medium text-sm cursor-pointer hover:bg-blue-700 transition-colors">
          <FileText className="w-4 h-4" />
          Parcourir
          <input type="file" className="hidden" accept=".txt,.csv,.xlsx,.xls" multiple onChange={handleFileSelect} />
        </label>
      </div>

      {/* Format attendu */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-6">
        <p className="text-sm font-medium text-slate-800 mb-2">Format FEC attendu (18 colonnes) :</p>
        <p className="text-xs text-slate-600 font-mono break-all leading-relaxed">
          JournalCode | JournalLib | EcritureNum | EcritureDate | CompteNum | CompteLib | CompAuxNum | CompAuxLib | PieceRef | PieceDate | EcritureLib | Debit | Credit | EcritureLet | DateLet | ValidDate | Montantdevise | Idevise
        </p>
        <ul className="mt-2 text-xs text-slate-600 space-y-1">
          <li>Dates au format <strong>AAAAMMJJ</strong> (ex: 20260315)</li>
          <li>Montants avec <strong>virgule décimale</strong> (ex: 500000,00)</li>
          <li>Séparateur <strong>TAB</strong> ou <strong>pipe</strong> (|)</li>
        </ul>
      </div>

      {/* Historique imports */}
      {imports.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
          <div className="p-4 sm:p-6 border-b border-slate-200">
            <h2 className="text-lg font-semibold text-slate-900">Fichiers importés ({imports.length})</h2>
          </div>
          <div className="divide-y divide-slate-100">
            {imports.map((imp) => (
              <div key={imp.id} className="p-4 sm:p-5 hover:bg-slate-50 transition-colors">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">{statusIcon(imp.status)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-slate-900 text-sm">{imp.filename}</span>
                      <span className="px-2 py-0.5 bg-slate-100 rounded text-xs font-medium text-slate-700">{imp.type}</span>
                      {statusLabel(imp)}
                    </div>
                    <div className="flex gap-4 mt-2 text-xs">
                      {imp.lignes > 0 && <span className="text-slate-600">{imp.lignes.toLocaleString("fr-FR")} écritures</span>}
                      {imp.importees > 0 && <span className="text-emerald-700 font-medium">{imp.importees.toLocaleString("fr-FR")} intégrées</span>}
                      {imp.erreurs > 0 && <span className="text-red-700">{imp.erreurs} erreurs</span>}
                    </div>
                    {/* Détail des erreurs */}
                    {imp.details.length > 0 && imp.status !== "succes" && (
                      <div className="mt-2 bg-red-50 rounded p-2">
                        {imp.details.map((d, i) => (
                          <p key={i} className="text-xs text-red-800">{d}</p>
                        ))}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => setDeleteTarget(imp)}
                    className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors shrink-0"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {imports.length === 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-8 text-center shadow-sm">
          <p className="text-slate-600 text-sm">Aucun fichier importé. Déposez votre FEC ci-dessus.</p>
        </div>
      )}

      {deleteTarget && (
        <ConfirmModal
          title="Supprimer cet import ?"
          message={`"${deleteTarget.filename}" sera retiré de l'historique.`}
          confirmLabel="Supprimer"
          danger
          onConfirm={() => removeImport(deleteTarget.id)}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
      {ToastComponent}
    </div>
  )
}
