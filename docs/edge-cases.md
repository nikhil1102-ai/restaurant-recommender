# Edge Cases & Handling Guide
## AI-Powered Restaurant Recommendation System (Zomato × Groq)

> **Based on:** [implementation-plan.md](./implementation-plan.md) · [architecture.md](./architecture.md)
> **Purpose:** Enumerate all anticipated edge cases per module, their root cause, impact, and recommended handling strategy.

---

## Table of Contents

1. [Data Ingestion Edge Cases](#1-data-ingestion-edge-cases)
2. [Input Handler Edge Cases](#2-input-handler-edge-cases)
3. [Data Filter Engine Edge Cases](#3-data-filter-engine-edge-cases)
4. [Prompt Builder Edge Cases](#4-prompt-builder-edge-cases)
5. [Groq LLM Integration Edge Cases](#5-groq-llm-integration-edge-cases)
6. [Response Parser / Output Formatter Edge Cases](#6-response-parser--output-formatter-edge-cases)
7. [System-Level / Cross-Cutting Edge Cases](#7-system-level--cross-cutting-edge-cases)
8. [Edge Case Test Matrix](#8-edge-case-test-matrix)

---

## 1. Data Ingestion Edge Cases

> **Module:** `src/ingest.py`

---

### EC-1.1 — Dataset Unavailable / Network Failure

| Field | Detail |
|---|---|
| **Trigger** | HuggingFace is unreachable, or dataset name changes |
| **Impact** | App crashes at startup with an unhandled `ConnectionError` |
| **Root Cause** | No internet connection or deprecated dataset path |
| **Handling** | Wrap `load_dataset()` in try/except; fall back to cached CSV if available |

```python
try:
    dataset = load_dataset(HF_DATASET_NAME, split=HF_DATASET_SPLIT)
except Exception as e:
    print(f"⚠️  Failed to load from HuggingFace: {e}")
    if os.path.exists("data/zomato_preprocessed.csv"):
        print("📦 Loading from local cache...")
        return pd.read_csv("data/zomato_preprocessed.csv")
    raise RuntimeError("No data source available. Check internet or cache.")
```

---

### EC-1.2 — Missing or Renamed Columns

| Field | Detail |
|---|---|
| **Trigger** | HuggingFace dataset schema updated; column names differ from expected |
| **Impact** | `KeyError` on column access; silent data loss |
| **Root Cause** | External dataset not under project control |
| **Handling** | Print available columns; validate before renaming |

```python
expected = ["name", "location", "cuisines", "approx_cost(for two people)", "aggregate rating"]
missing = [c for c in expected if c not in df.columns]
if missing:
    print(f"⚠️  Missing expected columns: {missing}")
    print(f"   Available columns: {df.columns.tolist()}")
```

---

### EC-1.3 — Cost Column Contains Non-Numeric Values

| Field | Detail |
|---|---|
| **Trigger** | Cost stored as `"1,200"`, `"N/A"`, `""`, or `"300-500"` |
| **Impact** | `pd.to_numeric()` fails; cost column becomes fully NaN |
| **Root Cause** | Inconsistent dataset formatting |
| **Handling** | Strip commas, remove non-numeric characters before conversion |

```python
df["cost"] = df["cost"].astype(str).str.replace(",", "").str.replace("[^0-9.]", "", regex=True)
df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
```

---

### EC-1.4 — Rating Stored as `"NEW"` or `"-"`

| Field | Detail |
|---|---|
| **Trigger** | Newly listed restaurants have no rating; stored as string `"NEW"` or `"-"` |
| **Impact** | `pd.to_numeric()` returns NaN; these rows are dropped |
| **Root Cause** | Zomato's own data format for new/unrated restaurants |
| **Handling** | Explicitly handle these strings before numeric conversion; either drop or assign `0.0` |

```python
df["rating"] = df["rating"].replace(["NEW", "-", ""], pd.NA)
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
# Choose: drop NaN ratings, or fill with 0.0 for unrated
df.dropna(subset=["rating"], inplace=True)
```

---

### EC-1.5 — Votes Column Is Zero or Missing

| Field | Detail |
|---|---|
| **Trigger** | Brand new restaurants with 0 votes or missing `votes` field |
| **Impact** | Sorting by votes fails or skews results toward unreviewed restaurants |
| **Root Cause** | Incomplete data for new listings |
| **Handling** | Fill `votes` NaN with `0`; factor into sort order without crashing |

```python
df["votes"] = pd.to_numeric(df.get("votes", 0), errors="coerce").fillna(0).astype(int)
```

---

### EC-1.6 — Entirely Empty DataFrame After Cleaning

| Field | Detail |
|---|---|
| **Trigger** | Every row has at least one null in critical columns |
| **Impact** | Empty DataFrame propagates through entire pipeline; crashes at filter stage |
| **Root Cause** | Aggressive `dropna()` combined with highly incomplete dataset |
| **Handling** | Check DataFrame length post-cleaning; raise descriptive error |

```python
if df.empty:
    raise ValueError("❌ Dataset is empty after cleaning. Check column mappings.")
print(f"✅ {len(df)} clean restaurants loaded.")
```

---

## 2. Input Handler Edge Cases

> **Module:** `src/input_handler.py`

---

### EC-2.1 — Empty Location Input

| Field | Detail |
|---|---|
| **Trigger** | User presses Enter without typing a location |
| **Impact** | Filter returns all records regardless of city → irrelevant results |
| **Root Cause** | No mandatory field enforcement |
| **Handling** | Loop until non-empty string provided |

```python
while not location.strip():
    location = input("   Location cannot be empty. Please enter a city: ").strip()
```

---

### EC-2.2 — Location Not in Dataset

| Field | Detail |
|---|---|
| **Trigger** | User types `"Tokyo"` or misspells `"Bangalor"` |
| **Impact** | Filter returns 0 results; LLM never gets called |
| **Root Cause** | Exact/substring match fails on typo or unknown city |
| **Handling** | Suggest closest valid location using fuzzy matching |

```python
from fuzzywuzzy import process

all_locations = df["location"].unique().tolist()
best_match, score = process.extractOne(user_input_location, all_locations)
if score < 70:
    print(f"⚠️  Location '{user_input_location}' not found in dataset.")
else:
    print(f"📍 Did you mean '{best_match}'? (matched {score}%)")
```

---

### EC-2.3 — Invalid Budget Tier Input

| Field | Detail |
|---|---|
| **Trigger** | User types `"cheap"`, `"₹500"`, `"medium-high"`, or gibberish |
| **Impact** | Budget filter fails or skips entirely |
| **Root Cause** | No strict input validation |
| **Handling** | Validation loop until one of `low`, `medium`, `high` is entered |

---

### EC-2.4 — Non-Numeric Rating Input

| Field | Detail |
|---|---|
| **Trigger** | User enters `"great"`, `"5 stars"`, or accidentally hits letters |
| **Impact** | `float()` conversion throws `ValueError` |
| **Root Cause** | No type-safe input parsing |
| **Handling** | Wrap in try/except; default to `3.5` with a notice |

```python
try:
    min_rating = float(input("⭐ Minimum rating (0.0 – 5.0): "))
    min_rating = max(0.0, min(5.0, min_rating))
except ValueError:
    print("   Invalid input. Defaulting to rating ≥ 3.5")
    min_rating = 3.5
```

---

### EC-2.5 — Rating Out of Valid Range

| Field | Detail |
|---|---|
| **Trigger** | User enters `-1`, `6`, or `100` |
| **Impact** | Filter with `>5.0` returns zero results; negative filter returns everything |
| **Root Cause** | No bounds enforcement |
| **Handling** | Clamp input: `min_rating = max(0.0, min(5.0, value))` |

---

### EC-2.6 — Special Characters / SQL-Injection-Like Input

| Field | Detail |
|---|---|
| **Trigger** | User enters `'; DROP TABLE --` or HTML/script tags |
| **Impact** | Could corrupt prompt string if passed raw to LLM |
| **Root Cause** | No input sanitization |
| **Handling** | Strip special characters from all text fields before use in prompt |

```python
import re
def sanitize(text: str) -> str:
    return re.sub(r"[^\w\s,.\-]", "", text).strip()
```

---

## 3. Data Filter Engine Edge Cases

> **Module:** `src/filter.py`

---

### EC-3.1 — Zero Results After All Filters Applied

| Field | Detail |
|---|---|
| **Trigger** | Highly specific combination: `"Mysore"` + `"Korean"` + `"low"` + `4.5+` |
| **Impact** | Empty candidates → no prompt built → no LLM call |
| **Root Cause** | Dataset may not contain restaurants matching all constraints |
| **Handling** | Progressive filter relaxation — drop filters one by one and retry |

```python
# Filter relaxation strategy
def filter_with_fallback(df, prefs):
    result = filter_restaurants(df, prefs)
    if result.empty:
        print("🔄 Relaxing cuisine filter...")
        prefs_relaxed = {**prefs, "cuisine": "any"}
        result = filter_restaurants(df, prefs_relaxed)
    if result.empty:
        print("🔄 Relaxing rating filter...")
        prefs_relaxed["min_rating"] = max(0.0, prefs["min_rating"] - 1.0)
        result = filter_restaurants(df, prefs_relaxed)
    return result
```

---

### EC-3.2 — Case Sensitivity Mismatch

| Field | Detail |
|---|---|
| **Trigger** | User types `"Bangalore"` but dataset stores `"bangalore"` or `"BANGALORE"` |
| **Impact** | Location filter returns 0 results |
| **Root Cause** | String comparison without normalization |
| **Handling** | Normalize both dataset and user input to lowercase at ingestion |

---

### EC-3.3 — Cuisine Substring Overlap

| Field | Detail |
|---|---|
| **Trigger** | User types `"Indian"` but filter also matches `"North Indian"`, `"South Indian"`, `"Indo-Chinese"` |
| **Impact** | Overly broad results mixed with correct results |
| **Root Cause** | `str.contains()` matches substrings |
| **Handling** | Acceptable behavior — note it as a feature; document it |

---

### EC-3.4 — Very Large Candidate Set (> TOP_K)

| Field | Detail |
|---|---|
| **Trigger** | Broad query: `"any"` cuisine in `"Bangalore"` + `"low"` budget |
| **Impact** | Hundreds of candidates → LLM context window overflow |
| **Root Cause** | No upper bound enforced before prompt building |
| **Handling** | Always `head(TOP_K_FILTER)` after sorting — hard cap at K=10 |

---

### EC-3.5 — All Restaurants Have Same Rating

| Field | Detail |
|---|---|
| **Trigger** | Tiny filtered set where all restaurants are rated `4.1` |
| **Impact** | Sort is non-deterministic; results may vary between runs |
| **Root Cause** | Tie-breaking not defined |
| **Handling** | Secondary sort on `votes` (already implemented); tertiary sort on `name` for determinism |

```python
filtered = filtered.sort_values(["rating", "votes", "name"], ascending=[False, False, True])
```

---

## 4. Prompt Builder Edge Cases

> **Module:** `src/prompt_builder.py`

---

### EC-4.1 — Empty Restaurant List Passed to Prompt Builder

| Field | Detail |
|---|---|
| **Trigger** | Filter engine returns an empty DataFrame |
| **Impact** | Prompt is built with no restaurant data → LLM hallucinates restaurants |
| **Root Cause** | Missing guard before calling `build_prompt()` |
| **Handling** | Check for empty DataFrame in `main.py` before invoking prompt builder |

---

### EC-4.2 — Extremely Long Extra Preferences

| Field | Detail |
|---|---|
| **Trigger** | User types a 500-word essay in the "extra preferences" field |
| **Impact** | Prompt exceeds LLM context window; API errors or truncation |
| **Root Cause** | No character limit on free-text input |
| **Handling** | Truncate `extra_prefs` to max 200 characters |

```python
extra_prefs = extra_prefs[:200] + "..." if len(extra_prefs) > 200 else extra_prefs
```

---

### EC-4.3 — Restaurant Name Contains Special Characters

| Field | Detail |
|---|---|
| **Trigger** | Restaurant named `"Café ☕ & Bar – (Est. 1990)"` |
| **Impact** | Prompt formatting breaks; LLM may misparse restaurant boundaries |
| **Root Cause** | No sanitization of dataset text before prompt injection |
| **Handling** | Sanitize restaurant fields before embedding in prompt |

---

### EC-4.4 — Cost Value Is `NaN` or `0` After Cleaning

| Field | Detail |
|---|---|
| **Trigger** | Some rows survived cleaning with `cost = NaN` or `cost = 0` |
| **Impact** | Prompt displays `₹nan` or `₹0` — confuses the LLM |
| **Root Cause** | Lenient `dropna` policy during ingestion |
| **Handling** | Replace with `"N/A"` in formatter |

```python
cost_display = f"₹{int(row['cost'])}" if pd.notna(row['cost']) and row['cost'] > 0 else "N/A"
```

---

## 5. Groq LLM Integration Edge Cases

> **Module:** `src/groq_client.py`

---

### EC-5.1 — Missing or Invalid `GROQ_API_KEY`

| Field | Detail |
|---|---|
| **Trigger** | `.env` file missing, key expired, or key not set |
| **Impact** | `AuthenticationError` from Groq SDK; app crashes |
| **Root Cause** | Environment not configured correctly |
| **Handling** | Validate key presence at startup before any user input |

```python
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("❌ GROQ_API_KEY not found. Add it to your .env file.")
```

---

### EC-5.2 — Groq Rate Limit Exceeded

| Field | Detail |
|---|---|
| **Trigger** | Too many requests per minute on free-tier Groq account |
| **Impact** | `RateLimitError` (HTTP 429); recommendation not returned |
| **Root Cause** | Free-tier API limits |
| **Handling** | Catch `RateLimitError`; wait and retry with exponential backoff |

```python
import time

for attempt in range(3):
    try:
        response = client.chat.completions.create(...)
        break
    except Exception as e:
        if "rate_limit" in str(e).lower():
            wait = 2 ** attempt
            print(f"⏳ Rate limit hit. Retrying in {wait}s...")
            time.sleep(wait)
        else:
            raise e
```

---

### EC-5.3 — Groq Returns an Empty Response

| Field | Detail |
|---|---|
| **Trigger** | LLM returns empty string or whitespace only (rare but possible) |
| **Impact** | Formatter displays blank output; user sees nothing |
| **Root Cause** | Model safety filters, malformed prompt, or transient API issue |
| **Handling** | Check response length before returning; display fallback message |

```python
content = response.choices[0].message.content
if not content or not content.strip():
    return "⚠️  The AI could not generate recommendations. Please try different preferences."
```

---

### EC-5.4 — Groq Context Window Overflow

| Field | Detail |
|---|---|
| **Trigger** | Prompt (system + user + restaurant list) exceeds model's token limit (`8192` for llama3-8b) |
| **Impact** | `BadRequestError` from API; request rejected |
| **Root Cause** | TOP_K too high or restaurant descriptions too long |
| **Handling** | Reduce `TOP_K_FILTER` to 5–7; truncate restaurant list if token estimate is too high |

---

### EC-5.5 — Network Timeout / Groq Unreachable

| Field | Detail |
|---|---|
| **Trigger** | Internet drops mid-request; Groq service is down |
| **Impact** | `requests.exceptions.Timeout` or `ConnectionError` |
| **Root Cause** | External dependency on Groq infrastructure |
| **Handling** | Set a `timeout` parameter; display retry message |

```python
# Groq SDK uses httpx internally; set timeout in client
client = Groq(api_key=api_key, timeout=30.0)
```

---

### EC-5.6 — LLM Hallucinates Restaurant Names

| Field | Detail |
|---|---|
| **Trigger** | LLM recommends restaurants NOT in the provided list |
| **Impact** | User gets recommendations for non-existent or wrong restaurants |
| **Root Cause** | LLM uses pre-trained knowledge instead of staying grounded to provided data |
| **Handling** | Add explicit instruction in system prompt: *"Only recommend from the provided list. Do not invent restaurants."* |

---

## 6. Response Parser / Output Formatter Edge Cases

> **Module:** `src/formatter.py`

---

### EC-6.1 — LLM Response Is `None`

| Field | Detail |
|---|---|
| **Trigger** | `get_recommendations()` returns `None` due to API failure |
| **Impact** | `NoneType` passed to formatter → `AttributeError` on `.strip()` |
| **Root Cause** | Missing null guard in formatter |
| **Handling** | Check for `None` before any string operations |

```python
if response_text is None:
    print("⚠️  No response from AI. Please check your API key and connection.")
    return
```

---

### EC-6.2 — LLM Responds in Different Language

| Field | Detail |
|---|---|
| **Trigger** | User's `extra_prefs` included non-English text; LLM responds in same language |
| **Impact** | Output may be in Hindi, French, etc. — unexpected for some users |
| **Root Cause** | LLM naturally mirrors input language |
| **Handling** | Add to system prompt: *"Always respond in English."* |

---

### EC-6.3 — Terminal Doesn't Support Unicode / Emoji

| Field | Detail |
|---|---|
| **Trigger** | Running on Windows CMD without UTF-8 configured |
| **Impact** | `UnicodeEncodeError`; emojis render as `?` or crash |
| **Root Cause** | Windows default CP1252 encoding |
| **Handling** | Wrap print in try/except; provide emoji-free fallback |

```python
# At top of main.py
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```

---

## 7. System-Level / Cross-Cutting Edge Cases

---

### EC-7.1 — Python Version Incompatibility

| Field | Detail |
|---|---|
| **Trigger** | Running on Python 3.8 with `tuple[str, str]` type hints (3.10+ syntax) |
| **Impact** | `TypeError` on function definitions |
| **Root Cause** | PEP 585 generics not backported to 3.8/3.9 |
| **Handling** | Use `from __future__ import annotations` or `Tuple[str, str]` from `typing` |

---

### EC-7.2 — `.env` File Committed to Git

| Field | Detail |
|---|---|
| **Trigger** | Developer forgets to add `.env` to `.gitignore` |
| **Impact** | `GROQ_API_KEY` exposed publicly on GitHub |
| **Root Cause** | Missing `.gitignore` configuration |
| **Handling** | Always include `.env` in `.gitignore`; use `git-secrets` pre-commit hook |

---

### EC-7.3 — Repeated Dataset Downloads on Every Run

| Field | Detail |
|---|---|
| **Trigger** | No local cache; `load_dataset()` called every session |
| **Impact** | Slow startup; unnecessary bandwidth usage |
| **Root Cause** | No persistence layer for preprocessed data |
| **Handling** | Save to `data/zomato_preprocessed.csv` on first load; reload from CSV on subsequent runs |

```python
CACHE_PATH = "data/zomato_preprocessed.csv"

if os.path.exists(CACHE_PATH):
    return pd.read_csv(CACHE_PATH)
else:
    df = load_and_clean()
    df.to_csv(CACHE_PATH, index=False)
    return df
```

---

### EC-7.4 — Concurrent / Multiple Users

| Field | Detail |
|---|---|
| **Trigger** | App scaled to a web interface (Streamlit/Gradio) with multiple simultaneous users |
| **Impact** | Shared in-memory DataFrame could be mutated; Groq API rate limits hit faster |
| **Root Cause** | Single-user CLI design |
| **Handling** | Load DataFrame as read-only; use per-request copies; implement request queuing |

---

## 8. Edge Case Test Matrix

| EC ID | Module | Scenario | Severity | Handled? |
|---|---|---|---|---|
| EC-1.1 | Ingest | HuggingFace unreachable | 🔴 Critical | Try/Except + cache fallback |
| EC-1.2 | Ingest | Missing columns | 🔴 Critical | Column validation + print |
| EC-1.3 | Ingest | Cost has commas/strings | 🟡 High | Strip + `pd.to_numeric` |
| EC-1.4 | Ingest | Rating = `"NEW"` / `"-"` | 🟡 High | Replace → NaN → drop |
| EC-1.5 | Ingest | Votes = NaN / 0 | 🟢 Medium | `fillna(0)` |
| EC-1.6 | Ingest | Empty DataFrame post-clean | 🔴 Critical | Raise descriptive error |
| EC-2.1 | Input | Empty location | 🔴 Critical | Validation loop |
| EC-2.2 | Input | Location not in dataset | 🟡 High | Fuzzy match suggestion |
| EC-2.3 | Input | Invalid budget string | 🟡 High | Validation loop |
| EC-2.4 | Input | Non-numeric rating | 🟡 High | Try/Except + default 3.5 |
| EC-2.5 | Input | Rating out of range | 🟢 Medium | Clamp to 0–5 |
| EC-2.6 | Input | Special characters | 🟢 Medium | Regex sanitize |
| EC-3.1 | Filter | Zero results | 🔴 Critical | Progressive relaxation |
| EC-3.2 | Filter | Case mismatch | 🟡 High | Lowercase normalization |
| EC-3.3 | Filter | Cuisine substring overlap | 🟢 Low | Acceptable / documented |
| EC-3.4 | Filter | Too many candidates | 🟡 High | Hard cap at TOP_K |
| EC-3.5 | Filter | All same rating | 🟢 Low | Secondary sort on votes |
| EC-4.1 | Prompt | Empty restaurant list | 🔴 Critical | Guard in `main.py` |
| EC-4.2 | Prompt | Long extra preferences | 🟡 High | Truncate to 200 chars |
| EC-4.3 | Prompt | Special chars in names | 🟢 Medium | Sanitize before prompt |
| EC-4.4 | Prompt | Cost is `NaN` / `0` | 🟢 Medium | Replace with `"N/A"` |
| EC-5.1 | Groq | Missing API key | 🔴 Critical | Validate at startup |
| EC-5.2 | Groq | Rate limit exceeded | 🟡 High | Exponential backoff retry |
| EC-5.3 | Groq | Empty LLM response | 🟡 High | Fallback message |
| EC-5.4 | Groq | Context window overflow | 🟡 High | Reduce TOP_K + truncate |
| EC-5.5 | Groq | Network timeout | 🟡 High | Timeout config + retry |
| EC-5.6 | Groq | LLM hallucination | 🟡 High | System prompt grounding |
| EC-6.1 | Output | `None` response | 🔴 Critical | Null guard |
| EC-6.2 | Output | Non-English response | 🟢 Low | System prompt instruction |
| EC-6.3 | Output | Unicode/emoji crash | 🟢 Medium | UTF-8 reconfigure |
| EC-7.1 | System | Python version mismatch | 🟡 High | `from __future__` import |
| EC-7.2 | System | `.env` in git | 🔴 Critical | `.gitignore` |
| EC-7.3 | System | Repeated HF downloads | 🟢 Medium | CSV cache on first load |
| EC-7.4 | System | Multi-user concurrency | 🟢 Low | Read-only DataFrame copies |

---

### Severity Legend

| Symbol | Level | Meaning |
|---|---|---|
| 🔴 | Critical | App crashes or produces completely wrong output |
| 🟡 | High | Feature broken but app survives; user gets degraded experience |
| 🟢 | Medium / Low | Minor UX issue; easy workaround available |
