# src/input_handler.py -- Phase 3: Input Handler
# Collects user preferences from the terminal (CLI), validates them,
# and returns a structured preferences dictionary ready for the filter engine.

import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import sys

# Resolve project root so config is importable when run directly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import BUDGET_TIERS

# ---------------------------------------------------------------------------
# Task 3.1 -- UserPreferences schema (typed dict for clarity)
# ---------------------------------------------------------------------------
# Keys returned by get_user_preferences():
#   location   : str   -- city / neighbourhood, lower-cased
#   cuisine    : str   -- preferred cuisine, lower-cased; "any" = no filter
#   budget     : str   -- "low" | "medium" | "high"
#   min_rating : float -- minimum acceptable rating, clamped 0.0-5.0
#   extra_prefs: str   -- free-text extra preferences (may be empty)


def _prompt(label: str, default: str = "") -> str:
    """Display a labelled prompt and return stripped input."""
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"{label}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        value = ""
    return value or default


# ---------------------------------------------------------------------------
# Task 3.7 -- Validation helpers
# ---------------------------------------------------------------------------

def _validate_budget(raw: str) -> str | None:
    """Return canonical budget tier or None if invalid."""
    normalized = raw.strip().lower()
    if normalized in BUDGET_TIERS:
        return normalized
    # Accept single-letter shortcuts: l -> low, m -> medium, h -> high
    shortcuts = {"l": "low", "m": "medium", "h": "high"}
    return shortcuts.get(normalized)


def _validate_rating(raw: str) -> float:
    """Parse and clamp a rating string to [0.0, 5.0]; default 3.5 on error."""
    try:
        value = float(raw)
        return max(0.0, min(5.0, value))
    except (ValueError, TypeError):
        return 3.5


# ---------------------------------------------------------------------------
# Task 3.2-3.7 -- Main interactive collection function
# ---------------------------------------------------------------------------

def get_user_preferences() -> dict:
    """
    Interactively collect and validate user preferences from the terminal.

    Tasks covered:
      3.2  Prompt for location (required, non-empty)
      3.3  Prompt for cuisine   (optional; default = "any")
      3.4  Prompt for budget    (validated: low / medium / high)
      3.5  Prompt for min_rating (float, clamped 0.0-5.0; default 3.5)
      3.6  Prompt for extra preferences (optional free text)
      3.7  Validate and sanitize all inputs; return clean dict

    Returns:
        dict with keys: location, cuisine, budget, min_rating, extra_prefs
    """
    print()
    print("=" * 55)
    print("   Welcome to the Zomato AI Recommender!")
    print("=" * 55)
    print()

    # ------------------------------------------------------------------
    # Task 3.2 -- Location (required)
    # ------------------------------------------------------------------
    location = _prompt("Location (e.g., Bangalore, BTM Layout)")
    while not location:
        print("   [!] Location cannot be empty. Please try again.")
        location = _prompt("Location")

    # ------------------------------------------------------------------
    # Task 3.3 -- Cuisine (optional)
    # ------------------------------------------------------------------
    cuisine_raw = _prompt("Preferred cuisine (press Enter for any)", default="any")
    cuisine = cuisine_raw.lower().strip() or "any"

    # ------------------------------------------------------------------
    # Task 3.4 -- Budget (validated loop)
    # ------------------------------------------------------------------
    valid_labels = " / ".join(BUDGET_TIERS.keys())
    budget_raw = _prompt(f"Budget [{valid_labels}]")
    budget = _validate_budget(budget_raw)
    while budget is None:
        print(f"   [!] Invalid budget. Choose from: {valid_labels}")
        budget_raw = _prompt(f"Budget [{valid_labels}]")
        budget = _validate_budget(budget_raw)

    # ------------------------------------------------------------------
    # Task 3.5 -- Minimum rating (float, clamped)
    # ------------------------------------------------------------------
    rating_raw = _prompt("Minimum rating (0.0 - 5.0)", default="3.5")
    min_rating = _validate_rating(rating_raw)
    if rating_raw and min_rating != float(rating_raw.strip()) if rating_raw.strip().replace(".", "", 1).isdigit() else False:
        print(f"   [i] Rating clamped to {min_rating}.")

    # ------------------------------------------------------------------
    # Task 3.6 -- Extra preferences (optional free text)
    # ------------------------------------------------------------------
    extra_prefs = _prompt("Any extra preferences? (e.g., family-friendly, rooftop)")

    # ------------------------------------------------------------------
    # Task 3.7 -- Build clean, sanitized preferences dict
    # ------------------------------------------------------------------
    prefs = {
        "location":    location.lower().strip(),
        "cuisine":     cuisine,
        "budget":      budget,
        "min_rating":  min_rating,
        "extra_prefs": extra_prefs.strip(),
    }

    # Summary echo
    print()
    print("-" * 55)
    print("  Your preferences:")
    print(f"    Location   : {prefs['location'].title()}")
    print(f"    Cuisine    : {prefs['cuisine'].title()}")
    print(f"    Budget     : {prefs['budget'].title()}")
    print(f"    Min Rating : {prefs['min_rating']} stars")
    if prefs["extra_prefs"]:
        print(f"    Extras     : {prefs['extra_prefs']}")
    print("-" * 55)
    print()

    return prefs


