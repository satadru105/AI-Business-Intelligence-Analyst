import pandas as pd
import numpy as np


# ============================================================
# 1. SALES ANOMALY DETECTION
# ============================================================

def detect_sales_anomalies(df):
    """
    Detect unusual monthly sales using the IQR method.
    """

    if "Order_Date" not in df.columns or "Sales" not in df.columns:
        return pd.DataFrame()

    temp = df.copy()

    temp["Order_Date"] = pd.to_datetime(
        temp["Order_Date"],
        errors="coerce"
    )

    temp = temp.dropna(subset=["Order_Date"])

    if temp.empty:
        return pd.DataFrame()

    temp["Month"] = temp["Order_Date"].dt.to_period("M").astype(str)

    monthly_sales = (
        temp.groupby("Month")["Sales"]
        .sum()
        .reset_index()
    )

    if len(monthly_sales) < 4:
        return pd.DataFrame()

    q1 = monthly_sales["Sales"].quantile(0.25)
    q3 = monthly_sales["Sales"].quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    monthly_sales["Anomaly"] = (
        (monthly_sales["Sales"] < lower_bound)
        |
        (monthly_sales["Sales"] > upper_bound)
    )

    monthly_sales["Anomaly Type"] = np.where(
        monthly_sales["Sales"] > upper_bound,
        "Sales Spike",
        np.where(
            monthly_sales["Sales"] < lower_bound,
            "Sales Drop",
            "Normal"
        )
    )

    monthly_sales["Severity"] = monthly_sales.apply(
        lambda row: calculate_severity(
            row["Sales"],
            lower_bound,
            upper_bound
        ),
        axis=1
    )

    return monthly_sales


# ============================================================
# 2. PROFIT ANOMALY DETECTION
# ============================================================

def detect_profit_anomalies(df):
    """
    Detect unusual monthly profit.
    """

    if "Order_Date" not in df.columns or "Profit" not in df.columns:
        return pd.DataFrame()

    temp = df.copy()

    temp["Order_Date"] = pd.to_datetime(
        temp["Order_Date"],
        errors="coerce"
    )

    temp = temp.dropna(subset=["Order_Date"])

    if temp.empty:
        return pd.DataFrame()

    temp["Month"] = temp["Order_Date"].dt.to_period("M").astype(str)

    monthly_profit = (
        temp.groupby("Month")["Profit"]
        .sum()
        .reset_index()
    )

    if len(monthly_profit) < 4:
        return pd.DataFrame()

    q1 = monthly_profit["Profit"].quantile(0.25)
    q3 = monthly_profit["Profit"].quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    monthly_profit["Anomaly"] = (
        (monthly_profit["Profit"] < lower_bound)
        |
        (monthly_profit["Profit"] > upper_bound)
    )

    monthly_profit["Anomaly Type"] = np.where(
        monthly_profit["Profit"] > upper_bound,
        "Profit Spike",
        np.where(
            monthly_profit["Profit"] < lower_bound,
            "Profit Drop",
            "Normal"
        )
    )

    monthly_profit["Severity"] = monthly_profit.apply(
        lambda row: calculate_severity(
            row["Profit"],
            lower_bound,
            upper_bound
        ),
        axis=1
    )

    return monthly_profit


# ============================================================
# 3. REGION ANOMALY DETECTION
# ============================================================

def detect_region_anomalies(df):
    """
    Detect regions with unusually high or low revenue.
    """

    if "Region" not in df.columns or "Sales" not in df.columns:
        return pd.DataFrame()

    region_sales = (
        df.groupby("Region", dropna=False)["Sales"]
        .sum()
        .reset_index()
    )

    if len(region_sales) < 4:
        return pd.DataFrame()

    q1 = region_sales["Sales"].quantile(0.25)
    q3 = region_sales["Sales"].quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    region_sales["Anomaly"] = (
        (region_sales["Sales"] < lower_bound)
        |
        (region_sales["Sales"] > upper_bound)
    )

    region_sales["Anomaly Type"] = np.where(
        region_sales["Sales"] > upper_bound,
        "High Revenue",
        np.where(
            region_sales["Sales"] < lower_bound,
            "Low Revenue",
            "Normal"
        )
    )

    region_sales["Severity"] = region_sales.apply(
        lambda row: calculate_severity(
            row["Sales"],
            lower_bound,
            upper_bound
        ),
        axis=1
    )

    return region_sales.sort_values(
        "Sales",
        ascending=False
    )


