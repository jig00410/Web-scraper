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


# Recommended fast model
DEFAULT_MODEL = "llama-3.3-70b-versatile"


def call_llm_api(prompt, model=DEFAULT_MODEL, temperature=0.2):
    """
    Generic LLM caller using Groq

    Args:
        prompt (str): Input prompt
        model (str): Groq model
        temperature (float): Controls randomness

    Returns:
        str: Extracted response text
    """

    if not client:
        raise RuntimeError("Groq client not configured.")

    try:
        # Convert prompt → chat format
        messages = [
            {"role": "user", "content": str(prompt)}
        ]

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )

        # Extract text
        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"Groq API Error: {e}")