# config.py — Central configuration for TableMate AI Recommender

GROQ_MODEL        = "openai/gpt-oss-20b"   # llama3-8b-8192 decommissioned; use available model
GROQ_MAX_TOKENS   = 1024
GROQ_TEMPERATURE  = 0.5

HF_DATASET_NAME   = "ManikaSaini/zomato-restaurant-recommendation"
HF_DATASET_SPLIT  = "train"

TOP_K_FILTER      = 10       # Max restaurants passed to LLM

BUDGET_TIERS = {
    "low":    (0,   500),
    "medium": (501, 1200),
    "high":   (1201, float("inf"))
}
