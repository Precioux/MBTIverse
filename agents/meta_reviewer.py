# agents/meta_reviewer.py
from __future__ import annotations
from typing import List, Dict, Optional
from openai import OpenAI
import os
from agents.base_agent import DEFAULTS, AVALAI_MODEL

client = OpenAI(
    api_key=os.getenv("AVALAI_API_KEY"),
    base_url=os.getenv("AVALAI_API_BASE", "https://api.avalai.ai/v1"),
)

_EMBEDDED_META_PROMPT = """You are the Meta Reviewer for a 16-agent MBTI panel.

Your job is to write a **clear, human-readable briefing** that anyone can understand.
Focus on social impacts, risks, and opportunities.

Output must include these sections with clear headers:

1. Consensus — main points the agents agree on.
2. Disagreements — where their perspectives conflict.
3. Blindspots — important issues no agent raised.
4. Potential Social Effects — explain in plain English the impacts across domains
   like public trust, misinformation, fairness, privacy, economy, health, environment,
   safety, law, and culture.
   Use short paragraphs and bullet points, avoid jargon.
5. Recommended Actions — 3–5 concrete, practical steps for decision-makers.

Style:
- Use plain English, clear structure, short paragraphs.
- Think like a policy briefing or executive summary.
- Make it engaging and easy for a non-technical reader.

Notice! 
You are allowed to use MAXIMUM 1500 Characters!
"""

class MetaReviewerAgent:
    def __init__(self):
        self.name = "MetaReviewer"
        self.prompt = _EMBEDDED_META_PROMPT

    def build_messages(self, news: str, reactions: List[Dict[str, str]]):
        system = self.prompt.strip()
        panel_lines = []
        for r in reactions:
            who = r.get("personality", "Unknown")
            txt = (r.get("reaction") or "").strip().replace("\n", " ")
            panel_lines.append(f"- {who}: {txt}")
        user = (
            f"News:\n{news.strip()}\n\n"
            "Panel Reactions:\n" + "\n".join(panel_lines) +
            "\n\nWrite the meta-review briefing now."
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

    def review(
        self,
        reactions: List[Dict[str, str]],
        news: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        params = dict(DEFAULTS)
        if temperature is not None:
            params["temperature"] = float(temperature)
        if top_p is not None:
            params["top_p"] = float(top_p)
        if max_tokens is not None:
            params["max_tokens"] = int(max_tokens)

        try:
            resp = client.chat.completions.create(
                model=AVALAI_MODEL,
                messages=self.build_messages(news, reactions),
                temperature=params["temperature"],
                top_p=params["top_p"],
                max_tokens=params["max_tokens"],
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"Meta reviewer failed: {type(e).__name__}: {e}")