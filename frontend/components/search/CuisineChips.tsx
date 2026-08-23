"use client";
// components/search/CuisineChips.tsx — Task 8.8

import styles from "./CuisineChips.module.css";

const CUISINES = ["any", "north indian", "south indian", "chinese", "biryani", "mughlai", "fast food", "pizza", "continental"];

interface Props {
  value:    string;
  onChange: (v: string) => void;
}

export default function CuisineChips({ value, onChange }: Props) {
  return (
    <div className={styles.wrapper}>
      <label className={styles.label}>Cuisine</label>
      <div className={styles.chips} role="group" aria-label="Cuisine selection">
        {CUISINES.map(c => (
          <button
            key={c}
            className={`${styles.chip} ${value === c ? styles.active : ""}`}
            onClick={() => onChange(c)}
            aria-pressed={value === c}
          >
            {c === "any" ? "Any" : c.split(" ").map(w => w[0].toUpperCase() + w.slice(1)).join(" ")}
          </button>
        ))}
      </div>
    </div>
  );
}
