"use client";
// hooks/useSavedRestaurants.ts — Task 8.20
// Persists saved restaurant names to localStorage.

import { useState, useEffect, useCallback } from "react";

const STORAGE_KEY = "tablemate_saved";

export function useSavedRestaurants() {
  const [saved, setSaved] = useState<Set<string>>(new Set());

  // Hydrate from localStorage on mount (client only)
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setSaved(new Set(JSON.parse(raw) as string[]));
    } catch { /* ignore */ }
  }, []);

  const toggle = useCallback((name: string) => {
    setSaved(prev => {
      const next = new Set(prev);
      next.has(name) ? next.delete(name) : next.add(name);
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify([...next])); } catch { /* ignore */ }
      return next;
    });
  }, []);

  const isSaved = useCallback((name: string) => saved.has(name), [saved]);

  return { saved, toggle, isSaved };
}
