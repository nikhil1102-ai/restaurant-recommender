// types/api.ts — Task 8.11
// TypeScript contracts mirroring the FastAPI Pydantic models exactly.

export interface RecommendRequest {
  location:    string;
  cuisine:     string;
  budget:      "low" | "medium" | "high";
  min_rating:  number;
  extra_prefs: string;
}

export interface Restaurant {
  rank:       number;
  name:       string;
  cuisine:    string;
  cost:       number;
  rating:     number;
  votes:      number;
  location:   string;
  ai_summary: string;
}

export interface RecommendResponse {
  query_summary: string;
  considered:    number;
  restaurants:   Restaurant[];
}
