import pandas as pd


# =========================================================
# KPI CALCULATIONS
# =========================================================

def calculate_kpis(df):
    """
    Calculate the main business KPIs.
    """

    total_revenue = (
        df["Sales"].sum()
        if "Sales" in df.columns
        else 0
    )

    total_profit = (
        df["Profit"].sum()
        if "Profit" in df.columns
        else 0
    )

    total_orders = (
        df["Order_ID"].nunique()
        if "Order_ID" in df.columns
        else len(df)
    )

    total_quantity = (
        df["Quantity"].sum()
        if "Quantity" in df.columns
        else 0
    )

    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
    )

    profit_margin = (
        (total_profit / total_revenue) * 100
        if total_revenue > 0
        else 0
    )

    return {
        "Total Revenue": total_revenue,
        "Total Profit": total_profit,
        "Total Orders": total_orders,
        "Total Quantity": total_quantity,
        "Average Order Value": average_order_value,
        "Profit Margin": profit_margin
    }


# =========================================================
# REVENUE BY REGION
# =========================================================

def revenue_by_region(df):

    if "Region" not in df.columns:
        return pd.DataFrame()

    result = (
        df.groupby("Region", dropna=False)["Sales"]
        .sum()
        .reset_index()
        .sort_values(
            "Sales",
            ascending=False
        )
    )

    return result


# =========================================================
# REVENUE BY CATEGORY
# =========================================================

def revenue_by_category(df):

    if "Category" not in df.columns:
        return pd.DataFrame()

    result = (
        df.groupby("Category", dropna=False)["Sales"]
        .sum()
        .reset_index()
        .sort_values(
            "Sales",
            ascending=False
        )
    )

    return result


# =========================================================
# PROFIT BY PRODUCT
# =========================================================

def profit_by_product(df):

    if "Product" not in df.columns or "Profit" not in df.columns:
        return pd.DataFrame()

    result = (
        df.groupby("Product", dropna=False)["Profit"]
        .sum()
        .reset_index()
        .sort_values(
            "Profit",
            ascending=False
        )
    )

    return result


# =========================================================
# MONTHLY SALES TREND
# =========================================================

def monthly_sales(df):

    if "Order_Date" not in df.columns:
        return pd.DataFrame()

    temp = df.copy()

    temp["Order_Date"] = pd.to_datetime(
        temp["Order_Date"],
        errors="coerce"
    )

    temp = temp.dropna(
        subset=["Order_Date"]
    )

    temp["Month"] = (
        temp["Order_Date"]
        .dt.to_period("M")
        .astype(str)
    )

    result = (
        temp.groupby("Month")["Sales"]
        .sum()
        .reset_index()
    )

    return result


# =========================================================
# TOP 10 PRODUCTS
# =========================================================

def top_products(df, n=10):

    if "Product" not in df.columns:
        return pd.DataFrame()

    result = (
        df.groupby("Product")["Sales"]
        .sum()
        .reset_index()
        .sort_values(
            "Sales",
            ascending=False
        )
        .head(n)
    )

    return result


# =========================================================
# BEST & WORST REGION
# =========================================================

def region_performance(df):

    result = revenue_by_region(df)

    if result.empty:
        return {
            "best_region": None,
            "worst_region": None
        }

    best_region = result.iloc[0]["Region"]
    worst_region = result.iloc[-1]["Region"]

    return {
        "best_region": best_region,
        "worst_region": worst_region
    }


# =========================================================
# CUSTOMER SEGMENT PERFORMANCE
# =========================================================

def customer_segment_performance(df):

    if "Customer_Segment" not in df.columns:
        return pd.DataFrame()

    result = (
        df.groupby(
            "Customer_Segment",
            dropna=False
        )
        .agg(
            Revenue=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order_ID", "nunique")
            if "Order_ID" in df.columns
            else ("Sales", "count")
        )
        .reset_index()
        .sort_values(
            "Revenue",
            ascending=False
        )
    )

    return result


# =========================================================
# COMPLETE ANALYTICS ENGINE
# =========================================================

def generate_analytics(df):

    kpis = calculate_kpis(df)

    return {
        "kpis": kpis,
        "region": revenue_by_region(df),
        "category": revenue_by_category(df),
        "product_profit": profit_by_product(df),
        "monthly": monthly_sales(df),
        "top_products": top_products(df),
        "regions": region_performance(df),
        "segments": customer_segment_performance(df)
    }