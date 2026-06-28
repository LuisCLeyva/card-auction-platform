import { Cinzel, Inter } from "next/font/google";
import type { Metadata } from "next";

import { AuthProvider } from "@/components/AuthProvider";
import { Navbar } from "@/components/Navbar";

import "./globals.css";

const body = Inter({ subsets: ["latin"], variable: "--font-body" });
const display = Cinzel({ subsets: ["latin"], weight: ["600", "700"], variable: "--font-display" });

export const metadata: Metadata = {
  title: "Card Auction House",
  description: "Buy, sell, and bid on trading cards.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${body.variable} ${display.variable} min-h-screen font-sans text-parchment`}>
        <AuthProvider>
          <Navbar />
          <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}
