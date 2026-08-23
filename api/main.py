# api/main.py -- Phase 7: FastAPI REST API Layer
#
# Tasks covered:
#   7.1  FastAPI app with CORS middleware
#   7.2  RecommendRequest Pydantic model (validates incoming JSON)
#   7.3  RecommendResponse / Restaurant Pydantic models (typed output)
#   7.4  /api/recommend handler wiring: ingest -> filter -> prompt -> Groq
#   7.5  parse_llm_response() — maps LLM ranked text to typed Restaurant array
#
# Run: uvicorn api.main:app --reload
# Test: curl -X POST http://localhost:8000/api/recommend \
#         -H "Content-Type: application/json" \
#         -d '{"location":"banashankari","cuisine":"north indian","budget":"medium","min_rating":3.5}'

import os
import re
import sys

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# Ensure project root is on sys.path so `src.*` and `config` are importable
# when uvicorn is launched from the project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.ingest        import load_restaurants
from src.filter        import filter_restaurants
from src.prompt_builder import build_prompt
from src.groq_client   import get_recommendations


# ---------------------------------------------------------------------------
# Task 7.1 — FastAPI app + CORS
# ---------------------------------------------------------------------------

app = FastAPI(
    title="TableMate AI API",
    version="1.0.0",
    description="AI-powered restaurant recommendation engine (Zomato × Groq).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins for local dev (file://, localhost:*)
    allow_credentials=False,      # Must be False when allow_origins=["*"]
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Load dataset once at startup (not per-request) — keeps latency low
# ---------------------------------------------------------------------------

print("[STARTUP] Loading restaurant dataset...")
_df = load_restaurants(use_cache=True)
print(f"[STARTUP] {len(_df):,} restaurants loaded and ready.")


# ---------------------------------------------------------------------------
# Task 7.2 — Request model
# ---------------------------------------------------------------------------

class RecommendRequest(BaseModel):
    """Validates JSON body sent by the frontend / cURL client."""
    location:    str   = Field(..., min_length=1, description="City or area (e.g. Banashankari)")
    cuisine:     str   = Field("any", description="Preferred cuisine, or 'any'")
    budget:      str   = Field(..., pattern=r"^(low|medium|high)$", description="low | medium | high")
    min_rating:  float = Field(3.5, ge=0.0, le=5.0, description="Minimum aggregate rating (0-5)")
    extra_prefs: Optional[str] = Field("", description="Free-text extra preferences")


# ---------------------------------------------------------------------------
# Task 7.3 — Response models
# ---------------------------------------------------------------------------

class Restaurant(BaseModel):
    """A single ranked restaurant returned by the API."""
    rank:       int
    name:       str
    cuisine:    str
    cost:       int
    rating:     float
    votes:      int
    location:   str
    ai_summary: str


class RecommendResponse(BaseModel):
    """Top-level API response envelope."""
    query_summary: str
    considered:    int
    restaurants:   List[Restaurant]


# ---------------------------------------------------------------------------
# Task 7.5 — LLM response parser
# ---------------------------------------------------------------------------

def parse_llm_response(raw: str, candidates) -> List[dict]:
    """
    Best-effort parser that maps the LLM's ranked free-text response back
    to structured candidate rows.

    Strategy:
      1. Try to find the restaurant's name (exact regex) anywhere in the raw
         LLM output and collect the surrounding snippet as the ai_summary.
      2. Fall back to a generic message if no match is found for a candidate.
      3. Limit to top-5 candidates to match the LLM's 3-5 recommendation rule.
    """
    results: List[dict] = []
    top5 = candidates.head(5)

    for _, row in top5.iterrows():
        name    = row["name"]
        pattern = re.compile(re.escape(name), re.IGNORECASE)

        # Walk through lines of the LLM response; collect the first matching
        # non-heading line (lines starting with '#' are rank headers).
        snippet = ""
        lines   = raw.split("\n")
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if pattern.search(stripped):
                # The explanation typically follows the header line
                if stripped.startswith("#"):
                    # Look ahead for the explanation paragraph
                    for next_line in lines[idx + 1:]:
                        next_stripped = next_line.strip()
                        if next_stripped and not next_stripped.startswith("#"):
                            snippet = next_stripped
                            break
                else:
                    snippet = stripped
                break

        results.append({
            "rank":       len(results) + 1,
            "name":       name,
            "cuisine":    row["cuisines"],
            "cost":       int(row["cost"]),
            "rating":     round(float(row["rating"]), 1),
            "votes":      int(row.get("votes", 0)),
            "location":   row["location"].title(),
            "ai_summary": snippet or "Highly rated match for your preferences.",
        })

    return results


# ---------------------------------------------------------------------------
# Task 7.4 — POST /api/recommend handler
# ---------------------------------------------------------------------------

@app.post(
    "/api/recommend",
    response_model=RecommendResponse,
    summary="Get AI-ranked restaurant recommendations",
    tags=["recommendations"],
)
def recommend(req: RecommendRequest) -> RecommendResponse:
    """
    Full pipeline:
      1. Filter restaurants from the pre-loaded DataFrame
      2. Build the (system, user) prompt
      3. Call Groq LLM
      4. Parse LLM response → typed Restaurant list
      5. Return RecommendResponse
    """
    prefs = req.model_dump()

    # Step 1 — Filter
    candidates = filter_restaurants(_df, prefs)
    if candidates.empty:
        raise HTTPException(
            status_code=404,
            detail="Sorry! currently there are no restaurants matching your query. please try later with another combination.",
        )

    # Step 2 — Build prompt
    system_prompt, user_prompt = build_prompt(prefs, candidates)

    # Step 3 — Call LLM
    raw = get_recommendations(system_prompt, user_prompt)
    if not raw:
        raise HTTPException(
            status_code=502,
            detail="The AI did not return a response. Please try again.",
        )

    # Step 4 — Parse
    restaurants = parse_llm_response(raw, candidates)

    # Step 5 — Return
    return RecommendResponse(
        query_summary=(
            f"{len(candidates)} restaurant(s) considered in "
            f"{req.location.title()} | {req.cuisine.title()} | {req.budget.title()} budget"
        ),
        considered=len(candidates),
        restaurants=restaurants,
    )


# ---------------------------------------------------------------------------
# Health-check endpoint (useful for frontend readiness probes)
# ---------------------------------------------------------------------------

@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "restaurants_loaded": len(_df)}


@app.get("/api/locations", tags=["recommendations"])
def get_locations():
    """Return sorted list of unique locations available in the dataset."""
    locations = (
        _df["location"]
        .dropna()
        .str.strip()
        .str.title()
        .unique()
        .tolist()
    )
    locations.sort()
    return {"locations": locations}

