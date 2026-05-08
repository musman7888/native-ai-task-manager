"""Pytest configuration for Tasks MCP tests."""

import sys
from pathlib import Path

# Add src to path so tests can import tasks_mcp
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
