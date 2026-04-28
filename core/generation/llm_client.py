"""LLM client – Together AI primary, Groq fallback."""
from openai import OpenAI
from config.settings import OPENAI_API_KEY, GROQ_API_KEY, TOGETHER_API_KEY

# Primary: Together AI
together_client = OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url="https://api.together.xyz/v1",
)

# Fallback: Groq
groq_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

PRIMARY_MODEL = "meta-llama/Llama-3.2-3B-Instruct"   # fast & free
FALLBACK_MODEL = "llama-3.3-70b-versatile"
MAX_RETRIES = 2

def _try_generate(client, model, system_prompt, user_prompt, n):
    variants = []
    for _ in range(n):
        for attempt in range(1, MAX_RETRIES + 2):
            try:
                response = client.chat.completions.create(
                    model=model,
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
                    print(f"Together AI call failed (attempt {attempt}/{MAX_RETRIES+1}): {e}. Retrying...")
                else:
                    raise
    return variants

def generate_tweet(system_prompt: str, user_prompt: str, n: int = 1) -> list[str]:
    """Generate tweet variants, fallback to Groq if Together AI fails."""
    try:
        return _try_generate(together_client, PRIMARY_MODEL, system_prompt, user_prompt, n)
    except Exception as primary_e:
        print(f"Together AI primary failed: {primary_e}")
        print("Falling back to Groq...")
        try:
            return _try_generate(groq_client, FALLBACK_MODEL, system_prompt, user_prompt, n)
        except Exception as fallback_e:
            raise RuntimeError(f"Both LLMs failed. Together: {primary_e}, Groq: {fallback_e}")
