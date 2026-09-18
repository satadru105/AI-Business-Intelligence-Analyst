import pandas as pd
import re


ROLE_ALIASES = {
    "Order_ID": ["order id", "order number", "transaction id", "invoice id", "invoice number", "order no"],
    "Order_Date": ["order date", "transaction date", "invoice date", "sale date", "date", "created at", "timestamp"],
    "Sales": ["sales", "sale", "revenue", "amount", "total", "turnover", "net sales", "gross sales", "value"],
    "Profit": ["profit", "gross profit", "net profit", "margin amount", "earnings"],
    "Quantity": ["quantity", "qty", "units", "unit sold", "volume", "count"],
    "Unit_Price": ["unit price", "price", "selling price", "rate", "unit cost"],
    "Product": ["product", "item", "item name", "product name", "sku", "stock item", "service"],
    "Category": ["category", "product category", "department", "type", "class", "line of business"],
    "Region": ["region", "territory", "area", "state", "province", "country", "market", "location"],
    "Customer_Segment": ["customer segment", "segment", "customer type", "client type"],
}


def _normalise_name(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def infer_business_mapping(df):
    """Infer common business roles from flexible CSV column names."""
    mapping = {}
    used = set()
    normalised_columns = {
        column: _normalise_name(column)
        for column in df.columns
    }

    for role, aliases in ROLE_ALIASES.items():
        candidates = aliases + [role]
        for column, normalised in normalised_columns.items():
            if column in used:
                continue
            if normalised in candidates:
                mapping[role] = column
                used.add(column)
                break

    numeric_columns = [
        column for column in df.select_dtypes(include="number").columns
        if column not in used
    ]

    if "Sales" not in mapping and numeric_columns:
        mapping["Sales"] = numeric_columns[0]
        used.add(numeric_columns[0])

    if "Order_Date" not in mapping:
        for column in df.columns:
            normalised = _normalise_name(column)
            if not any(token in normalised for token in ["date", "time", "period"]):
                continue
            if not (
                pd.api.types.is_object_dtype(df[column])
                or pd.api.types.is_string_dtype(df[column])
            ):
                continue
            converted = pd.to_datetime(df[column], errors="coerce")
            if converted.notna().mean() >= 0.8:
                mapping["Order_Date"] = column
                break

    categorical_columns = [
        column for column in df.select_dtypes(exclude="number").columns
        if column not in used and column != mapping.get("Order_Date")
    ]

    if "Product" not in mapping and categorical_columns:
        mapping["Product"] = categorical_columns[0]

    return mapping


def detect_schema(df):

    schema = {
        "numeric_columns": [],
        "categorical_columns": [],
        "date_columns": [],
        "text_columns": [],
        "business_mapping": infer_business_mapping(df)
    }

    for column in df.columns:

        series = df[column]

        # Numeric
        if pd.api.types.is_numeric_dtype(series):
            schema["numeric_columns"].append(column)
            continue

        # Try date detection
        if pd.api.types.is_datetime64_any_dtype(series):
            schema["date_columns"].append(column)
            continue

        # Try converting object columns to dates
        if series.dtype == "object":

            converted = pd.to_datetime(
                series,
                errors="coerce"
            )

            if converted.notna().mean() >= 0.8:
                schema["date_columns"].append(column)
                continue

        # Categorical
        unique_ratio = (
            series.nunique(dropna=True) /
            max(len(series), 1)
        )

        if unique_ratio <= 0.5:
            schema["categorical_columns"].append(column)
        else:
            schema["text_columns"].append(column)

    return schema