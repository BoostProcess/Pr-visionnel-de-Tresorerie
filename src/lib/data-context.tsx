"use client"

import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from "react"
import type { MonthForecast, KPIs, CompteResultat, BalanceAgeeLine, FluxTresorerie } from "./types"
import { demoForecasts, demoKPIs, demoCompteResultat, demoBalanceClients, demoBalanceFournisseurs, demoFluxTresorerie } from "./demo-data"
import { parseFECFile, type FECData } from "./fec-parser"

interface DataState {
  isDemo: boolean
  forecasts: Record<string, MonthForecast[]>
  kpis: KPIs
  compteResultat: CompteResultat
  balanceClients: BalanceAgeeLine[]
  balanceFournisseurs: BalanceAgeeLine[]
  fluxTresorerie: FluxTresorerie
  fecStats: { nbLignes: number; nbErreurs: number; erreurs: string[] } | null
  importFEC: (content: string, filename: string) => FECData
  reset: () => void
}

const DataContext = createContext<DataState | null>(null)

const STORAGE_KEY = "tresorerie_fec_data"

export function DataProvider({ children }: { children: ReactNode }) {
  const [isDemo, setIsDemo] = useState(true)
  const [forecasts, setForecasts] = useState<Record<string, MonthForecast[]>>(demoForecasts)
  const [kpis, setKpis] = useState<KPIs>(demoKPIs)
  const [compteResultat, setCompteResultat] = useState<CompteResultat>(demoCompteResultat)
  const [balanceClients, setBalanceClients] = useState<BalanceAgeeLine[]>(demoBalanceClients)
  const [balanceFournisseurs, setBalanceFournisseurs] = useState<BalanceAgeeLine[]>(demoBalanceFournisseurs)
  const [fluxTresorerie, setFluxTresorerie] = useState<FluxTresorerie>(demoFluxTresorerie)
  const [fecStats, setFecStats] = useState<DataState["fecStats"]>(null)

  // Charger depuis localStorage au montage
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const data = JSON.parse(stored) as Omit<DataState, "importFEC" | "reset">
        setIsDemo(false)
        setForecasts(data.forecasts)
        setKpis(data.kpis)
        setCompteResultat(data.compteResultat)
        setBalanceClients(data.balanceClients)
        setBalanceFournisseurs(data.balanceFournisseurs)
        setFluxTresorerie(data.fluxTresorerie)
        setFecStats(data.fecStats)
      }
    } catch {
      // localStorage indisponible ou données corrompues
    }
  }, [])

  const importFEC = useCallback((content: string, filename: string): FECData => {
    const data = parseFECFile(content)

    if (data.nbLignes > 0) {
      setIsDemo(false)
      setForecasts(data.forecasts)
      setKpis(data.kpis)
      setCompteResultat(data.compteResultat)
      setBalanceClients(data.balanceClients)
      setBalanceFournisseurs(data.balanceFournisseurs)
      setFluxTresorerie(data.fluxTresorerie)
      setFecStats({ nbLignes: data.nbLignes, nbErreurs: data.nbErreurs, erreurs: data.erreurs })

      // Persister dans localStorage
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
          isDemo: false,
          forecasts: data.forecasts,
          kpis: data.kpis,
          compteResultat: data.compteResultat,
          balanceClients: data.balanceClients,
          balanceFournisseurs: data.balanceFournisseurs,
          fluxTresorerie: data.fluxTresorerie,
          fecStats: { nbLignes: data.nbLignes, nbErreurs: data.nbErreurs, erreurs: data.erreurs },
        }))
      } catch {
        // localStorage plein
      }
    }

    return data
  }, [])

  const reset = useCallback(() => {
    setIsDemo(true)
    setForecasts(demoForecasts)
    setKpis(demoKPIs)
    setCompteResultat(demoCompteResultat)
    setBalanceClients(demoBalanceClients)
    setBalanceFournisseurs(demoBalanceFournisseurs)
    setFluxTresorerie(demoFluxTresorerie)
    setFecStats(null)
    try { localStorage.removeItem(STORAGE_KEY) } catch {}
  }, [])

  return (
    <DataContext.Provider value={{
      isDemo, forecasts, kpis, compteResultat,
      balanceClients, balanceFournisseurs, fluxTresorerie,
      fecStats, importFEC, reset,
    }}>
      {children}
    </DataContext.Provider>
  )
}

export function useData(): DataState {
  const ctx = useContext(DataContext)
  if (!ctx) throw new Error("useData must be used within DataProvider")
  return ctx
}
