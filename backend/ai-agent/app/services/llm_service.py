from groq import Groq
from app.config.settings import GROQ_API_KEY, GROQ_MODEL

_client = None

def get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=GROQ_API_KEY)
    return _client

def call_llm(prompt: str, system: str = "You are a helpful medical AI assistant.", temperature: float = 0.2) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=2048,
    )
    return response.choices[0].message.content.strip()