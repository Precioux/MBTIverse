from fastapi import FastAPI
from pydantic import BaseModel
from agent import Agent

app = FastAPI()

# Load one agent for now
istj = Agent("ISTJ", "prompts/istj.txt")
istp = Agent("ISTP", "prompts/istp.txt")

class NewsRequest(BaseModel):
    news: str

@app.post("/reaction/istj")
def istj_reaction(req: NewsRequest):
    return {"personality": istj.name, "reaction": istj.react(req.news)}
