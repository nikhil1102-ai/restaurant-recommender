# src/ingest.py -- Phase 2: Data Ingestion Module
# Loads the Zomato HuggingFace dataset, cleans it, normalizes fields,
# and exposes a ready-to-query Pandas DataFrame.

import os
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import sys
import pandas as pd
from datasets import load_dataset

# Resolve project root so config is importable regardless of working directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import HF_DATASET_NAME, HF_DATASET_SPLIT, BUDGET_TIERS

# Optional: path to save/load a preprocessed CSV (speeds up repeat runs)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
PREPROCESSED_CSV = os.path.join(DATA_DIR, "zomato_preprocessed.csv")


# ---------------------------------------------------------------------------
# Task 2.6 — Budget tier mapper
# ---------------------------------------------------------------------------
def map_budget(cost: float) -> str:
    """Map a numeric cost value to a budget tier label (low / medium / high)."""
    for tier, (low, high) in BUDGET_TIERS.items():
        if low <= cost <= high:
            return tier
    return "high"          # anything above the highest threshold is "high"


# ---------------------------------------------------------------------------
# Task 2.8 — Public entry point
# ---------------------------------------------------------------------------
def load_restaurants(use_cache: bool = True) -> pd.DataFrame:
    """
    Load, clean, and return the Zomato restaurant DataFrame.

    Steps performed:
      2.1  Load dataset from HuggingFace using load_dataset()
      2.2  Convert Arrow Dataset to Pandas DataFrame
      2.3  Inspect and keep only relevant columns
      2.4  Drop rows with null values in critical fields
      2.5  Normalise text fields (lower-case + strip)
      2.6  Map cost -> budget tier using BUDGET_TIERS
      2.7  Optionally persist preprocessed data to data/zomato_preprocessed.csv

    Args:
        use_cache: If True and the preprocessed CSV exists, load from disk
                   instead of re-downloading from HuggingFace.

    Returns:
        A clean pandas DataFrame ready for filtering.
    """

    # -----------------------------------------------------------------------
    # Fast path: load from cached CSV if available
    # -----------------------------------------------------------------------
    if use_cache and os.path.exists(PREPROCESSED_CSV):
        print(f"[CACHE] Loading from cache: {PREPROCESSED_CSV}")
        # Load with memory-optimised dtypes to stay within Railway's 512MB limit
        dtype_map = {
            "name":        "string",
            "location":    "category",
            "cuisines":    "category",
            "cost":        "float32",
            "rating":      "float32",
            "votes":       "int32",
            "budget_tier": "category",
        }
        usecols = list(dtype_map.keys())
        df = pd.read_csv(
            PREPROCESSED_CSV,
            usecols=lambda c: c in usecols,
            dtype={k: v for k, v in dtype_map.items() if k != "votes"},
        )
        # votes may be stored as float due to NaN — coerce to int32
        if "votes" in df.columns:
            df["votes"] = df["votes"].fillna(0).astype("int32")
        print(f"[OK] {len(df):,} restaurants loaded from cache.")
        return df

    # -----------------------------------------------------------------------
    # Task 2.1 — Load dataset from HuggingFace
    # -----------------------------------------------------------------------
    print(f"[DOWNLOAD] Fetching dataset '{HF_DATASET_NAME}' (split='{HF_DATASET_SPLIT}')...")
    dataset = load_dataset(HF_DATASET_NAME, split=HF_DATASET_SPLIT)

    # -----------------------------------------------------------------------
    # Task 2.2 — Convert to Pandas DataFrame
    # -----------------------------------------------------------------------
    df = dataset.to_pandas()

    # -----------------------------------------------------------------------
    # Task 2.3 — Inspect column names and keep only relevant ones
    # -----------------------------------------------------------------------
    print(f"[INFO] Raw columns: {list(df.columns)}")

    desired_cols = [
        "name",
        "location",
        "cuisines",
        "approx_cost(for two people)",
        "aggregate rating",   # some HF snapshots
        "rate",               # actual column in ManikaSaini dataset
        "votes",
        "online_order",
        "book_table",
    ]
    # Keep only the columns that actually exist in this dataset snapshot
    available_cols = [c for c in desired_cols if c in df.columns]
    df = df[available_cols].copy()

    # -----------------------------------------------------------------------
    # Rename columns for convenience
    # -----------------------------------------------------------------------
    rename_map = {}
    if "approx_cost(for two people)" in df.columns:
        rename_map["approx_cost(for two people)"] = "cost"
    if "aggregate rating" in df.columns:      # some snapshots use this name
        rename_map["aggregate rating"] = "rating"
    if "rate" in df.columns:                  # actual column name in this dataset
        rename_map["rate"] = "rating"
    df.rename(columns=rename_map, inplace=True)

    # -----------------------------------------------------------------------
    # Task 2.4 — Drop rows with null values in critical fields
    # -----------------------------------------------------------------------
    critical = [c for c in ["name", "location", "cuisines", "rating"] if c in df.columns]
    before = len(df)
    df.dropna(subset=critical, inplace=True)
    print(f"[CLEAN] Dropped {before - len(df):,} rows with null critical fields.")

    # -----------------------------------------------------------------------
    # Task 2.5 — Normalise text fields
    # -----------------------------------------------------------------------
    if "location" in df.columns:
        df["location"] = df["location"].astype(str).str.lower().str.strip().astype("category")
    if "cuisines" in df.columns:
        df["cuisines"] = df["cuisines"].astype(str).str.lower().str.strip().astype("category")
    if "name" in df.columns:
        df["name"] = df["name"].astype(str).str.strip().astype("string")

    # -----------------------------------------------------------------------
    # Coerce numeric columns; drop rows that cannot be parsed
    # -----------------------------------------------------------------------
    if "cost" in df.columns:
        # Handle values like "1,200" -> 1200
        df["cost"] = (
            df["cost"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .pipe(pd.to_numeric, errors="coerce")
        )
    else:
        # Column missing entirely — create a placeholder so budget mapping works
        df["cost"] = float("nan")

    if "rating" in df.columns:
        # The dataset stores ratings as strings like '4.1/5' — extract the numeric part
        df["rating"] = (
            df["rating"]
            .astype(str)
            .str.extract(r"([\d.]+)", expand=False)   # grab '4.1' from '4.1/5'
            .pipe(pd.to_numeric, errors="coerce")
        )

    if "votes" in df.columns:
        df["votes"] = pd.to_numeric(df["votes"], errors="coerce").fillna(0).astype("int32")
    else:
        df["votes"] = 0

    # Drop rows still null in cost or rating after coercion
    numeric_critical = [c for c in ["cost", "rating"] if c in df.columns]
    before = len(df)
    df.dropna(subset=numeric_critical, inplace=True)
    print(f"[CLEAN] Dropped {before - len(df):,} rows with un-parseable cost/rating.")

    # -----------------------------------------------------------------------
    # Task 2.6 — Map cost -> budget tier
    # -----------------------------------------------------------------------
    df["budget_tier"] = df["cost"].apply(map_budget).astype("category")

    # -----------------------------------------------------------------------
    # Deduplication -- keep one entry per unique (name, location, cost)
    # Strategy: sort by votes DESC so .first() keeps the best-reviewed copy.
    # -----------------------------------------------------------------------
    before = len(df)
    df = (
        df
        .sort_values("votes", ascending=False)
        .drop_duplicates(subset=["name", "location", "cost"], keep="first")
    )
    print(f"[DEDUP] Removed {before - len(df):,} duplicate rows "
          f"({len(df):,} unique restaurants remain).")

    # Reset index for clean downstream access
    df = df.reset_index(drop=True)

    # -----------------------------------------------------------------------
    # Task 2.7 — Persist preprocessed data (optional)
    # -----------------------------------------------------------------------
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(PREPROCESSED_CSV, index=False)
    print(f"[SAVE] Preprocessed data saved to: {PREPROCESSED_CSV}")

    print(f"[OK] {len(df):,} restaurants ready.")
    print(f"[BUDGET DISTRIBUTION]\n{df['budget_tier'].value_counts().to_string()}")

    return df


# ---------------------------------------------------------------------------
# Quick smoke-test (run: python src/ingest.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    df = load_restaurants(use_cache=False)   # force fresh download for testing
    print("\n--- DataFrame Info ---")
    print(df.dtypes)
    print("\n--- Sample rows ---")
    print(df.head(3).to_string())
    assert not df.empty, "DataFrame must not be empty"
    assert "budget_tier" in df.columns, "budget_tier column missing"
    assert "rating" in df.columns, "rating column missing — check rename_map"
    critical_check = [c for c in ["name", "location", "cuisines", "rating"] if c in df.columns]
    null_count = df[critical_check].isnull().sum().sum()
    assert null_count == 0, f"Null values found in critical columns: {null_count}"
    print("\n[PASS] Phase 2 smoke-test PASSED.")
