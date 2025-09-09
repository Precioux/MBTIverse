# agents/base_agent.py
from __future__ import annotations
import os
from pathlib import Path
from openai import OpenAI
from typing import Optional

# AvalAI client (OpenAI-compatible)
client = OpenAI(
    api_key=os.getenv("AVALAI_API_KEY"),
    base_url=os.getenv("AVALAI_API_BASE", "https://api.avalai.ai/v1"),
)
AVALAI_MODEL = os.getenv("AVALAI_MODEL", "openai.gpt-oss-120b-1:0")

DEFAULTS = {
    "temperature": float(os.getenv("MBITVERSE_TEMPERATURE", "0.3")),
    "top_p": float(os.getenv("MBITVERSE_TOP_P", "0.95")),
    "max_tokens": int(os.getenv("MBITVERSE_MAX_TOKENS", "256")),
}

class BaseAgent:
    def __init__(self, name: str, prompt_path: str):
        self.name = name
        self.prompt = self._load_prompt(prompt_path)

    def _load_prompt(self, path_str: str) -> str:
        p = Path(path_str)
        if p.exists():
            return p.read_text(encoding="utf-8")
        # fallback if prompts dir not found
        raise FileNotFoundError(f"Prompt not found: {path_str}")

    def build_messages(self, news: str):
        system = self.prompt.strip()
        user = (
            f"React to the following news in 2–3 concise sentences. "
            f"Stay true to your {self.name} persona.\n\n"
            f"News:\n{news.strip()}"
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    def react(
        self,
        news: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        params = dict(DEFAULTS)
        if temperature is not None: params["temperature"] = float(temperature)
        if top_p is not None:       params["top_p"] = float(top_p)
        if max_tokens is not None:  params["max_tokens"] = int(max_tokens)

        resp = client.chat.completions.create(
            model=AVALAI_MODEL,
            messages=self.build_messages(news),
            temperature=params["temperature"],
            top_p=params["top_p"],
            max_tokens=params["max_tokens"],
        )
        return resp.choices[0].message.content.strip()