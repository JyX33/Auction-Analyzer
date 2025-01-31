import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "WoW Auction Analyzer",
  description: "Compare item prices across realms",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" data-google-analytics-opt-out="">
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          <header className="border-b">
            <div className="container flex h-14 items-center">
              <div className="font-semibold">WoW Auction Analyzer</div>
            </div>
          </header>
          <main className="container py-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