# ---------------------------------------------------------------------------
# Non-interactive helper (used by tests and the FastAPI layer)
# ---------------------------------------------------------------------------

def build_preferences(
    location: str,
    cuisine: str = "any",
    budget: str = "medium",
    min_rating: float = 3.5,
    extra_prefs: str = "",
) -> dict:
    """
    Build a validated preferences dict without prompting the user.
    Useful for unit tests and the FastAPI request handler.

    Raises:
        ValueError: if location is empty or budget is invalid.
    """
    if not location or not location.strip():
        raise ValueError("location must not be empty")

    validated_budget = _validate_budget(budget)
    if validated_budget is None:
        valid = " / ".join(BUDGET_TIERS.keys())
        raise ValueError(f"budget must be one of: {valid}")

    return {
        "location":    location.lower().strip(),
        "cuisine":     (cuisine or "any").lower().strip(),
        "budget":      validated_budget,
        "min_rating":  _validate_rating(str(min_rating)),
        "extra_prefs": (extra_prefs or "").strip(),
    }


# ---------------------------------------------------------------------------
# Smoke-test (run: python src/input_handler.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("[TEST] Running non-interactive smoke-test via build_preferences()...")

    # Valid inputs
    prefs = build_preferences(
        location="Bangalore",
        cuisine="north indian",
        budget="medium",
        min_rating=4.0,
        extra_prefs="family-friendly",
    )
    assert prefs["location"] == "bangalore",         "location normalisation failed"
    assert prefs["cuisine"]  == "north indian",      "cuisine normalisation failed"
    assert prefs["budget"]   == "medium",            "budget validation failed"
    assert prefs["min_rating"] == 4.0,               "rating parsing failed"
    assert prefs["extra_prefs"] == "family-friendly","extra_prefs failed"

    # Budget shortcut
    prefs2 = build_preferences(location="Mumbai", budget="h")
    assert prefs2["budget"] == "high", "budget shortcut 'h' -> 'high' failed"

    # Rating clamping
    prefs3 = build_preferences(location="Delhi", budget="low", min_rating=99.0)
    assert prefs3["min_rating"] == 5.0, "rating clamping to 5.0 failed"

    prefs4 = build_preferences(location="Chennai", budget="low", min_rating=-1.0)
    assert prefs4["min_rating"] == 0.0, "rating clamping to 0.0 failed"

    # Invalid location
    try:
        build_preferences(location="")
        raise AssertionError("Should have raised ValueError for empty location")
    except ValueError:
        pass

    # Invalid budget
    try:
        build_preferences(location="Pune", budget="rich")
        raise AssertionError("Should have raised ValueError for invalid budget")
    except ValueError:
        pass

    print("[PASS] Phase 3 smoke-test PASSED.")
    print()
    print("Keys returned:", list(prefs.keys()))
    print("Sample prefs :", prefs)
