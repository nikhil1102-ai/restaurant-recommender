// components/results/SkeletonCard.tsx — Task 8.14

import styles from "./SkeletonCard.module.css";

export default function SkeletonCard() {
  return (
    <div className={styles.card} aria-hidden="true">
      <div className={`skeleton ${styles.image}`} />
      <div className={styles.body}>
        <div className={`skeleton ${styles.title}`} />
        <div className={`skeleton ${styles.sub}`}   />
        <div className={styles.lines}>
          <div className={`skeleton ${styles.line}`} />
          <div className={`skeleton ${styles.line}`} style={{ width: "80%" }} />
          <div className={`skeleton ${styles.line}`} style={{ width: "60%" }} />
        </div>
      </div>
    </div>
  );
}
