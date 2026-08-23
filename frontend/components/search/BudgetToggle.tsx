"use client";
// components/search/BudgetToggle.tsx — Task 8.7

import styles from "./BudgetToggle.module.css";

interface Props {
  value:    "low" | "medium" | "high";
  onChange: (v: "low" | "medium" | "high") => void;
}

const OPTIONS: { value: "low" | "medium" | "high"; label: string; range: string }[] = [
  { value: "low",    label: "Low",    range: "Up to ₹500"     },
  { value: "medium", label: "Medium", range: "₹501 – ₹1,200"  },
  { value: "high",   label: "High",   range: "₹1,200+"        },
];

export default function BudgetToggle({ value, onChange }: Props) {
  const current = OPTIONS.find(o => o.value === value);
  return (
    <div className={styles.wrapper}>
      <div className={styles.labelRow}>
        <label className={styles.label}>Budget</label>
        <span className={styles.range}>{current?.range} for two</span>
      </div>
      <div className={styles.pill} role="group" aria-label="Budget selection">
        {OPTIONS.map(opt => (
          <button
            key={opt.value}
            className={`${styles.btn} ${value === opt.value ? styles.active : ""}`}
            onClick={() => onChange(opt.value)}
            aria-pressed={value === opt.value}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}
