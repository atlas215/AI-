"""
Configuration Module for ATLAS System
Centralized settings for API keys, endpoints, and system parameters
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==================== API KEYS ====================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
JUDGE0_API_KEY = os.getenv("JUDGE0_API_KEY", "")

# ==================== REPOSITORY SETTINGS ====================
GITHUB_REPO_OWNER = os.getenv("GITHUB_REPO_OWNER", "atlas215")
GITHUB_REPO_NAME = os.getenv("GITHUB_REPO_NAME", "AI-")
GITHUB_REPO_BRANCH = os.getenv("GITHUB_REPO_BRANCH", "main")
MEMORY_FILE = "memory.json"
MEMORY_COMMIT_MESSAGE = "[ATLAS] Auto-commit memory snapshot"

# ==================== LLM ENDPOINTS ====================
LLM_PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "models": [
            "llama-3-70b-versatile",
            "llama-3-8b-instant",
            "llama-2-70b-4096"
        ]
    },
    "huggingface": {
        "base_url": "https://api-inference.huggingface.co/models",
        "models": [
            "meta-llama/Llama-2-70b-chat-hf",
            "deepseek-ai/deepseek-coder-33b-instruct",
            "mistralai/Mistral-7B-Instruct-v0.1"
        ]
    },
    "github_models": {
        "base_url": "https://models.inference.ai.azure.com",
        "models": [
            "gpt-4o",
            "Llama-3-70b",
            "Phi-4"
        ]
    }
}

# ==================== JUDGE0 SETTINGS ====================
JUDGE0_BASE_URL = os.getenv("JUDGE0_BASE_URL", "https://judge0-ce.p.rapidapi.com")
JUDGE0_LANGUAGE_IDS = {
    "c": 50,
    "cpp": 54,
    "python": 71,
    "javascript": 63,
    "rust": 73
}
JUDGE0_TIMEOUT = 10  # seconds

# ==================== VISION SYSTEM ====================
SCREENSHOT_DIR = "logs/vision"
VISION_LOG_INTERVAL = 60  # seconds

# ==================== COMMUNICATION ====================
WHATSAPP_TARGET_PHONE = os.getenv("WHATSAPP_TARGET_PHONE", "+255697003469")
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))
FASTAPI_DEBUG = os.getenv("FASTAPI_DEBUG", "False").lower() == "true"

# ==================== BRAIN ENGINE ====================
LLM_PARALLEL_REQUESTS = 15
LLM_TIMEOUT = 30  # seconds
VOTING_THRESHOLD = 0.7  # For code quality scoring
C_CODE_ANALYSIS_PROMPT = """
You are an expert C programmer. Analyze the following requirements and generate production-ready C code.
Follow these principles:
1. Memory safety (no buffer overflows)
2. Efficient algorithms
3. Proper error handling
4. Clear variable naming
5. Include comments for complex logic

Requirements: {requirements}

Generate only the C code, no explanations.
"""

# ==================== CONSTRUCTOR (ASYNC) ====================
CYCLE_INTERVAL = 60  # seconds between main cycles
MAX_CONCURRENT_TASKS = 10
ASYNC_TIMEOUT = 300  # seconds

# ==================== LOGGING ====================
LOG_DIR = "logs"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==================== SECURITY ====================
ENABLE_AUTH = os.getenv("ENABLE_AUTH", "True").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# ==================== SYSTEM ====================
ATLAS_VERSION = "ATLAS-V2.0-REFACTORED"
SYSTEM_NAME = "ATLAS"
OWNER = "SIR BURTON"
