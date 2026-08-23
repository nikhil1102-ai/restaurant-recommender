// lib/api.ts — Task 8.12
// Typed fetch wrapper for POST /api/recommend.
// Uses Next.js rewrite proxy so no CORS header required.

import type { RecommendRequest, RecommendResponse } from "@/types/api";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

export async function recommend(req: RecommendRequest): Promise<RecommendResponse> {
  const res = await fetch("/api/recommend", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(req),
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch { /* ignore parse errors */ }
    throw new ApiError(res.status, detail);
  }

  return res.json() as Promise<RecommendResponse>;
}

export async function fetchLocations(): Promise<string[]> {
  const res = await fetch("/api/locations");
  if (!res.ok) return [];
  const data = await res.json() as { locations: string[] };
  return data.locations;
}

