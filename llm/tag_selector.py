import json
from llm.gemini_client import call_llm_api


def select_relevant_tags(query, tag_tree):
    prompt = f"""
You are an intelligent HTML analyzer.

User Query:
{query}

Tag Tree (JSON):
{json.dumps(tag_tree)[:15000]}

Task:
- Identify ONLY the most relevant tags for extracting the requested data
- Return a JSON list in format:
[
  {{"tag": "div", "attrs": {{"class": "price"}}}},
  {{"tag": "span", "attrs": {{"id": "title"}}}}
]

STRICT: Return ONLY JSON. No explanation.
"""

    response_text = call_llm_api(prompt)

    try:
        return json.loads(response_text)
    except Exception:
        return []