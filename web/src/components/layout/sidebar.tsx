"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Users,
  Upload,
  Settings,
  PenLine,
  Scale,
} from "lucide-react"
import { cn } from "@/lib/utils"

const navigation = [
  { name: "Synthèse", href: "/", icon: LayoutDashboard },
  { name: "Analyse financière", href: "/analyse", icon: BarChart3 },
  { name: "Balance âgée", href: "/balance-agee", icon: Scale },
  { name: "Encaissements", href: "/encaissements", icon: TrendingUp },
  { name: "Décaissements", href: "/decaissements", icon: TrendingDown },
  { name: "Hypothèses", href: "/hypotheses", icon: Settings },
  { name: "Imports", href: "/imports", icon: Upload },
  { name: "Ajustements", href: "/ajustements", icon: PenLine },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 text-white flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-700">
        <div className="w-9 h-9 rounded-lg bg-blue-500 flex items-center justify-center font-bold text-lg">
          T
        </div>
        <div>
          <h1 className="font-semibold text-sm leading-tight">Prévisionnel</h1>
          <p className="text-xs text-slate-400">Trésorerie XPF</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              )}
            >
              <item.icon className="w-5 h-5 shrink-0" />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-slate-700">
        <p className="text-xs text-slate-500">v2.0 — Sage 100 GC</p>
        <p className="text-xs text-slate-500">Devise : Franc Pacifique</p>
      </div>
    </aside>
  )
}
