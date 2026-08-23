# src/formatter.py -- Phase 7: CLI Display Formatter
# Renders the raw LLM response text as a clean, structured terminal output.
# Kept ASCII-safe for Windows CP1252 terminals; emoji are avoided in print()
# to prevent UnicodeEncodeError.  The LLM response itself is written via
# sys.stdout.buffer so any Unicode in the text is preserved.

import sys
import os

os.environ.setdefault("PYTHONIOENCODING", "utf-8")


# ---------------------------------------------------------------------------
# Task 7.6 -- CLI display function
# ---------------------------------------------------------------------------

def display_recommendations(response_text: str, prefs: dict) -> None:
    """
    Print the LLM recommendation response in a formatted CLI box.

    Args:
        response_text: Raw text returned by get_recommendations() (may be None).
        prefs:         User preferences dict (location, cuisine, budget, min_rating).
    """
    border = "=" * 58

    print("\n" + border)
    print("   [ TableMate AI ]  Restaurant Recommendations")
    print(border)
    print(
        f"  Location : {prefs['location'].title():<18} "
        f"Cuisine : {prefs['cuisine'].title()}"
    )
    print(
        f"  Budget   : {prefs['budget'].title():<18} "
        f"Min Rating: {prefs['min_rating']}+"
    )
    if prefs.get("extra_prefs"):
        print(f"  Notes    : {prefs['extra_prefs']}")
    print(border + "\n")

    if response_text:
        # Write via buffer to safely handle any Unicode in the LLM response
        sys.stdout.buffer.write(response_text.encode("utf-8"))
        sys.stdout.buffer.write(b"\n")
        sys.stdout.buffer.flush()
    else:
        print("[WARNING] Could not generate recommendations. Please try again.")

    print("\n" + border)


# ---------------------------------------------------------------------------
# Smoke-test (run: python src/formatter.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sample_prefs = {
        "location":    "banashankari",
        "cuisine":     "north indian",
        "budget":      "medium",
        "min_rating":  3.5,
        "extra_prefs": "family-friendly",
    }
    sample_response = (
        "#1. Peppy Peppers\n"
        "A North-Indian spot within the medium budget. "
        "4.2 stars and family-friendly seating make it a top pick.\n\n"
        "#2. Jalsa\n"
        "Cozy Mughlai-North-Indian eatery, Rs.800 for two, 4.1 stars.\n"
    )

    print("[TEST] display_recommendations with valid response_text:")
    display_recommendations(sample_response, sample_prefs)

    print("\n[TEST] display_recommendations with None response_text:")
    display_recommendations(None, sample_prefs)

    print("\n[PASS] formatter.py smoke-test PASSED.")
