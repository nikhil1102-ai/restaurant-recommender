// app/layout.tsx — Tasks 8.2 · 8.26

import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title:       "TableMate AI — Restaurant Recommendations",
  description: "AI-powered restaurant discovery using Zomato data and Groq LLM. Find the best spots near you — personalised by location, cuisine, budget, and rating.",
  keywords:    ["restaurant", "recommendation", "AI", "Zomato", "Bangalore", "food"],
  openGraph: {
    title:       "TableMate AI",
    description: "Discover your next great meal with AI-powered restaurant recommendations.",
    type:        "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Material Symbols icon font */}
        <link
          rel="preconnect"
          href="https://fonts.googleapis.com"
        />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
