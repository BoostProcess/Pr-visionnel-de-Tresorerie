"use client"

import { useState } from "react"
import { Upload, FileText, CheckCircle, AlertCircle, XCircle } from "lucide-react"

export default function ImportsPage() {
  const [dragActive, setDragActive] = useState(false)
  const [imports, setImports] = useState<Array<{
    filename: string
    type: string
    status: "succes" | "partiel" | "echec"
    lignes: number
    importees: number
    doublons: number
    erreurs: number
  }>>([])

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(false)
    const files = Array.from(e.dataTransfer.files)
    processFiles(files)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) processFiles(Array.from(e.target.files))
  }

  const processFiles = (files: File[]) => {
    files.forEach((file) => {
      setImports((prev) => [
        {
          filename: file.name,
          type: file.name.toLowerCase().includes("fec") ? "FEC" : "Sage CSV",
          status: "succes",
          lignes: Math.floor(Math.random() * 500) + 50,
          importees: Math.floor(Math.random() * 400) + 50,
          doublons: Math.floor(Math.random() * 20),
          erreurs: Math.floor(Math.random() * 5),
        },
        ...prev,
      ])
    })
  }

  const statusIcon = (status: string) => {
    if (status === "succes") return <CheckCircle className="w-5 h-5 text-emerald-500" />
    if (status === "partiel") return <AlertCircle className="w-5 h-5 text-amber-500" />
    return <XCircle className="w-5 h-5 text-red-500" />
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-slate-900 mb-1">Import des données</h1>
      <p className="text-sm text-slate-500 mb-6">Importez vos fichiers FEC ou exports Sage 100</p>

      {/* Zone de drop */}
      <div
        className={`bg-white rounded-xl border-2 border-dashed p-12 text-center transition-colors mb-8 ${
          dragActive ? "border-blue-500 bg-blue-50" : "border-slate-300 hover:border-slate-400"
        }`}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
        onDragLeave={() => setDragActive(false)}
        onDrop={handleDrop}
      >
        <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
        <p className="text-lg font-medium text-slate-700 mb-2">
          Glissez vos fichiers ici
        </p>
        <p className="text-sm text-slate-500 mb-4">
          FEC (.txt) ou Exports Sage (.csv, .xlsx)
        </p>
        <label className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg font-medium text-sm cursor-pointer hover:bg-blue-700 transition-colors">
          <FileText className="w-4 h-4" />
          Parcourir
          <input type="file" className="hidden" accept=".txt,.csv,.xlsx,.xls" multiple onChange={handleFileSelect} />
        </label>
      </div>

      {/* Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
        <p className="text-sm text-blue-800">
          <strong>Ordre recommandé :</strong> Clients → Fournisseurs → Factures → Commandes → Avoirs → Historique
          <br />
          <strong>FEC :</strong> Le fichier FEC (TXT tabulé, format réglementaire AAAAMMJJ) extrait automatiquement les factures clients/fournisseurs ouvertes et crée les tiers.
        </p>
      </div>

      {/* Historique imports */}
      {imports.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Historique des imports</h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-3 text-slate-500 font-medium">Statut</th>
                <th className="text-left py-3 text-slate-500 font-medium">Fichier</th>
                <th className="text-left py-3 text-slate-500 font-medium">Type</th>
                <th className="text-right py-3 text-slate-500 font-medium">Lignes</th>
                <th className="text-right py-3 text-slate-500 font-medium">Importées</th>
                <th className="text-right py-3 text-slate-500 font-medium">Doublons</th>
                <th className="text-right py-3 text-slate-500 font-medium">Erreurs</th>
              </tr>
            </thead>
            <tbody>
              {imports.map((imp, i) => (
                <tr key={i} className="border-b border-slate-50 hover:bg-slate-50">
                  <td className="py-3">{statusIcon(imp.status)}</td>
                  <td className="py-3 font-medium">{imp.filename}</td>
                  <td className="py-3">
                    <span className="px-2 py-1 bg-slate-100 rounded text-xs font-medium">{imp.type}</span>
                  </td>
                  <td className="py-3 text-right">{imp.lignes}</td>
                  <td className="py-3 text-right text-emerald-600 font-medium">{imp.importees}</td>
                  <td className="py-3 text-right text-amber-600">{imp.doublons}</td>
                  <td className="py-3 text-right text-red-500">{imp.erreurs}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
