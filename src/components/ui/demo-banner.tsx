"use client"

import { useState } from "react"
import { AlertTriangle, X } from "lucide-react"

export function DemoBanner() {
  const [visible, setVisible] = useState(true)

  if (!visible) return null

  return (
    <div className="bg-amber-50 border-b border-amber-200 px-4 py-2.5 flex items-center gap-3">
      <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
      <p className="text-xs sm:text-sm text-amber-800 flex-1">
        <strong>Mode démonstration</strong> — Les données affichées sont fictives. Importez votre FEC pour voir vos vraies données.
      </p>
      <button onClick={() => setVisible(false)} className="p-1 text-amber-600 hover:text-amber-800">
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}
