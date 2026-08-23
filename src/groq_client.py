# src/groq_client.py -- Phase 6: Groq LLM Integration
# Sends the (system_prompt, user_prompt) tuple to Groq's API and returns
# the ranked recommendation text.  All six tasks from the implementation
# plan are covered here:
#
#   6.1  Load GROQ_API_KEY from .env
#   6.2  Instantiate Groq client
#   6.3  Build chat messages list ([system, user] roles)
#   6.4  Call client.chat.completions.create()
#   6.5  Extract response text
#   6.6  Handle API errors gracefully (rate limits, auth, timeouts, network)
#   6.7  Return raw LLM response string for the parser / formatter

import os
import time
import sys

# --- UTF-8 safe output on Windows terminals ---------------------------------
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# --- Ensure project root is on sys.path (so `config` is always importable) --
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from groq import Groq, APIConnectionError, APIStatusError, RateLimitError
from dotenv import load_dotenv
from config import GROQ_MODEL, GROQ_MAX_TOKENS, GROQ_TEMPERATURE

# ---------------------------------------------------------------------------
# Task 6.1 -- Load GROQ_API_KEY from .env
# ---------------------------------------------------------------------------
# load_dotenv() is idempotent; calling it at module import time means any
# module that imports groq_client automatically picks up the secret.
_dotenv_path = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(dotenv_path=_dotenv_path)

# Retry settings (Task 6.6)
_MAX_RETRIES = 3          # number of attempts on transient failures
_RETRY_DELAY = 2.0        # seconds to wait between retries (doubled each time)


# ---------------------------------------------------------------------------
# Task 6.2 -- Instantiate Groq client (lazy, once per call to keep it fresh)
# ---------------------------------------------------------------------------

def _build_client() -> Groq:
    """
    Create and return a Groq client using the API key loaded from .env.

    Raises:
        EnvironmentError: if GROQ_API_KEY is not set.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Add it to your .env file: GROQ_API_KEY=gsk_..."
        )
    return Groq(api_key=api_key)


# ---------------------------------------------------------------------------
# Tasks 6.3 + 6.4 + 6.5 + 6.6 + 6.7 -- Core recommendation function
# ---------------------------------------------------------------------------

def get_recommendations(system_prompt: str, user_prompt: str) -> str | None:
    """
    Send the constructed prompt to Groq and return the LLM's response text.

    Tasks covered:
      6.3  Builds the messages list with system + user roles.
      6.4  Calls client.chat.completions.create() with config from config.py.
      6.5  Extracts response.choices[0].message.content.
      6.6  Handles RateLimitError (with exponential back-off), auth errors,
           connection errors, and unexpected exceptions without crashing.
      6.7  Returns the raw response string for Phase 7 parser / CLI formatter.

    Args:
        system_prompt: The persona / instruction block (from Phase 5).
        user_prompt:   The user preferences + candidate list (from Phase 5).

    Returns:
        The LLM response text as a string, or None on unrecoverable failure.
    """
    # Task 6.3 -- Build messages list
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_prompt},
    ]

    client = _build_client()
    delay  = _RETRY_DELAY

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            # Task 6.4 -- Call the API
            response = client.chat.completions.create(
                model       = GROQ_MODEL,
                messages    = messages,
                max_tokens  = GROQ_MAX_TOKENS,
                temperature = GROQ_TEMPERATURE,
            )

            # Task 6.5 -- Extract and return the response text
            return response.choices[0].message.content

        # --- Task 6.6 : Targeted error handling ----------------------------

        except RateLimitError as e:
            # Groq free tier has per-minute token limits; back off and retry.
            if attempt < _MAX_RETRIES:
                print(
                    f"[RETRY] Groq rate limit hit (attempt {attempt}/{_MAX_RETRIES}). "
                    f"Retrying in {delay:.0f}s..."
                )
                time.sleep(delay)
                delay *= 2          # exponential back-off
            else:
                print(f"[ERROR] Groq rate limit exceeded after {_MAX_RETRIES} attempts: {e}")
                return None

        except APIStatusError as e:
            # 401 Unauthorized, 403 Forbidden, 404 model not found, etc.
            if e.status_code in (401, 403):
                print(
                    f"[ERROR] Groq authentication error ({e.status_code}): "
                    "Check your GROQ_API_KEY in .env."
                )
            else:
                print(f"[ERROR] Groq API error [{e.status_code}]: {e.message}")
            # Auth / model errors are not recoverable; do not retry.
            return None

        except APIConnectionError as e:
            # Network timeout, DNS failure, etc.
            if attempt < _MAX_RETRIES:
                print(
                    f"[RETRY] Connection error (attempt {attempt}/{_MAX_RETRIES}). "
                    f"Retrying in {delay:.0f}s... ({e})"
                )
                time.sleep(delay)
                delay *= 2
            else:
                print(f"[ERROR] Groq connection failed after {_MAX_RETRIES} attempts: {e}")
                return None

        except Exception as e:
            # Catch-all: surface the error but don't crash the caller.
            print(f"[ERROR] Unexpected error calling Groq API: {type(e).__name__}: {e}")
            return None

    # Should never reach here, but satisfy the type checker.
    return None


# ---------------------------------------------------------------------------
# Smoke-test (run: python src/groq_client.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from src.ingest       import load_restaurants
    from src.filter       import filter_restaurants
    from src.prompt_builder import build_prompt

    print("[TEST] Phase 6 smoke-test starting...\n")

    # --- 1. Load data -------------------------------------------------------
    print("[1/4] Loading restaurant dataset from cache...")
    df = load_restaurants(use_cache=True)
    print(f"      OK — {len(df):,} restaurants loaded.\n")

    # --- 2. Filter ----------------------------------------------------------
    prefs = {
        "location":    "banashankari",
        "cuisine":     "north indian",
        "budget":      "medium",
        "min_rating":  3.5,
        "extra_prefs": "family-friendly",
    }
    print("[2/4] Filtering candidates...")
    candidates = filter_restaurants(df, prefs)
    print(f"      OK — {len(candidates)} candidates selected.\n")

    if candidates.empty:
        print("[SKIP] No candidates found; cannot test LLM call. Try relaxing prefs.")
        sys.exit(0)

    # --- 3. Build prompt ----------------------------------------------------
    print("[3/4] Building prompt...")
    system_prompt, user_prompt = build_prompt(prefs, candidates)
    print("      OK — prompt built.\n")

    # --- 4. Call Groq -------------------------------------------------------
    print("[4/4] Calling Groq LLM...")
    response = get_recommendations(system_prompt, user_prompt)

    # --- Assertions ---------------------------------------------------------
    assert response is not None, "get_recommendations() returned None — check API key / network."
    assert isinstance(response, str), "Response must be a string."
    assert len(response.strip()) > 0, "Response must not be empty."

    print("\n" + "=" * 60)
    print("GROQ RESPONSE:")
    print("=" * 60)
    # Write the response in UTF-8 to handle non-ASCII chars on Windows terminals
    sys.stdout.buffer.write((response + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()
    print("=" * 60)
    print("\n[PASS] Phase 6 smoke-test PASSED.")
