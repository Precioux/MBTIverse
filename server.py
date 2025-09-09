# server.py
from __future__ import annotations
from typing import Dict, List, Optional, Any, Union

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field, field_validator

from agents.personas import (
    ISTJAgent, ISFJAgent, INFJAgent, INTJAgent,
    ISTPAgent, ISFPAgent, INFPAgent, INTPAgent,
    ESTPAgent, ESFPAgent, ENFPAgent, ENTPAgent,
    ESTJAgent, ESFJAgent, ENFJAgent, ENTJAgent,
)
from agents.meta_reviewer import MetaReviewerAgent

app = FastAPI(
    title="Mbitverse — 16 Agents with Meta Reviewer",
    version="2.1.0",
    description=(
        "Post news and get reactions from 16 MBTI agents plus a meta-review.\n\n"
        "Tip: You can send `news` as a single JSON string (use \\n for line breaks), "
        "or `news_lines` as a list of strings. The server will join them for you."
    ),
)

MBTI: List[str] = [
    "ISTJ", "ISFJ", "INFJ", "INTJ",
    "ISTP", "ISFP", "INFP", "INTP",
    "ESTP", "ESFP", "ENFP", "ENTP",
    "ESTJ", "ESFJ", "ENFJ", "ENTJ",
]

def _mk(kls):
    return kls()

AGENTS: Dict[str, Any] = {
    "ISTJ": _mk(ISTJAgent), "ISFJ": _mk(ISFJAgent), "INFJ": _mk(INFJAgent), "INTJ": _mk(INTJAgent),
    "ISTP": _mk(ISTPAgent), "ISFP": _mk(ISFPAgent), "INFP": _mk(INFPAgent), "INTP": _mk(INTPAgent),
    "ESTP": _mk(ESTPAgent), "ESFP": _mk(ESFPAgent), "ENFP": _mk(ENFPAgent), "ENTP": _mk(ENTPAgent),
    "ESTJ": _mk(ESTJAgent), "ESFJ": _mk(ESFJAgent), "ENFJ": _mk(ENFJAgent), "ENTJ": _mk(ENTJAgent),
}
META = MetaReviewerAgent()

# ---------------- Models (Swagger-friendly) ----------------

class SingleAgentRequest(BaseModel):
    # Either provide news (string) or news_lines (list of strings)
    news: Optional[str] = Field(
        None, description="Input text. If multi-line, escape line breaks as \\n."
    )
    news_lines: Optional[List[str]] = Field(
        None, description="Alternative: provide a list of lines; server joins them with spaces."
    )
    temperature: Optional[float] = Field(None, ge=0, le=2)
    top_p: Optional[float] = Field(None, ge=0, le=1)
    max_tokens: Optional[int] = Field(None, ge=1, le=8192)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "Single string (escaped newlines)",
                    "value": {
                        "news": "Line 1.\\nLine 2.\\nLine 3.",
                        "temperature": 0.5, "top_p": 0.9, "max_tokens": 256
                    }
                },
                {
                    "summary": "List of lines (easier to paste)",
                    "value": {
                        "news_lines": ["Line 1.", "Line 2.", "Line 3."],
                        "temperature": 0.3, "top_p": 0.9, "max_tokens": 256
                    }
                }
            ]
        }
    }

class MultiAgentRequest(BaseModel):
    # Either provide news (string) or news_lines (list of strings)
    news: Optional[str] = Field(
        None, description="Input text. If multi-line, escape line breaks as \\n."
    )
    news_lines: Optional[List[str]] = Field(
        None, description="Alternative: provide a list of lines; server joins them with spaces."
    )
    agents: Optional[Union[List[str], str]] = Field(
        None, description="MBTI codes (e.g., ['ISTJ','ENFP']). Omit → all 16."
    )
    temperature: Optional[float] = Field(None, ge=0, le=2)
    top_p: Optional[float] = Field(None, ge=0, le=1)
    max_tokens: Optional[int] = Field(None, ge=1, le=8192)

    @field_validator("agents")
    @classmethod
    def normalize_agents(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = [v]
        out: List[str] = []
        for a in v or []:
            code = str(a).upper().strip()
            if code and code in MBTI and code not in out:
                out.append(code)
        return out or None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "summary": "All 16 agents — multi-line as list",
                    "value": {
                        "news_lines": [
                            "The Israeli army says it has carried out an assassination attempt on Hamas leaders in Doha.",
                            "A Hamas source tells Al Jazeera the attack happened during ceasefire talks.",
                            "Qatar condemns the attack as a violation of international law."
                        ],
                        "temperature": 0.3, "top_p": 0.9, "max_tokens": 512
                    }
                },
                {
                    "summary": "Subset of agents — single string",
                    "value": {
                        "news": "ECB hints at rate cuts as inflation cools across the eurozone.",
                        "agents": ["ISTJ", "ENFP", "INTJ", "ESFP"],
                        "temperature": 0.6, "top_p": 0.9, "max_tokens": 256
                    }
                }
            ]
        }
    }

