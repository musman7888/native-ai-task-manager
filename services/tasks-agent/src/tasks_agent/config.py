"""Configuration from environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TASKS_MCP_URL = os.getenv("TASKS_MCP_URL", "http://localhost:8000/mcp")
AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini/gemini-3.1-flash-lite-preview")
