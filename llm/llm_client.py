import os
from dotenv import load_dotenv
from groq import Groq

# Load env
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")


if not api_key:
    print("CRITICAL ERROR: GROQ_API_KEY not found.")
    client = None
else:
    client = Groq(api_key=api_key)

DEFAULT_MODEL = "llama-3.3-70b-versatile"

def call_llm_api(prompt, model=DEFAULT_MODEL, temperature=0.2):
    """
    Generic LLM caller for all modules via Groq.

    Args:
        prompt (str or dict): Input prompt
        model (str): Groq model ID
        temperature (float): Controls randomness

    Returns:
        str: Extracted response text
    """

    if not client:
        raise RuntimeError("Groq client not configured.")

    # Normalize prompt to Groq message format
    if isinstance(prompt, str):
        messages = [{"role": "user", "content": prompt}]
    elif isinstance(prompt, list):
        messages = prompt  # Already in message format
    elif isinstance(prompt, dict):
        messages = [{"role": "user", "content": str(prompt)}]
    else:
        messages = [{"role": "user", "content": str(prompt)}]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=4096,
        )

        return response.choices[0].message.content

    except Exception as e:
        raise RuntimeError(f"Groq API Error: {e}")