"use client"

import { useState } from "react"
import { Upload, FileText, CheckCircle, AlertCircle, XCircle, Trash2, ArrowRight } from "lucide-react"

interface ImportEntry {
  id: number
  filename: string
  type: string
  status: "en_attente" | "succes" | "partiel" | "echec"
  validated: boolean
  lignes: number
  importees: number
  doublons: number
  erreurs: number
}

let nextId = 1

export default function ImportsPage() {
  const [dragActive, setDragActive] = useState(false)
  const [imports, setImports] = useState<ImportEntry[]>([])

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

  const processFiles = (files: File[]) => {
    files.forEach((file) => {
      const lignes = Math.floor(Math.random() * 500) + 50
      const importees = Math.floor(lignes * 0.85)
      const doublons = Math.floor(Math.random() * 20)
      const erreurs = Math.floor(Math.random() * 5)
      setImports((prev) => [
        {
          id: nextId++,
          filename: file.name,
          type: file.name.toLowerCase().includes("fec") ? "FEC" : "Sage CSV",
          status: "en_attente",
          validated: false,
          lignes,
          importees,
          doublons,
          erreurs,
        },
        ...prev,
      ])
    })
  }

  const removeImport = (id: number) => {
    setImports((prev) => prev.filter((imp) => imp.id !== id))
  }

  const validateImport = (id: number) => {
    setImports((prev) =>
      prev.map((imp) =>
        imp.id === id ? { ...imp, status: "succes" as const, validated: true } : imp
      )
    )
  }

  const validateAll = () => {
    setImports((prev) =>
      prev.map((imp) =>
        !imp.validated ? { ...imp, status: "succes" as const, validated: true } : imp
      )
    )
  }

  const statusIcon = (status: string) => {
    if (status === "succes") return <CheckCircle className="w-5 h-5 text-emerald-600" />
    if (status === "partiel") return <AlertCircle className="w-5 h-5 text-amber-600" />
    if (status === "en_attente") return <div className="w-5 h-5 rounded-full border-2 border-blue-400 border-t-transparent animate-spin" />
    return <XCircle className="w-5 h-5 text-red-600" />
  }

  const statusLabel = (status: string, validated: boolean) => {
    if (validated) return <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-1 rounded">Intégré</span>
    if (status === "en_attente") return <span className="text-xs font-medium text-blue-700 bg-blue-50 px-2 py-1 rounded">En attente</span>
    if (status === "partiel") return <span className="text-xs font-medium text-amber-700 bg-amber-50 px-2 py-1 rounded">Partiel</span>
    if (status === "echec") return <span className="text-xs font-medium text-red-700 bg-red-50 px-2 py-1 rounded">Échec</span>
    return <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-1 rounded">OK</span>
  }

  const pendingCount = imports.filter((imp) => !imp.validated).length

  return (
    <div>
      <h1 className="text-xl sm:text-2xl font-bold text-slate-900 mb-1">Import des données</h1>
      <p className="text-sm text-slate-600 mb-6">Importez vos fichiers FEC ou exports Sage 100</p>

      {/* Zone de drop */}
      <div
        className={`bg-white rounded-xl border-2 border-dashed p-8 sm:p-12 text-center transition-colors mb-6 ${
          dragActive ? "border-blue-500 bg-blue-50" : "border-slate-300 hover:border-slate-400"
        }`}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
      >
        <Upload className="w-10 h-10 text-slate-600 mx-auto mb-3" />
        <p className="text-base font-medium text-slate-800 mb-2">
          Glissez vos fichiers ici
        </p>
        <p className="text-sm text-slate-600 mb-4">
          FEC (.txt) ou Exports Sage (.csv, .xlsx)
        </p>
        <label className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg font-medium text-sm cursor-pointer hover:bg-blue-700 transition-colors">
          <FileText className="w-4 h-4" />
          Parcourir
          <input type="file" className="hidden" accept=".txt,.csv,.xlsx,.xls" multiple onChange={handleFileSelect} />
        </label>
      </div>

      {/* Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <p className="text-sm text-blue-900">
          <strong>Ordre recommandé :</strong> Clients → Fournisseurs → Factures → Commandes → Avoirs → Historique
        </p>
        <p className="text-sm text-blue-900 mt-1">
          <strong>FEC :</strong> Le fichier FEC extrait automatiquement les factures clients/fournisseurs ouvertes.
        </p>
      </div>

      {/* Fichiers importés */}
      {imports.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
          {/* Header avec bouton valider tout */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 sm:p-6 border-b border-slate-200">
            <h2 className="text-lg font-semibold text-slate-900">
              Fichiers importés ({imports.length})
            </h2>
            {pendingCount > 0 && (
              <button
                onClick={validateAll}
                className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 transition-colors self-start"
              >
                <ArrowRight className="w-4 h-4" />
                Valider et intégrer au Dashboard ({pendingCount})
              </button>
            )}
          </div>

          {/* Liste des imports */}
          <div className="divide-y divide-slate-100">
            {imports.map((imp) => (
              <div key={imp.id} className="p-4 sm:p-5 hover:bg-slate-50 transition-colors">
                {/* Ligne principale */}
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">{statusIcon(imp.status)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-slate-900 text-sm truncate">{imp.filename}</span>
                      <span className="px-2 py-0.5 bg-slate-100 rounded text-xs font-medium text-slate-700">{imp.type}</span>
                      {statusLabel(imp.status, imp.validated)}
                    </div>
                    {/* Détails chiffrés */}
                    <div className="flex gap-4 mt-2 text-xs">
                      <span className="text-slate-600">{imp.lignes} lignes</span>
                      <span className="text-emerald-700 font-medium">{imp.importees} importées</span>
                      {imp.doublons > 0 && <span className="text-amber-700">{imp.doublons} doublons</span>}
                      {imp.erreurs > 0 && <span className="text-red-700">{imp.erreurs} erreurs</span>}
                    </div>
                  </div>
                  {/* Actions */}
                  <div className="flex items-center gap-2 shrink-0">
                    {!imp.validated && (
                      <button
                        onClick={() => validateImport(imp.id)}
                        className="px-3 py-1.5 bg-emerald-600 text-white rounded-md text-xs font-medium hover:bg-emerald-700 transition-colors"
                      >
                        Valider
                      </button>
                    )}
                    <button
                      onClick={() => removeImport(imp.id)}
                      className="p-1.5 text-slate-600 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors"
                      title="Supprimer"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* État vide */}
      {imports.length === 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-8 text-center shadow-sm">
          <p className="text-slate-600 text-sm">Aucun fichier importé. Déposez un fichier ci-dessus pour commencer.</p>
        </div>
      )}
    </div>
  )
}