# ============================================================
# 4. PRODUCT ANOMALY DETECTION
# ============================================================

def detect_product_anomalies(df):
    """
    Detect unusually high or low product revenue.
    """

    if "Product" not in df.columns or "Sales" not in df.columns:
        return pd.DataFrame()

    product_sales = (
        df.groupby("Product", dropna=False)["Sales"]
        .sum()
        .reset_index()
    )

    if len(product_sales) < 4:
        return pd.DataFrame()

    q1 = product_sales["Sales"].quantile(0.25)
    q3 = product_sales["Sales"].quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    product_sales["Anomaly"] = (
        (product_sales["Sales"] < lower_bound)
        |
        (product_sales["Sales"] > upper_bound)
    )

    product_sales["Anomaly Type"] = np.where(
        product_sales["Sales"] > upper_bound,
        "High Product Sales",
        np.where(
            product_sales["Sales"] < lower_bound,
            "Low Product Sales",
            "Normal"
        )
    )

    product_sales["Severity"] = product_sales.apply(
        lambda row: calculate_severity(
            row["Sales"],
            lower_bound,
            upper_bound
        ),
        axis=1
    )

    return product_sales.sort_values(
        "Sales",
        ascending=False
    )


# ============================================================
# 5. SEVERITY CALCULATION
# ============================================================

def calculate_severity(value, lower_bound, upper_bound):

    if value < lower_bound or value > upper_bound:

        distance_from_range = min(
            abs(value - lower_bound),
            abs(value - upper_bound)
        )

        range_size = max(
            abs(upper_bound - lower_bound),
            1
        )

        anomaly_strength = (
            distance_from_range / range_size
        )

        if anomaly_strength >= 1:
            return "High"

        elif anomaly_strength >= 0.5:
            return "Medium"

        else:
            return "Low"

    return "Normal"


# ============================================================
# 6. DETECT ALL ANOMALIES
# ============================================================

def detect_all_anomalies(df):

    sales_anomalies = detect_sales_anomalies(df)

    profit_anomalies = detect_profit_anomalies(df)

    region_anomalies = detect_region_anomalies(df)

    product_anomalies = detect_product_anomalies(df)

    return {
        "sales": sales_anomalies,
        "profit": profit_anomalies,
        "region": region_anomalies,
        "product": product_anomalies
    }


# ============================================================
# 7. GET ONLY ANOMALOUS RECORDS
# ============================================================

def get_anomaly_records(df):

    all_anomalies = detect_all_anomalies(df)

    records = []

    for anomaly_type, result in all_anomalies.items():

        if result.empty:
            continue

        if "Anomaly" not in result.columns:
            continue

        anomalies = result[
            result["Anomaly"] == True
        ].copy()

        if anomalies.empty:
            continue

        for _, row in anomalies.iterrows():

            if anomaly_type == "sales":

                records.append({
                    "Type": "Sales",
                    "Metric": row["Month"],
                    "Value": row["Sales"],
                    "Anomaly": row["Anomaly Type"],
                    "Severity": row["Severity"]
                })

            elif anomaly_type == "profit":

                records.append({
                    "Type": "Profit",
                    "Metric": row["Month"],
                    "Value": row["Profit"],
                    "Anomaly": row["Anomaly Type"],
                    "Severity": row["Severity"]
                })

            elif anomaly_type == "region":

                records.append({
                    "Type": "Region",
                    "Metric": row["Region"],
                    "Value": row["Sales"],
                    "Anomaly": row["Anomaly Type"],
                    "Severity": row["Severity"]
                })

            elif anomaly_type == "product":

                records.append({
                    "Type": "Product",
                    "Metric": row["Product"],
                    "Value": row["Sales"],
                    "Anomaly": row["Anomaly Type"],
                    "Severity": row["Severity"]
                })

    return pd.DataFrame(records)


# ============================================================
# 8. ANOMALY SUMMARY
# ============================================================

def generate_anomaly_summary(df):

    records = get_anomaly_records(df)

    if records.empty:

        return {
            "total": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

    return {
        "total": len(records),

        "high": (
            records["Severity"] == "High"
        ).sum(),

        "medium": (
            records["Severity"] == "Medium"
        ).sum(),

        "low": (
            records["Severity"] == "Low"
        ).sum()
    }