# Problem Statement: AI-Powered Restaurant Recommendation System (Zomato Use Case)

## Overview

You are tasked with building an **AI-powered restaurant recommendation service** inspired by Zomato. The system should intelligently suggest restaurants based on user preferences by combining structured data with a **Large Language Model (LLM)**.

---

## Objective

Design and implement an application that:

- Takes **user preferences** (such as location, budget, cuisine, and ratings)
- Uses a **real-world dataset** of restaurants
- Leverages an **LLM** to generate personalized, human-like recommendations
- Displays **clear and useful results** to the user

---

## System Workflow

### 1. Data Ingestion

- Load and preprocess the **Zomato dataset** from Hugging Face:
  > 🔗 [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- Extract relevant fields such as:
  - Restaurant name
  - Location
  - Cuisine type
  - Cost
  - Rating
  - Other metadata

---

### 2. User Input

Collect user preferences including:

| Preference | Examples |
|---|---|
| **Location** | Delhi, Bangalore |
| **Budget** | Low, Medium, High |
| **Cuisine** | Italian, Chinese, Indian |
| **Minimum Rating** | e.g., 4.0 and above |
| **Additional Preferences** | Family-friendly, Quick service, etc. |

---

### 3. Integration Layer

- **Filter** and prepare relevant restaurant data based on user input
- **Pass** structured results into an LLM prompt
- **Design a prompt** that helps the LLM reason and rank options effectively

---

### 4. Recommendation Engine

Use the LLM to:

- ✅ **Rank restaurants** based on relevance to user preferences
- ✅ **Provide explanations** — why each recommendation fits the user
- ✅ **Optionally summarize** choices for quick decision-making

---

### 5. Output Display

Present top recommendations in a user-friendly format:

| Field | Description |
|---|---|
| **Restaurant Name** | Name of the recommended restaurant |
| **Cuisine** | Type of cuisine served |
| **Rating** | User/aggregated rating |
| **Estimated Cost** | Approximate cost for two |
| **AI-Generated Explanation** | Personalized reasoning from the LLM |

---

## Technology Context

- **Dataset Source:** Hugging Face — `ManikaSaini/zomato-restaurant-recommendation`
- **Core AI Component:** Large Language Model (LLM) for reasoning and ranking
- **Use Case Inspiration:** Zomato-style restaurant discovery

---

## Summary

This project bridges **structured data filtering** with **generative AI** to deliver a smart, conversational restaurant recommendation experience. The LLM adds a layer of personalization and explainability that goes beyond simple rule-based filtering.
