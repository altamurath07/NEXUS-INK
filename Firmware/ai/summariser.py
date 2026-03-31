# sends post text to a local ollama instance and gets a 3 sentence summary back
# fix: ollama 0.1.8 returns an obj not a dict - use response.message.content

import ollama, os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL   = os.getenv("OLLAMA_MODEL", "mistral")
PROMPT_TEMPLATE = """
You are a concise news summariser for an e-ink display device.
Summarise the following content in exactly 3 sentences.
Use plain language. No bullet points. No markdown.

Content:
{text}
"""

def summarise(text: str, model: str = DEFAULT_MODEL) -> str:
    logger.info(f"summarising {len(text)} chars w/ {model}")
    if not text or len(text.strip()) < 20:
        return text.strip()
    try:
        response = ollama.chat(
            model    = model,
            messages = [{"role": "user", "content": PROMPT_TEMPLATE.format(text=text[:2000])}]
        )
        result = response.message.content.strip()
        logger.success(f"summary: {result[:80]}…")
        return result
    except Exception as e:
        logger.error(f"ollama failed: {e}")
        return text[:300]

def summarise_batch(texts: list, model: str = DEFAULT_MODEL) -> list:
    return [summarise(t, model=model) for t in texts]
