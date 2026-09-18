import pandas as pd
import numpy as np


# =========================================================
# 1. BASIC DATA QUALITY CHECK
# =========================================================

def check_missing_values(df):
    """
    Find missing values in every column.
    """

    missing = df.isnull().sum()

    result = pd.DataFrame({
        "Column": missing.index,
        "Missing Values": missing.values,
        "Missing %": (
            (missing.values / len(df)) * 100
        ).round(2)
    })

    result = result[
        result["Missing Values"] > 0
    ].sort_values(
        "Missing Values",
        ascending=False
    )

    return result


# =========================================================
# 2. DUPLICATE ROW CHECK
# =========================================================

def check_duplicates(df):
    """
    Count duplicate rows.
    """

    duplicate_count = df.duplicated().sum()

    return duplicate_count


# =========================================================
# 3. DUPLICATE ID CHECK
# =========================================================

def check_duplicate_ids(df):
    """
    Check common ID columns for duplicate values.
    """

    possible_id_columns = [
        "Order_ID",
        "Customer_ID",
        "Employee_ID",
        "Product_ID",
        "Transaction_ID"
    ]

    results = []

    for column in possible_id_columns:

        if column in df.columns:

            duplicate_count = (
                df[column].duplicated().sum()
            )

            results.append({
                "Column": column,
                "Duplicate Values": duplicate_count
            })

    return pd.DataFrame(results)


# =========================================================
# 4. TEXT CONSISTENCY CHECK
# =========================================================

def check_text_consistency(df):
    """
    Detect values that differ only by capitalization
    or surrounding spaces.

    Example:
        North
        north
        NORTH
    """

    results = []

    text_columns = df.select_dtypes(
        include=["object"]
    ).columns

    for column in text_columns:

        values = (
            df[column]
            .dropna()
            .astype(str)
        )

        normalized = (
            values
            .str.strip()
            .str.lower()
        )

        grouped = (
            pd.DataFrame({
                "Original": values,
                "Normalized": normalized
            })
            .groupby("Normalized")["Original"]
            .nunique()
        )

        inconsistent_count = (
            (grouped > 1).sum()
        )

        if inconsistent_count > 0:

            results.append({
                "Column": column,
                "Inconsistent Groups":
                    inconsistent_count
            })

    return pd.DataFrame(results)


# =========================================================
# 5. NUMERIC OUTLIER CHECK
# =========================================================

def check_outliers(df):
    """
    Detect numeric outliers using the IQR method.
    """

    results = []

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns

    for column in numeric_columns:

        series = df[column].dropna()

        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = (
            (series < lower_bound) |
            (series > upper_bound)
        )

        outlier_count = outliers.sum()

        if outlier_count > 0:

            results.append({
                "Column": column,
                "Outliers": int(outlier_count),
                "Lower Bound": round(
                    lower_bound,
                    2
                ),
                "Upper Bound": round(
                    upper_bound,
                    2
                )
            })

    return pd.DataFrame(results)


# =========================================================
# 6. DATE VALIDATION
# =========================================================

def check_date_columns(df):
    """
    Detect columns that appear to contain dates
    and count invalid date values.
    """

    results = []

    for column in df.columns:

        column_name = column.lower()

        if (
            "date" in column_name or
            "time" in column_name
        ):

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            invalid_count = (
                converted.isna() &
                df[column].notna()
            ).sum()

            results.append({
                "Column": column,
                "Invalid Dates":
                    int(invalid_count)
            })

    return pd.DataFrame(results)


# =========================================================
# 7. DATA QUALITY SCORE
# =========================================================

def calculate_quality_score(df):
    """
    Calculate an overall data quality score out of 100.
    """

    if len(df) == 0:
        return 0

    score = 100.0

    total_cells = (
        df.shape[0] *
        df.shape[1]
    )

    # -----------------------------------------------------
    # Missing values penalty
    # -----------------------------------------------------

    missing_cells = (
        df.isnull().sum().sum()
    )

    missing_percentage = (
        missing_cells /
        total_cells
    ) * 100

    score -= min(
        missing_percentage * 2,
        25
    )

    # -----------------------------------------------------
    # Duplicate penalty
    # -----------------------------------------------------

    duplicate_rows = (
        df.duplicated().sum()
    )

    duplicate_percentage = (
        duplicate_rows /
        len(df)
    ) * 100

    score -= min(
        duplicate_percentage * 2,
        20
    )

    # -----------------------------------------------------
    # Outlier penalty
    # -----------------------------------------------------

    outlier_result = check_outliers(df)

    if not outlier_result.empty:

        total_outliers = (
            outlier_result["Outliers"]
            .sum()
        )

        outlier_percentage = (
            total_outliers /
            len(df)
        ) * 100

        score -= min(
            outlier_percentage,
            15
        )

    # Keep score between 0 and 100
    score = max(
        0,
        min(100, score)
    )

    return round(score, 1)


# =========================================================
# 8. QUALITY STATUS
# =========================================================

def get_quality_status(score):
    """
    Convert numerical score into readable status.
    """

    if score >= 90:
        return "Excellent"

    elif score >= 75:
        return "Good"

    elif score >= 60:
        return "Needs Improvement"

    else:
        return "Poor"


# =========================================================
# 9. AUTOMATIC CLEANING
# =========================================================

def clean_dataset(df):
    """
    Perform safe automatic cleaning:
    - Remove duplicate rows
    - Strip text spaces
    - Standardize text capitalization
    """

    cleaned_df = df.copy()

    # -----------------------------------------------------
    # Remove duplicate rows
    # -----------------------------------------------------

    cleaned_df = (
        cleaned_df
        .drop_duplicates()
        .reset_index(drop=True)
    )

    # -----------------------------------------------------
    # Clean text columns
    # -----------------------------------------------------

    text_columns = cleaned_df.select_dtypes(
        include=["object"]
    ).columns

    for column in text_columns:

        cleaned_df[column] = (
            cleaned_df[column]
            .apply(
                lambda x:
                x.strip()
                if isinstance(x, str)
                else x
            )
        )

    # -----------------------------------------------------
    # Standardize known categorical columns
    # -----------------------------------------------------

    categorical_columns = [
        "Region",
        "Customer_Segment",
        "Sales_Channel",
        "Payment_Method",
        "Category"
    ]

    for column in categorical_columns:

        if column in cleaned_df.columns:

            cleaned_df[column] = (
                cleaned_df[column]
                .apply(
                    lambda x:
                    x.title()
                    if isinstance(x, str)
                    else x
                )
            )

    return cleaned_df


# =========================================================
# 10. GENERATE QUALITY SUMMARY
# =========================================================

def generate_quality_summary(df):
    """
    Generate all quality checks together.
    """

    summary = {

        "missing": check_missing_values(df),

        "duplicates":
            check_duplicates(df),

        "duplicate_ids":
            check_duplicate_ids(df),

        "inconsistencies":
            check_text_consistency(df),

        "outliers":
            check_outliers(df),

        "invalid_dates":
            check_date_columns(df),

    }

    summary["score"] = (
        calculate_quality_score(df)
    )

    summary["status"] = (
        get_quality_status(
            summary["score"]
        )
    )

    return summary