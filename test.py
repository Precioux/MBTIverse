from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("AVALAI_API_KEY"),
    base_url=os.getenv("AVALAI_API_BASE", "https://api.avalai.ai/v1"),
)

resp = client.chat.completions.create(
    model=os.getenv("AVALAI_MODEL", "openai.gpt-oss-120b-1:0"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in five words."}
    ],
)

print(resp.choices[0].message.content)
