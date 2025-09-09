import requests
from pathlib import Path

class Agent:
    def __init__(self, name: str, prompt_file: str, model: str = "gpt-oss", host: str = "http://localhost:11434"):
        self.name = name
        self.model = model
        self.host = host
        self.personality_prompt = self._load_prompt(prompt_file)

    def _load_prompt(self, prompt_file: str) -> str:
        path = Path(prompt_file)
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        return path.read_text(encoding="utf-8")

    def react(self, news: str) -> str:
        """Generate a reaction to the news based on this agent's personality definition."""
        prompt = f"{self.personality_prompt}\n\nNow react to this news in 2–3 sentences:\n{news}"

        resp = requests.post(
            f"{self.host}/api/generate",
            headers={"Content-Type": "application/json"},
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )

        if resp.status_code != 200:
            return f"[Error {resp.status_code}] {resp.text}"

        return resp.json().get("response", "").strip()
