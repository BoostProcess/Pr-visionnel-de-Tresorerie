"use client"

import { useState } from "react"
import { AlertTriangle, CheckCircle, X } from "lucide-react"
import { useData } from "@/lib/data-context"

export function DemoBannerWrapper() {
  const { isDemo, fecStats } = useData()
  const [visible, setVisible] = useState(true)

  if (!visible) return null

  if (isDemo) {
    return (
      <div className="bg-amber-50 border-b border-amber-200 px-4 py-2.5 flex items-center gap-3">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
        <p className="text-xs sm:text-sm text-amber-800 flex-1">
          <strong>Mode démonstration</strong> — Importez votre FEC pour voir vos vraies données.
        </p>
        <button onClick={() => setVisible(false)} className="p-1 text-amber-600 hover:text-amber-800">
          <X className="w-4 h-4" />
        </button>
      </div>
    )
  }

  if (fecStats) {
    return (
      <div className="bg-emerald-50 border-b border-emerald-200 px-4 py-2.5 flex items-center gap-3">
        <CheckCircle className="w-4 h-4 text-emerald-600 shrink-0" />
        <p className="text-xs sm:text-sm text-emerald-800 flex-1">
          <strong>Données FEC chargées</strong> — {fecStats.nbLignes.toLocaleString("fr-FR")} écritures importées.
          {fecStats.nbErreurs > 0 && ` (${fecStats.nbErreurs} erreurs)`}
        </p>
        <button onClick={() => setVisible(false)} className="p-1 text-emerald-600 hover:text-emerald-800">
          <X className="w-4 h-4" />
        </button>
      </div>
    )
  }

  return null
}
