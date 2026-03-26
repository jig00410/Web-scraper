import json
from llm.groq_client import call_llm_api

def analyze_dataset(df):
    """
    Full LLM-driven data analysis engine
    """

    if df is None or df.empty:
        return "No data available."

    try:
        sample = df.head(25).to_dict(orient="records")
        columns = list(df.columns)

        prompt = f"""
You are a senior data analyst.

Dataset columns:
{columns}

Sample data:
{json.dumps(sample, indent=2)}

Perform COMPLETE analysis:

1. Overview of dataset
2. Key patterns
3. Trends
4. Anomalies / outliers
5. Relationships between columns
6. Business insights
7. Actionable recommendations

Format clearly:

=== Overview ===
...
=== Patterns ===
...
=== Trends ===
...
=== Anomalies ===
...
=== Relationships ===
...
=== Insights ===
...
=== Recommendations ===
...
"""

        return call_llm_api(prompt)

    except Exception as e:
        return f"Analysis failed: {str(e)}"