class Reaction(BaseModel):
    personality: str
    reaction: str

class PanelResponse(BaseModel):
    news: str
    results: List[Reaction]                  # each agent’s answer
    meta_review: Optional[str] = None        # meta synthesis
    errors: Dict[str, str] = {}             # per-agent/meta errors (if any)

# ---------------- Helpers ----------------

def _normalize_news(news: Optional[str], news_lines: Optional[List[str]]) -> str:
    text = (news or "").strip() if news else ""
    if not text and news_lines:
        # join list of lines into a single space-separated paragraph
        text = " ".join((line or "").strip() for line in news_lines if line is not None).strip()
    return text

def _gen_params(temperature: Optional[float], top_p: Optional[float], max_tokens: Optional[int]) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if temperature is not None:
        params["temperature"] = max(0.0, float(temperature))
    if top_p is not None:
        params["top_p"] = min(1.0, max(0.0, float(top_p)))
    if max_tokens is not None and max_tokens > 0:
        params["max_tokens"] = int(max_tokens)
    return params

def _run_panel(req: MultiAgentRequest) -> PanelResponse:
    news_text = _normalize_news(req.news, req.news_lines)
    if not news_text:
        raise HTTPException(status_code=400, detail="Provide 'news' (string) or 'news_lines' (list of strings).")

    selection = req.agents or MBTI
    params = _gen_params(req.temperature, req.top_p, req.max_tokens)

    results: List[Reaction] = []
    errors: Dict[str, str] = {}

    # collect all agent reactions
    for code in selection:
        agent = AGENTS.get(code)
        if not agent:
            errors[code] = "Agent not found."
            continue
        try:
            out = agent.react(news_text, **params)
            results.append(Reaction(personality=code, reaction=out))
        except Exception as e:
            errors[code] = f"{type(e).__name__}: {e}"

    # run meta reviewer
    meta_text: Optional[str] = None
    try:
        meta_text = META.review(
            reactions=[{"personality": r.personality, "reaction": r.reaction} for r in results],
            news=news_text,
            **params,
        )
    except Exception as e:
        errors["META_REVIEW"] = str(e)

    return PanelResponse(news=news_text, results=results, meta_review=meta_text, errors=errors)

# ---------------- Routes (Swagger only) ----------------

@app.get("/agents", tags=["meta"])
def list_agents():
    return {"count": len(AGENTS), "agents": MBTI}

@app.post("/reaction/{agent_code}", response_model=Reaction, tags=["single"])
def reaction(agent_code: str, req: SingleAgentRequest = Body(...)):
    code = agent_code.upper()
    agent = AGENTS.get(code)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Unknown agent '{agent_code}'.")
    news_text = _normalize_news(req.news, req.news_lines)
    if not news_text:
        raise HTTPException(status_code=400, detail="Provide 'news' (string) or 'news_lines' (list of strings).")
    params = _gen_params(req.temperature, req.top_p, req.max_tokens)
    text = agent.react(news_text, **params)
    return Reaction(personality=code, reaction=text)

@app.post("/full_pipeline", response_model=PanelResponse, tags=["panel"])
def full_pipeline(
    req: MultiAgentRequest = Body(
        ...,
        example={
            "news_lines": [
                "NVIDIA unveils an energy-efficient GPU architecture aimed at hyperscale datacenters.",
                "Vendors expect lower TCO due to reduced power draw."
            ],
            "temperature": 0.4, "top_p": 0.9, "max_tokens": 512
        },
    )
):
    return _run_panel(req)
