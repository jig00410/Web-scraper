import pandas as pd

def refine_structured_data(json_data):
    """
    Converts LLM JSON → Clean Pandas DataFrame safely

    Handles:
    - Empty or invalid input
    - Mixed key types (int, str, None)
    - Messy price formats (₹, $, commas)
    - LLM inconsistent outputs
    - Prevents crashes like: 'int' object has no attribute 'lower'
    """

    # -------------------------
    # 0. Validate input
    # -------------------------
    if not json_data or not isinstance(json_data, list):
        return pd.DataFrame()

    # -------------------------
    # 1. Normalize keys (CRITICAL FIX)
    # Convert all keys → strings
    # -------------------------
    cleaned_data = []

    for item in json_data:
        if isinstance(item, dict):
            cleaned_item = {}
            for k, v in item.items():
                try:
                    cleaned_item[str(k)] = v
                except:
                    cleaned_item["unknown"] = v
            cleaned_data.append(cleaned_item)

    if not cleaned_data:
        return pd.DataFrame()

    df = pd.DataFrame(cleaned_data)

    if df.empty:
        return df

    # -------------------------
    # 2. Clean whitespace
    # -------------------------
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].map(
                lambda x: x.strip() if isinstance(x, str) else x
            )

    # -------------------------
    # 3. Detect price columns safely
    # -------------------------
    price_keywords = ['price', 'cost', 'amount', 'fee', 'mrp', 'value', 'rate']

    price_cols = []
    for col in df.columns:
        if isinstance(col, str):
            col_lower = col.lower()
            if any(k in col_lower for k in price_keywords):
                price_cols.append(col)

    # -------------------------
    # 4. Clean price columns
    # -------------------------
    for col in price_cols:
        df[col] = (
            df[col]
            .astype(str)
            .replace(r'[₹$€£,]', '', regex=True)
        )
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # -------------------------
    # 5. Remove invalid rows safely
    # -------------------------
    if len(df.columns) > 0:
        first_col = df.columns[0]

        df = df[df[first_col].notna()]
        df = df[df[first_col].astype(str).str.strip() != ""]
        df = df[df[first_col].astype(str).str.lower() != "n/a"]

    # -------------------------
    # 6. Fill numeric NaN
    # -------------------------
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(0.0)

    # -------------------------
    # 7. Drop duplicates
    # -------------------------
    df = df.drop_duplicates()

    # -------------------------
    # 8. Reset index
    # -------------------------
    df = df.reset_index(drop=True)

    return df