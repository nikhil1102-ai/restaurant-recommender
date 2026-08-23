"use client";
// hooks/useRecommendations.ts — Task 8.13

import { useState, useCallback } from "react";
import { recommend, ApiError }   from "@/lib/api";
import type { RecommendRequest, RecommendResponse } from "@/types/api";

interface State {
  data:    RecommendResponse | null;
  loading: boolean;
  error:   string | null;
}

export function useRecommendations() {
  const [state, setState] = useState<State>({ data: null, loading: false, error: null });

  const fetchRecommendations = useCallback(async (req: RecommendRequest) => {
    setState({ data: null, loading: true, error: null });
    try {
      const data = await recommend(req);
      setState({ data, loading: false, error: null });
    } catch (err) {
      const msg = err instanceof ApiError
        ? err.message
        : err instanceof Error
          ? err.message
          : "Unknown error";
      setState({ data: null, loading: false, error: msg });
    }
  }, []);

  return { ...state, fetchRecommendations };
}
