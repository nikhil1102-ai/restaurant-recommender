// components/results/AISummaryBanner.tsx — Task 8.17

import styles from "./AISummaryBanner.module.css";

interface Props {
  summary:    string;
  considered: number;
}

export default function AISummaryBanner({ summary, considered }: Props) {
  return (
    <div className={`anim-fade-in ${styles.banner}`}>
      <div className={styles.iconWrap}>
        <span className="material-symbols-outlined icon-fill" style={{ fontSize: 22, color: "var(--primary)" }}>
          auto_awesome
        </span>
      </div>
      <div>
        <p className={styles.summary}>{summary}</p>
        <p className={styles.considered}>
          Considered {considered} restaurant{considered !== 1 ? "s" : ""}
        </p>
      </div>
    </div>
  );
}
