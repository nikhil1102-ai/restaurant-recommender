"use client";
// app/saved/page.tsx — Task 8.21

import { useSavedRestaurants } from "@/hooks/useSavedRestaurants";
import TopBar   from "@/components/layout/TopBar";
import Sidebar  from "@/components/layout/Sidebar";
import styles   from "./page.module.css";
import pageStyles from "../page.module.css";

export default function SavedPage() {
  const { saved, toggle } = useSavedRestaurants();
  const names = [...saved];

  return (
    <div className={pageStyles.shell}>
      <TopBar />
      <div className={`app-shell ${pageStyles.appShell}`}>
        <Sidebar />
        <main className={`scroll ${styles.main}`}>
          <h1 className={styles.heading}>Saved Restaurants</h1>
          {names.length === 0 ? (
            <div className={`anim-fade-in ${styles.empty}`}>
              <span className="material-symbols-outlined" style={{ fontSize: 48, color: "var(--primary)" }}>
                bookmark_border
              </span>
              <p>No saved restaurants yet.</p>
              <p className={styles.hint}>Hit the bookmark icon on any recommendation to save it here.</p>
            </div>
          ) : (
            <div className={styles.grid}>
              {names.map((name, i) => (
                <div key={name} className={`anim-fade-up ${styles.card}`} style={{ animationDelay: `${i * 60}ms` }}>
                  <div className={styles.cardName}>{name}</div>
                  <button
                    className={styles.remove}
                    onClick={() => toggle(name)}
                    aria-label={`Remove ${name} from saved`}
                  >
                    <span className="material-symbols-outlined icon-fill" style={{ color: "var(--primary)" }}>bookmark</span>
                  </button>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
