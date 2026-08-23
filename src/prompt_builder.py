# src/prompt_builder.py -- Phase 5: Prompt Builder
# Transforms filtered restaurant data + user preferences into a structured
# (system_prompt, user_prompt) tuple ready for the Groq LLM API.

import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import sys
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import BUDGET_TIERS


# ---------------------------------------------------------------------------
# Task 5.1 -- SYSTEM_PROMPT: Expert recommender persona
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are TableMate AI, an expert restaurant recommendation assistant \
specializing in Indian dining.

Your task:
  1. Analyze the list of candidate restaurants provided.
  2. Consider the user's stated preferences (location, cuisine, budget, rating, extras).
  3. Select and RANK the top 3-5 restaurants that best match those preferences.

For each recommended restaurant, provide:
  - Rank number and restaurant name (e.g., "#1 MTR - Mavalli Tiffin Room")
  - A concise explanation (2-3 sentences) of WHY it suits this user specifically.
    Reference the cuisine type, cost value, rating, and any extra preferences.

Rules:
  - Be specific and conversational — avoid generic praise like "great food".
  - If fewer than 3 strong matches exist, recommend only those that genuinely fit.
  - Output ONLY the ranked list. Do not add preamble or closing remarks.
  - Use this exact format for each entry:

    #[rank]. [Restaurant Name]
    [Explanation sentence 1.] [Explanation sentence 2.] [Optional sentence 3.]
"""


# ---------------------------------------------------------------------------
# Task 5.2 -- Format each restaurant as a numbered entry
# ---------------------------------------------------------------------------

def format_restaurant_list(df: pd.DataFrame) -> str:
    """
    Convert the candidates DataFrame into a readable numbered list for the LLM.

    Each entry shows: rank, name, cuisine, cost, rating, votes,
    and optionally online order / table booking availability.
    """
    lines = []
    for i, row in df.iterrows():
        # Core fields (always present after Phase 2 cleaning)
        name    = row.get("name",     "Unknown")
        cuisine = row.get("cuisines", "—")
        cost    = row.get("cost",     0)
        rating  = row.get("rating",   "N/A")
        votes   = int(row.get("votes", 0))

        # Optional convenience fields
        online  = row.get("online_order", "")
        booking = row.get("book_table",   "")

        extras = []
        if str(online).strip().lower()  == "yes":
            extras.append("online order available")
        if str(booking).strip().lower() == "yes":
            extras.append("table booking available")
        extras_str = f"  | {', '.join(extras)}" if extras else ""

        lines.append(
            f"[{i + 1}] {name}\n"
            f"    Cuisine : {cuisine}\n"
            f"    Cost    : Rs.{int(cost)} for two\n"
            f"    Rating  : {rating} stars ({votes:,} votes){extras_str}\n"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Task 5.4 helper -- Human-readable budget range string
# ---------------------------------------------------------------------------

def get_budget_range(tier: str) -> str:
    """Return a human-readable budget range string for the given tier."""
    ranges = {
        "low":    "up to Rs.500",
        "medium": "Rs.501 - Rs.1,200",
        "high":   "Rs.1,200+",
    }
    return ranges.get(tier.lower(), tier)


# ---------------------------------------------------------------------------
# Task 5.3 + 5.4 + 5.5 -- Build the full (system, user) prompt tuple
# ---------------------------------------------------------------------------

def build_prompt(prefs: dict, candidates: pd.DataFrame) -> tuple[str, str]:
    """
    Build the (system_prompt, user_prompt) tuple for the Groq API.

    Tasks covered:
      5.3  Embed user preferences + restaurant list into the user prompt.
      5.4  Instruct the LLM to output a ranked list with explanations.
      5.5  Return (SYSTEM_PROMPT, user_prompt) ready for Groq.

    Args:
        prefs:      Validated preferences dict (from Phase 3).
        candidates: Filtered DataFrame of top-K restaurants (from Phase 4).

    Returns:
        Tuple of (system_prompt: str, user_prompt: str).

    Raises:
        ValueError: if candidates DataFrame is empty.
    """
    if candidates.empty:
        raise ValueError("build_prompt() called with an empty candidates DataFrame.")

    restaurant_list = format_restaurant_list(candidates)

    user_prompt = f"""User Preferences:
  - Location     : {prefs['location'].title()}
  - Cuisine      : {prefs['cuisine'].title()}
  - Budget       : {prefs['budget'].title()} ({get_budget_range(prefs['budget'])})
  - Min Rating   : {prefs['min_rating']} stars or above
  - Extra Notes  : {prefs.get('extra_prefs') or 'None'}

Candidate Restaurants ({len(candidates)} options):
{restaurant_list}
Please rank the top 3-5 restaurants from this list and explain why each one \
suits the user's preferences."""

    return SYSTEM_PROMPT, user_prompt


# ---------------------------------------------------------------------------
# Smoke-test (run: python src/prompt_builder.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from src.ingest import load_restaurants
    from src.filter import filter_restaurants

    print("[TEST] Loading dataset from cache...")
    df = load_restaurants(use_cache=True)
    print(f"[OK] {len(df):,} restaurants loaded.\n")

    prefs = {
        "location":    "banashankari",
        "cuisine":     "north indian",
        "budget":      "medium",
        "min_rating":  3.5,
        "extra_prefs": "family-friendly",
    }

    print("[TEST] Filtering candidates...")
    candidates = filter_restaurants(df, prefs)
    print(f"[OK] {len(candidates)} candidates selected.\n")

    # --- Build prompt ---
    system_prompt, user_prompt = build_prompt(prefs, candidates)

    # --- Assertions ---
    assert isinstance(system_prompt, str) and len(system_prompt) > 0, \
        "system_prompt must be a non-empty string"
    assert isinstance(user_prompt, str) and len(user_prompt) > 0, \
        "user_prompt must be a non-empty string"

    # System prompt must contain persona + format rules
    assert "TableMate AI" in system_prompt,    "SYSTEM_PROMPT missing persona name"
    assert "#[rank]" in system_prompt,         "SYSTEM_PROMPT missing format template"

    # User prompt must embed all preferences
    assert prefs["location"].title() in user_prompt, "location missing from user_prompt"
    assert prefs["cuisine"].title()  in user_prompt, "cuisine missing from user_prompt"
    assert prefs["budget"].title()   in user_prompt, "budget missing from user_prompt"
    assert str(prefs["min_rating"])  in user_prompt, "min_rating missing from user_prompt"
    assert prefs["extra_prefs"]      in user_prompt, "extra_prefs missing from user_prompt"

    # Restaurant list must be present
    assert "Rs." in user_prompt, "cost formatting missing from user_prompt"
    assert "stars" in user_prompt, "rating label missing from user_prompt"

    print("=" * 60)
    print("SYSTEM PROMPT:")
    print("=" * 60)
    print(system_prompt)

    print("=" * 60)
    print("USER PROMPT:")
    print("=" * 60)
    print(user_prompt)

    print("[PASS] Phase 5 smoke-test PASSED.")
