// components/ui/RankBadge.tsx — Task 8.15

import styles from "./RankBadge.module.css";

interface Props { rating: number; }

export default function RankBadge({ rating }: Props) {
  return (
    <div className={styles.badge}>
      <span className="material-symbols-outlined icon-fill" style={{ fontSize: 13 }}>star</span>
      {rating.toFixed(1)}
    </div>
  );
}
