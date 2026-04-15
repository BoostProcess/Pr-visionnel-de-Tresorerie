import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatXPF(amount: number): string {
  if (amount < 0) return `-${Math.abs(amount).toLocaleString("fr-FR")} F`
  return `${amount.toLocaleString("fr-FR")} F`
}

export function formatMonth(dateStr: string): string {
  const months = [
    "Janvier","Février","Mars","Avril","Mai","Juin",
    "Juillet","Août","Septembre","Octobre","Novembre","Décembre",
  ]
  const [year, month] = dateStr.split("-")
  return `${months[parseInt(month) - 1]} ${year}`
}
