import os
from dotenv import load_dotenv
from google import genai

# Load env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("CRITICAL ERROR: GEMINI_API_KEY not found.")
    client = None
else:
    client = genai.Client(api_key=api_key)


DEFAULT_MODEL = "gemini-2.5-flash"


def call_llm_api(prompt, model=DEFAULT_MODEL, temperature=0.2):
    """
    Generic LLM caller for all modules.

    Args:
        prompt (str or dict): Input prompt
        model (str): Gemini model
        temperature (float): Controls randomness

    Returns:
        str: Extracted response text
    """

    if not client:
        raise RuntimeError("GenAI client not configured.")

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "temperature": temperature
            }
        )

        # --- Robust response parsing ---
        if hasattr(response, "text") and response.text:
            return response.text

        elif getattr(response, "candidates", None):
            try:
                candidate = response.candidates[0]
                content = getattr(candidate, "content", None)

                if content and getattr(content, "parts", None):
                    parts = content.parts
                    return "".join([
                        p.text if hasattr(p, "text") else str(p)
                        for p in parts
                    ])

                return str(candidate)

            except Exception:
                return str(response)

        return str(response)

    except Exception as e:
        raise RuntimeError(f"Gemini API Error: {e}")