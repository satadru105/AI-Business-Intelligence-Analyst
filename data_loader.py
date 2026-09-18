import pandas as pd

from modules.schema_detector import infer_business_mapping


def _as_numeric(series):
    """Parse numbers containing currency symbols, commas, or percentages."""
    if pd.api.types.is_numeric_dtype(series):
        return series
    cleaned = (
        series.astype("string")
        .str.replace(r"[^0-9.\-]", "", regex=True)
    )
    return pd.to_numeric(cleaned, errors="coerce")


def standardize_business_schema(df):
    """Add the internal roles used by the analysis modules without losing source columns."""
    standardized = df.copy()
    mapping = infer_business_mapping(standardized)

    for role, source_column in mapping.items():
        if role not in standardized.columns:
            standardized[role] = standardized[source_column]

    numeric_roles = ["Sales", "Profit", "Quantity", "Unit_Price"]
    for role in numeric_roles:
        if role in standardized.columns:
            standardized[role] = _as_numeric(standardized[role])

    if "Sales" not in standardized.columns and {"Quantity", "Unit_Price"}.issubset(standardized.columns):
        standardized["Sales"] = standardized["Quantity"] * standardized["Unit_Price"]

    if "Profit" not in standardized.columns and {"Sales", "Cost"}.issubset(standardized.columns):
        standardized["Profit"] = standardized["Sales"] - _as_numeric(standardized["Cost"])

    return standardized


def load_file(uploaded_file):
    """
    Load CSV or Excel file into a Pandas DataFrame.
    """

    if uploaded_file is None:
        return None

    file_name = uploaded_file.name.lower()

    try:

        if file_name.endswith(".csv"):
            df = pd.read_csv(
                uploaded_file,
                sep=None,
                engine="python",
                encoding_errors="replace"
            )

        elif file_name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)

        elif file_name.endswith(".xls"):
            df = pd.read_excel(uploaded_file)

        else:
            raise ValueError(
                "Unsupported file format. Please upload CSV or Excel."
            )

        return standardize_business_schema(df)

    except Exception as e:
        raise Exception(f"Could not load the file: {e}")