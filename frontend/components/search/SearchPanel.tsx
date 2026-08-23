"use client";
// components/search/SearchPanel.tsx — Task 8.10

import { useState } from "react";
import BudgetToggle    from "./BudgetToggle";
import CuisineChips    from "./CuisineChips";
import LocationSelect  from "./LocationSelect";
import { recordSearch } from "@/app/history/page";
import RatingSlider    from "./RatingSlider";
import styles from "./SearchPanel.module.css";
import type { RecommendRequest } from "@/types/api";

interface Props {
  onSearch: (req: RecommendRequest) => void;
  loading:  boolean;
}

export default function SearchPanel({ onSearch, loading }: Props) {
  const [location,   setLocation]   = useState("");
  const [cuisine,    setCuisine]    = useState("any");
  const [budget,     setBudget]     = useState<"low"|"medium"|"high">("medium");
  const [minRating,  setMinRating]  = useState(3.5);
  const [extraPrefs, setExtraPrefs] = useState("");
  const [error,      setError]      = useState("");

  function handleSubmit() {
    if (!location.trim()) { setError("Please enter a location."); return; }
    setError("");
    const summary = `${location.trim()} • ${cuisine} • ${budget} • ⭐${minRating}+`;
    recordSearch(summary);
    onSearch({ location: location.trim().toLowerCase(), cuisine, budget, min_rating: minRating, extra_prefs: extraPrefs });
  }

  return (
    <section className={`search-panel ${styles.panel} scroll`}>
      <h1 className={styles.heading}>What are you in the mood for?</h1>

      <div className={styles.fields}>
        {/* Location — Task 8.6 — real dataset dropdown */}
        <LocationSelect value={location} onChange={setLocation} />

        {/* Budget */}
        <BudgetToggle value={budget} onChange={setBudget} />

        {/* Cuisines */}
        <CuisineChips value={cuisine} onChange={setCuisine} />

        {/* Rating */}
        <RatingSlider value={minRating} onChange={setMinRating} />

        {/* Extra prefs */}
        <div className={styles.field}>
          <label className={styles.fieldLabel} htmlFor="extra-input">
            Extra Preferences <span className={styles.optional}>(optional)</span>
          </label>
          <input
            id="extra-input"
            type="text"
            placeholder="e.g. family-friendly, outdoor seating, rooftop"
            value={extraPrefs}
            onChange={e => setExtraPrefs(e.target.value)}
            className={styles.input}
            aria-label="Extra preferences"
          />
        </div>
      </div>

      <div className={styles.cta}>
        {error && <p className={styles.error}>{error}</p>}
        <button
          id="get-recommendations-btn"
          className={styles.btn}
          onClick={handleSubmit}
          disabled={loading}
          aria-busy={loading}
        >
          {loading
            ? <><span className={`material-symbols-outlined spin`} style={{ fontSize: 20 }}>progress_activity</span> Finding restaurants…</>
            : <><span className="material-symbols-outlined" style={{ fontSize: 20 }}>magic_button</span> Get Recommendations</>
          }
        </button>
      </div>
    </section>
  );
}
