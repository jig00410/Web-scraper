import json
from llm.gemini_client import call_llm_api


def process_extracted_data(query, extracted_data):
    prompt = f"""
User Query:
{query}

Extracted Data:
{json.dumps(extracted_data)[:15000]}

Task:
- Clean and structure the data
- Remove duplicates
- Format into clear structured JSON

STRICT: Return ONLY JSON.
"""

    response_text = call_llm_api(prompt)

    try:
        return json.loads(response_text)
    except Exception:
        return response_text