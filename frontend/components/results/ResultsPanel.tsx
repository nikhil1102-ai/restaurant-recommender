"use client";
// components/results/ResultsPanel.tsx — Task 8.18

import AISummaryBanner from "./AISummaryBanner";
import RestaurantCard  from "./RestaurantCard";
import SkeletonCard    from "./SkeletonCard";
import styles from "./ResultsPanel.module.css";
import type { RecommendResponse } from "@/types/api";

interface Props {
  data:    RecommendResponse | null;
  loading: boolean;
  error:   string | null;
  onSave:  (name: string) => void;
  isSaved: (name: string) => boolean;
}

export default function ResultsPanel({ data, loading, error, onSave, isSaved }: Props) {
  return (
    <section className={`results-panel ${styles.panel} scroll`}>
      {/* Ambient glow */}
      <div className={styles.glow} aria-hidden="true" />

      {/* Loading skeletons */}
      {loading && (
        <div className={styles.list}>
          {[0, 1, 2].map(i => <SkeletonCard key={i} />)}
        </div>
      )}

      {/* Error state */}
      {!loading && error && (
        <div className={`anim-fade-in ${styles.error}`}>
          <span className="material-symbols-outlined" style={{ fontSize: 32, color: "var(--primary)" }}>
            error_outline
          </span>
          <p>{error}</p>
          {!error.includes("Sorry!") && (
            <p className={styles.errorHint}>
              Make sure the API server is running:<br />
              <code>uvicorn api.main:app --port 8000</code>
            </p>
          )}
        </div>
      )}

      {/* Results */}
      {!loading && data && (
        <>
          <AISummaryBanner summary={data.query_summary} considered={data.considered} />
          <div className={styles.list}>
            {data.restaurants.map((r, i) => (
              <RestaurantCard
                key={r.name}
                restaurant={r}
                onSave={onSave}
                isSaved={isSaved(r.name)}
                delay={i * 80}
              />
            ))}
          </div>
        </>
      )}

      {/* Empty state */}
      {!loading && !data && !error && (
        <div className={`anim-fade-in ${styles.empty}`}>
          <div className={styles.emptyIcon}>
            <span className="material-symbols-outlined" style={{ fontSize: 48, color: "var(--primary)" }}>
              restaurant
            </span>
          </div>
          <h2 className={styles.emptyTitle}>Discover your next meal</h2>
          <p className={styles.emptyBody}>
            Fill in your preferences and hit <strong>Get Recommendations</strong> to let
            the AI pick the best spots for you.
          </p>
        </div>
      )}
    </section>
  );
}
