"""
llm/groq_client.py — Single Groq API caller used by every module.

KEY FIX:
  When `prompt` is a list (chat history with system + user + assistant turns),
  it is forwarded directly to the API as `messages`.
  When it is a plain string, it is wrapped as a single user message.
  Previously, a list prompt was stringified via str(prompt) which completely
  destroyed the system prompt and conversation history in Chat.py.
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("CRITICAL ERROR: GROQ_API_KEY not found.")
    client = None
else:
    client = Groq(api_key=api_key)

DEFAULT_MODEL = "llama-3.3-70b-versatile"


def call_llm_api(prompt, model=DEFAULT_MODEL, temperature=0.2, max_tokens=1024):
    """
    Generic LLM caller for all modules via Groq.

    Args:
        prompt (str | list): 
            - str  → wrapped as single {"role":"user","content":...} message.
            - list → forwarded as-is (must be valid Groq messages list with
                     role/content dicts, e.g. system + history + user).
        model       (str):   Groq model ID.
        temperature (float): Sampling temperature.
        max_tokens  (int):   Hard cap on output tokens.

    Returns:
        str: Model response text.

    Raises:
        RuntimeError: If client is not configured or API call fails.
    """
    if not client:
        raise RuntimeError("Groq client not configured — check GROQ_API_KEY.")

    # ── Normalise prompt → messages list ──────────────────────────────────────
    if isinstance(prompt, list):
        # Already a fully-formed messages list (Chat.py passes system+history+user)
        messages = prompt
    elif isinstance(prompt, str):
        messages = [{"role": "user", "content": prompt}]
    elif isinstance(prompt, dict):
        messages = [{"role": "user", "content": str(prompt)}]
    else:
        messages = [{"role": "user", "content": str(prompt)}]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        usage = response.usage
        if usage:
            print(
                f"[groq] tokens — prompt: {usage.prompt_tokens}, "
                f"completion: {usage.completion_tokens}, "
                f"total: {usage.total_tokens}"
            )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"Groq API error: {e}")