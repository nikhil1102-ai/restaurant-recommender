"use client";
// components/search/RatingSlider.tsx — Task 8.9

import styles from "./RatingSlider.module.css";

interface Props {
  value:    number;
  onChange: (v: number) => void;
}

export default function RatingSlider({ value, onChange }: Props) {
  const pct = (value / 5) * 100;
  const trackStyle = {
    background: `linear-gradient(to right, var(--primary) ${pct}%, var(--surface-highest) ${pct}%)`,
  };

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <label className={styles.label} htmlFor="rating-slider">Minimum Rating</label>
        <div className={styles.badge}>
          <span className="material-symbols-outlined icon-fill" style={{ fontSize: 14 }}>star</span>
          {value === 0 ? "Any" : `${value}+`}
        </div>
      </div>

      <input
        id="rating-slider"
        type="range"
        min={0} max={5} step={0.5}
        value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
        className={`rating-slider ${styles.slider}`}
        style={trackStyle}
        aria-label={`Minimum rating: ${value}`}
      />

      <div className={styles.ticks}>
        <span>Any</span>
        <span>4.5+</span>
      </div>
    </div>
  );
}
