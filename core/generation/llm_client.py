"""LLM client – Groq (free tier)."""
from openai import OpenAI
from config.settings import GROQ_API_KEY

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

DEFAULT_MODEL = "llama-3.3-70b-versatile"
MAX_RETRIES = 2

def generate_tweet(system_prompt: str, user_prompt: str, n: int = 1) -> list[str]:
    """Generate n tweet variants."""
    variants = []
    for _ in range(n):
        for attempt in range(1, MAX_RETRIES + 2):
            try:
                response = client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=100,
                    temperature=0.9,
                )
                variants.append(response.choices[0].message.content.strip())
                break
            except Exception as e:
                if attempt <= MAX_RETRIES:
                    print(f"LLM call failed (attempt {attempt}/{MAX_RETRIES+1}): {e}. Retrying...")
                else:
                    raise RuntimeError(f"LLM generation failed after {MAX_RETRIES+1} attempts") from e
    return variants
