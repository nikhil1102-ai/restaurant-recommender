"use client";
// app/page.tsx — Task 8.19
// Main Discover page — 3-column: Sidebar + SearchPanel + ResultsPanel

import TopBar       from "@/components/layout/TopBar";
import Sidebar      from "@/components/layout/Sidebar";
import SearchPanel  from "@/components/search/SearchPanel";
import ResultsPanel from "@/components/results/ResultsPanel";
import { useRecommendations }    from "@/hooks/useRecommendations";
import { useSavedRestaurants }   from "@/hooks/useSavedRestaurants";
import styles from "./page.module.css";

export default function DiscoverPage() {
  const { data, loading, error, fetchRecommendations } = useRecommendations();
  const { toggle, isSaved }                            = useSavedRestaurants();

  return (
    <div className={styles.shell}>
      <TopBar />
      <div className={`app-shell ${styles.appShell}`}>
        <Sidebar />
        <div className={`main-area ${styles.mainArea}`}>
          <SearchPanel onSearch={fetchRecommendations} loading={loading} />
          <ResultsPanel
            data={data}
            loading={loading}
            error={error}
            onSave={toggle}
            isSaved={isSaved}
          />
        </div>
      </div>
    </div>
  );
}
