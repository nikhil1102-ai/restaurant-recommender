# main.py -- Phase 7: CLI Entry Point (Fallback)
# Orchestrates the full recommendation pipeline from the terminal.
# Run: python main.py
#
# Pipeline:
#   load_restaurants() -> get_user_preferences() -> filter_restaurants()
#       -> build_prompt() -> get_recommendations() -> display_recommendations()

import os
import sys

os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# Ensure project root is importable regardless of working directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.ingest          import load_restaurants
from src.input_handler   import get_user_preferences
from src.filter          import filter_restaurants
from src.prompt_builder  import build_prompt
from src.groq_client     import get_recommendations
from src.formatter       import display_recommendations


def main() -> None:
    """
    Task 7.7 -- CLI fallback entry point.
    Runs the full recommendation pipeline interactively in the terminal.
    """
    print("Loading restaurant data...")
    df = load_restaurants(use_cache=True)
    print(f"Loaded {len(df):,} restaurants.\n")

    # Collect and validate user preferences (Phase 3)
    prefs = get_user_preferences()

    # Filter candidates (Phase 4)
    candidates = filter_restaurants(df, prefs)
    if candidates.empty:
        # filter_restaurants() already prints the warning message
        return

    print(f"\nFound {len(candidates)} matching restaurants. Asking AI...\n")

    # Build prompt (Phase 5)
    system_prompt, user_prompt = build_prompt(prefs, candidates)

    # Call Groq LLM (Phase 6)
    response = get_recommendations(system_prompt, user_prompt)

    # Display results (Phase 7 — formatter)
    display_recommendations(response, prefs)


if __name__ == "__main__":
    main()
