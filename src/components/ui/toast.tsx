"use client"

import { useEffect, useState } from "react"
import { CheckCircle, AlertCircle, X } from "lucide-react"

interface ToastProps {
  message: string
  type?: "success" | "error" | "info"
  onClose: () => void
  duration?: number
}

export function Toast({ message, type = "success", onClose, duration = 3000 }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration)
    return () => clearTimeout(timer)
  }, [onClose, duration])

  const colors = {
    success: "bg-emerald-50 border-emerald-300 text-emerald-900",
    error: "bg-red-50 border-red-300 text-red-900",
    info: "bg-blue-50 border-blue-300 text-blue-900",
  }

  const icons = {
    success: <CheckCircle className="w-5 h-5 text-emerald-600" />,
    error: <AlertCircle className="w-5 h-5 text-red-600" />,
    info: <AlertCircle className="w-5 h-5 text-blue-600" />,
  }

  return (
    <div className={`fixed bottom-4 left-1/2 -translate-x-1/2 z-[100] flex items-center gap-3 px-4 py-3 rounded-lg border shadow-lg ${colors[type]}`}>
      {icons[type]}
      <span className="text-sm font-medium">{message}</span>
      <button onClick={onClose} className="p-0.5 hover:opacity-70">
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}

export function useToast() {
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" | "info" } | null>(null)

  const show = (message: string, type: "success" | "error" | "info" = "success") => {
    setToast({ message, type })
  }

  const hide = () => setToast(null)

  const ToastComponent = toast ? (
    <Toast message={toast.message} type={toast.type} onClose={hide} />
  ) : null

  return { show, ToastComponent }
}
