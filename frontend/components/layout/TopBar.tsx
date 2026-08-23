// components/layout/TopBar.tsx — Task 8.5

import styles from "./TopBar.module.css";

export default function TopBar() {
  return (
    <header className={`topbar ${styles.topbar}`}>
      <div className={styles.brand}>TableMate AI</div>

      <div className={styles.center}>
        <div className={styles.search}>
          <span className="material-symbols-outlined" style={{ fontSize: 18, color: "var(--on-surface-v)" }}>
            search
          </span>
          <input
            type="text"
            placeholder="Quick search…"
            className={styles.searchInput}
            aria-label="Quick search"
          />
        </div>
      </div>

      <div className={styles.right}>
        <span className={styles.stat}>9,565+ restaurants indexed</span>
        <div className={styles.avatar} aria-label="User profile">
          <span className="material-symbols-outlined icon-fill" style={{ fontSize: 20 }}>
            account_circle
          </span>
        </div>
      </div>
    </header>
  );
}
