import { cn, formatXPF } from "@/lib/utils"

interface KPICardProps {
  label: string
  value: number
  format?: "xpf" | "percent" | "days" | "raw"
  delta?: string
  trend?: "up" | "down" | "neutral"
  className?: string
}

export function KPICard({ label, value, format = "xpf", delta, trend, className }: KPICardProps) {
  const formattedValue =
    format === "xpf" ? formatXPF(value) :
    format === "percent" ? `${value}%` :
    format === "days" ? `${value} jours` :
    value.toLocaleString("fr-FR")

  return (
    <div className={cn("bg-white rounded-xl border border-slate-200 p-3 sm:p-5 shadow-sm", className)}>
      <p className="text-xs sm:text-sm text-slate-500 font-medium truncate">{label}</p>
      <p className={cn(
        "text-base sm:text-2xl font-bold mt-1 truncate",
        value < 0 ? "text-red-600" : "text-slate-900"
      )}>
        {formattedValue}
      </p>
      {delta && (
        <p className={cn(
          "text-xs mt-1 font-medium",
          trend === "up" ? "text-emerald-600" : trend === "down" ? "text-red-500" : "text-slate-400"
        )}>
          {delta}
        </p>
      )}
    </div>
  )
}
