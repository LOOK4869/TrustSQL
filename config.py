# Configuration: API keys, model names, and dataset paths for TrustSQL

import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# --- Model Names ---
OPENAI_MODEL: str = "gpt-4o-mini"
GEMINI_MODEL: str = "gemini-1.5-flash"
GROQ_MODEL: str = "llama3-8b-8192"

# --- Dataset Paths ---
BIRD_DATA_DIR: str = os.path.join("data", "bird")
BIRD_DEV_JSON: str = os.path.join(BIRD_DATA_DIR, "dev.json")
BIRD_DB_DIR: str = os.path.join(BIRD_DATA_DIR, "dev_databases")

# --- Pipeline Settings ---
MAX_SCHEMA_TABLES: int = 10        # Max tables to keep after schema filtering
MAX_TOKENS: int = 1024             # Max tokens for LLM responses
TEMPERATURE: float = 0.0           # Deterministic generation for SQL tasks
