import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "LunarMatch — Multi-Modal Lunar Image Registration Engine",
  description: "Pure monochrome aerospace research station for Chandrayaan-2 lunar image registration. ISRO Problem Statement 26166, Smart India Hackathon 2026.",
  icons: {
    icon: "/assets/icons/app_logo_64.png",
    apple: "/assets/icons/app_logo_128.png"
  }
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#000000",
  colorScheme: "dark"
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
