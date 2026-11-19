import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).with_name(".env"), override=False)


def setting(name: str) -> str:
    return os.getenv(name, "").strip()


def chat_tool_options(model: str) -> dict:
    # These models require reasoning to be disabled for Chat Completions tools.
    return {"reasoning_effort": "none"} if model in {"gpt-6-luna", "gpt-6-sol"} else {}
