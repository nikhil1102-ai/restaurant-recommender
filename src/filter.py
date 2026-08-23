# src/filter.py -- Phase 4: Data Filter Engine
# Applies user preferences as filters on the Pandas DataFrame and returns
# the top-K most relevant restaurant candidates for the LLM prompt.

import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import sys
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import TOP_K_FILTER


# ---------------------------------------------------------------------------
# Internal step-by-step filters (makes relaxation easy)
# ---------------------------------------------------------------------------

def _filter_location(df: pd.DataFrame, location: str) -> pd.DataFrame:
    """Task 4.1 -- Case-insensitive substring match on location."""
    return df[df["location"].str.contains(location.lower().strip(), na=False, regex=False)]


def _filter_cuisine(df: pd.DataFrame, cuisine: str) -> pd.DataFrame:
    """Task 4.2 -- Substring match on cuisines; skip entirely if 'any'."""
    if cuisine.lower().strip() == "any":
        return df
    return df[df["cuisines"].str.contains(cuisine.lower().strip(), na=False, regex=False)]


def _filter_budget(df: pd.DataFrame, budget: str) -> pd.DataFrame:
    """Task 4.3 -- Exact match on budget_tier column."""
    return df[df["budget_tier"] == budget.lower().strip()]


def _filter_rating(df: pd.DataFrame, min_rating: float) -> pd.DataFrame:
    """Task 4.4 -- Keep rows where rating >= min_rating."""
    return df[df["rating"] >= min_rating]


def _sort_and_cap(df: pd.DataFrame, k: int = TOP_K_FILTER) -> pd.DataFrame:
    """Tasks 4.5 + 4.6 -- Sort descending by rating then votes; return top-K."""
    sort_cols = [c for c in ["rating", "votes"] if c in df.columns]
    df = df.sort_values(sort_cols, ascending=[False] * len(sort_cols))
    return df.head(k).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Task 4.7 -- Progressive filter relaxation
# ---------------------------------------------------------------------------

def _relax_and_retry(df: pd.DataFrame, prefs: dict) -> pd.DataFrame:
    """
    When strict filtering yields no results, progressively relax constraints:
      1. Drop cuisine filter  (most selective — relax first)
      2. Drop rating filter   (may be too strict)
      3. Drop budget filter   (keep location — it's the anchor)
    Returns the best non-empty result found, or an empty DataFrame.
    """
    steps = [
        ("cuisine",    lambda d: _filter_cuisine(d, "any")),
        ("min_rating", lambda d: _filter_rating(d, 0.0)),
        ("budget",     lambda d: d),            # remove budget filter
    ]

    relaxed = df.copy()
    # Re-apply location (always required)
    relaxed = _filter_location(df, prefs["location"])

    for field, relax_fn in steps:
        # Re-apply all remaining strict filters except the one being relaxed
        candidate = relax_fn(relaxed)

        # Re-apply whichever strict filters haven't been relaxed yet
        if field != "cuisine":
            candidate = _filter_cuisine(candidate, prefs["cuisine"])
        if field != "min_rating":
            candidate = _filter_rating(candidate, prefs["min_rating"])
        if field != "budget":
            candidate = _filter_budget(candidate, prefs["budget"])

        if not candidate.empty:
            print(f"[INFO] Relaxed '{field}' filter -- found {len(candidate)} results.")
            return _sort_and_cap(candidate)

        # Each iteration, the current filter is permanently dropped
        relaxed = relax_fn(relaxed)

    return pd.DataFrame()   # nothing found even after full relaxation


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def filter_restaurants(df: pd.DataFrame, prefs: dict) -> pd.DataFrame:
    """
    Filter restaurants based on user preferences.

    Pipeline (Tasks 4.1 -> 4.6):
        location  --> cuisine  --> budget  --> rating  --> sort  --> top-K

    Task 4.7: If strict filtering yields no results, automatically relaxes
    filters in order: cuisine -> rating -> budget, logging each relaxation.

    Args:
        df:    Clean restaurant DataFrame from load_restaurants().
        prefs: Validated preferences dict from get_user_preferences() /
               build_preferences().

    Returns:
        DataFrame with <= TOP_K_FILTER rows, sorted by rating + votes.
        Empty DataFrame if no match even after relaxation.
    """
    if df.empty:
        print("[WARN] Input DataFrame is empty -- nothing to filter.")
        return pd.DataFrame()

    # --- Strict pipeline ---
    filtered = df.copy()

    # 4.1 Location
    filtered = _filter_location(filtered, prefs["location"])
    if filtered.empty:
        print(f"[WARN] No restaurants found in location: '{prefs['location']}'.")
        print("       Check the spelling or try a broader area name.")
        return pd.DataFrame()

    # 4.2 Cuisine
    filtered = _filter_cuisine(filtered, prefs["cuisine"])

    # 4.3 Budget
    filtered = _filter_budget(filtered, prefs["budget"])

    # 4.4 Rating
    filtered = _filter_rating(filtered, prefs["min_rating"])

    # 4.5 + 4.6 Sort & cap
    if not filtered.empty:
        return _sort_and_cap(filtered)

    # --- Task 4.7: Relax filters ---
    print("[WARN] No restaurants matched all criteria. Relaxing filters...")
    relaxed = _relax_and_retry(df, prefs)

    if relaxed.empty:
        print("[WARN] No restaurants found even after relaxing filters.")
        print("       Try a different location or broader budget.")

    return relaxed


