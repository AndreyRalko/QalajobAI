import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { cookies } from "next/headers";

import "./globals.css";

import { LanguageProvider } from "@/context/LanguageContext";
import { AuthProvider } from "@/context/AuthContext";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "QalaJob AI",
  description: "AI-powered HR platform for students and employers",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const storedLocale = cookieStore.get("qalajob-locale")?.value || "kk";
  const lang = storedLocale === "ru" ? "ru" : storedLocale === "en" ? "en" : "kk";

  return (
    <html
      lang={lang}
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >

      <body
  className="
    min-h-full
    overflow-x-hidden
    bg-white
    text-black
    dark:bg-[#030712]
    text-white
    transition-colors
    duration-300
  "
>

        <LanguageProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </LanguageProvider>

      </body>

    </html>
  );
}