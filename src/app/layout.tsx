import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/layout/sidebar";
import { DemoBanner } from "@/components/ui/demo-banner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Prévisionnel de Trésorerie",
  description: "Outil de prévision de trésorerie — Sage 100 GC — XPF",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" className="h-full">
      <body className={`${inter.className} h-full bg-slate-50 text-slate-900`}>
        <Sidebar />
        <main className="lg:ml-64 min-h-screen pt-14 lg:pt-0">
          <DemoBanner />
          <div className="p-4 lg:p-8 max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
