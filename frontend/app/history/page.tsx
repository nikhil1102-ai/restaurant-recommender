"use client";
// app/history/page.tsx — Task 8.22

import TopBar  from "@/components/layout/TopBar";
import Sidebar from "@/components/layout/Sidebar";
import styles  from "./page.module.css";
import pageStyles from "../page.module.css";

// History is stored in localStorage by the SearchPanel on every search
const HISTORY_KEY = "tablemate_history";

export function recordSearch(query: string) {
  try {
    const raw   = localStorage.getItem(HISTORY_KEY);
    const items = raw ? (JSON.parse(raw) as string[]) : [];
    const next  = [query, ...items.filter(i => i !== query)].slice(0, 20);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(next));
  } catch { /* ignore */ }
}

export default function HistoryPage() {
  // Client-only read
  let items: string[] = [];
  if (typeof window !== "undefined") {
    try {
      const raw = localStorage.getItem(HISTORY_KEY);
      items = raw ? JSON.parse(raw) : [];
    } catch { /* ignore */ }
  }

  return (
    <div className={pageStyles.shell}>
      <TopBar />
      <div className={`app-shell ${pageStyles.appShell}`}>
        <Sidebar />
        <main className={`scroll ${styles.main}`}>
          <h1 className={styles.heading}>Search History</h1>
          {items.length === 0 ? (
            <div className={`anim-fade-in ${styles.empty}`}>
              <span className="material-symbols-outlined" style={{ fontSize: 48, color: "var(--primary)" }}>
                history
              </span>
              <p>No search history yet.</p>
              <p className={styles.hint}>Your recent searches will appear here.</p>
            </div>
          ) : (
            <div className={styles.list}>
              {items.map((item, i) => (
                <div key={i} className={`anim-fade-up ${styles.row}`} style={{ animationDelay: `${i * 40}ms` }}>
                  <span className="material-symbols-outlined" style={{ fontSize: 18, color: "var(--on-surface-v)" }}>
                    history
                  </span>
                  <span className={styles.query}>{item}</span>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