# ---------------------------------------------------------------------------
# Debug helper: show which filter eliminated results
# ---------------------------------------------------------------------------

def diagnose_filters(df: pd.DataFrame, prefs: dict) -> None:
    """
    Print step-by-step row counts for each filter stage.
    Useful for debugging why a query returns no results.
    """
    print("\n[DIAGNOSE] Filter pipeline row counts:")
    print(f"  Total rows           : {len(df):>6}")

    after_loc = _filter_location(df, prefs["location"])
    print(f"  After location       : {len(after_loc):>6}  (location='{prefs['location']}')")

    after_cui = _filter_cuisine(after_loc, prefs["cuisine"])
    print(f"  After cuisine        : {len(after_cui):>6}  (cuisine='{prefs['cuisine']}')")

    after_bud = _filter_budget(after_cui, prefs["budget"])
    print(f"  After budget         : {len(after_bud):>6}  (budget='{prefs['budget']}')")

    after_rat = _filter_rating(after_bud, prefs["min_rating"])
    print(f"  After rating         : {len(after_rat):>6}  (min_rating={prefs['min_rating']})")

    after_top = _sort_and_cap(after_rat) if not after_rat.empty else after_rat
    print(f"  After top-{TOP_K_FILTER:<2}          : {len(after_top):>6}")
    print()


# ---------------------------------------------------------------------------
# Smoke-test (run: python src/filter.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from src.ingest import load_restaurants

    print("[TEST] Loading dataset from cache...")
    df = load_restaurants(use_cache=True)
    print(f"[OK] {len(df):,} restaurants loaded.\n")

    # --- Test 1: Normal query that should return results ---
    prefs1 = {
        "location":    "banashankari",
        "cuisine":     "north indian",
        "budget":      "medium",
        "min_rating":  3.5,
        "extra_prefs": "",
    }
    print("[TEST 1] Strict filter -- banashankari / north indian / medium / 3.5+")
    result1 = filter_restaurants(df, prefs1)
    print(f"  -> {len(result1)} results")
    if not result1.empty:
        print(result1[["name", "location", "cuisines", "rating", "budget_tier"]].to_string(index=False))
    assert not result1.empty, "Test 1 failed: expected results"
    assert len(result1) <= TOP_K_FILTER, "Test 1 failed: exceeded TOP_K_FILTER"
    assert result1["rating"].is_monotonic_decreasing or len(result1) == 1, \
        "Test 1 failed: results not sorted by rating"
    print()

    # --- Test 2: Cuisine = 'any' should skip cuisine filter ---
    prefs2 = {
        "location":    "banashankari",
        "cuisine":     "any",
        "budget":      "medium",
        "min_rating":  3.0,
        "extra_prefs": "",
    }
    print("[TEST 2] Cuisine='any' -- should skip cuisine filter")
    result2 = filter_restaurants(df, prefs2)
    print(f"  -> {len(result2)} results")
    assert not result2.empty, "Test 2 failed: expected results with cuisine='any'"
    print()

    # --- Test 3: Impossible query should trigger relaxation ---
    prefs3 = {
        "location":    "banashankari",
        "cuisine":     "japanese",
        "budget":      "high",
        "min_rating":  4.9,
        "extra_prefs": "",
    }
    print("[TEST 3] Impossible query -- should trigger filter relaxation")
    result3 = filter_restaurants(df, prefs3)
    print(f"  -> {len(result3)} results after relaxation")
    print()

    # --- Test 4: Bad location should return empty immediately ---
    prefs4 = {
        "location":    "zzznowherexxx",
        "cuisine":     "any",
        "budget":      "low",
        "min_rating":  0.0,
        "extra_prefs": "",
    }
    print("[TEST 4] Unknown location -- should return empty DataFrame")
    result4 = filter_restaurants(df, prefs4)
    assert result4.empty, "Test 4 failed: expected empty DataFrame for bad location"
    print(f"  -> correctly returned empty DataFrame")
    print()

    # --- Diagnose view ---
    diagnose_filters(df, prefs1)

    print("[PASS] Phase 4 smoke-test PASSED.")
