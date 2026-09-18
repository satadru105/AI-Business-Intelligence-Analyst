import pandas as pd
import numpy as np

from modules.analytics import (
    calculate_kpis,
    revenue_by_region,
    revenue_by_category,
    profit_by_product,
    customer_segment_performance
)

from modules.anomaly_detection import get_anomaly_records


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_percentage(value, total):
    if total == 0:
        return 0
    return (value / total) * 100


def add_recommendation(
    recommendations,
    category,
    title,
    priority,
    reason,
    action
):
    recommendations.append({
        "Category": category,
        "Recommendation": title,
        "Priority": priority,
        "Why": reason,
        "Recommended Action": action
    })


# ============================================================
# 1. SALES GROWTH RECOMMENDATIONS
# ============================================================

def generate_sales_recommendations(df, recommendations):

    if "Sales" not in df.columns:
        return

    kpis = calculate_kpis(df)

    total_revenue = kpis["Total Revenue"]

    if total_revenue <= 0:
        return

    # --------------------------------------------------------
    # Region opportunity
    # --------------------------------------------------------

    region_data = revenue_by_region(df)

    if not region_data.empty and len(region_data) >= 2:

        best_region = region_data.iloc[0]
        worst_region = region_data.iloc[-1]

        best_revenue = best_region["Sales"]
        worst_revenue = worst_region["Sales"]

        difference = best_revenue - worst_revenue

        if difference > 0:

            add_recommendation(
                recommendations,
                "Sales Growth",
                f"Improve sales performance in the {worst_region['Region']} region",
                "High",
                f"The {worst_region['Region']} region generated "
                f"₹{worst_revenue:,.2f}, while the top region "
                f"generated ₹{best_revenue:,.2f}.",
                "Review pricing, product availability, customer demand, "
                "sales coverage and promotional activity in this region."
            )

    # --------------------------------------------------------
    # Category opportunity
    # --------------------------------------------------------

    category_data = revenue_by_category(df)

    if not category_data.empty and len(category_data) >= 2:

        best_category = category_data.iloc[0]
        worst_category = category_data.iloc[-1]

        category_share = safe_percentage(
            worst_category["Sales"],
            total_revenue
        )

        if category_share < 15:

            add_recommendation(
                recommendations,
                "Sales Growth",
                f"Increase sales focus on {worst_category['Category']}",
                "Medium",
                f"{worst_category['Category']} contributes only "
                f"{category_share:.2f}% of total revenue.",
                "Test targeted promotions, bundles and cross-selling "
                "campaigns for this category."
            )

    # --------------------------------------------------------
    # Sales concentration
    # --------------------------------------------------------

    if not region_data.empty:

        top_region_share = safe_percentage(
            region_data.iloc[0]["Sales"],
            total_revenue
        )

        if top_region_share > 35:

            add_recommendation(
                recommendations,
                "Sales Growth",
                "Reduce dependency on the top-performing region",
                "Medium",
                f"The {region_data.iloc[0]['Region']} region contributes "
                f"{top_region_share:.2f}% of total revenue.",
                "Develop growth campaigns and distribution strategies "
                "for other regions to diversify revenue."
            )


# ============================================================
# 2. PRODUCT RECOMMENDATIONS
# ============================================================

def generate_product_recommendations(df, recommendations):

    if "Product" not in df.columns or "Sales" not in df.columns:
        return

    product_sales = (
        df.groupby("Product")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    if product_sales.empty or len(product_sales) < 2:
        return

    top_product = product_sales.index[0]
    top_product_sales = product_sales.iloc[0]

    bottom_product = product_sales.index[-1]
    bottom_product_sales = product_sales.iloc[-1]

    # --------------------------------------------------------
    # Top product
    # --------------------------------------------------------

    add_recommendation(
        recommendations,
        "Product",
        f"Expand opportunities for {top_product}",
        "Medium",
        f"{top_product} generated the highest product revenue "
        f"at ₹{top_product_sales:,.2f}.",
        "Consider increasing inventory availability, promotional "
        "visibility and complementary product bundles."
    )

    # --------------------------------------------------------
    # Underperforming product
    # --------------------------------------------------------

    add_recommendation(
        recommendations,
        "Product",
        f"Review the performance of {bottom_product}",
        "High",
        f"{bottom_product} generated the lowest product revenue "
        f"at ₹{bottom_product_sales:,.2f}.",
        "Investigate demand, pricing, product positioning and "
        "customer feedback before deciding whether to improve, "
        "promote or reduce the product."
    )


# ============================================================
# 3. PROFIT RECOMMENDATIONS
# ============================================================

def generate_profit_recommendations(df, recommendations):

    if "Profit" not in df.columns or "Product" not in df.columns:
        return

    product_profit = profit_by_product(df)

    if product_profit.empty:
        return

    most_profitable = product_profit.iloc[0]
    least_profitable = product_profit.iloc[-1]

    # --------------------------------------------------------
    # Most profitable product
    # --------------------------------------------------------

    add_recommendation(
        recommendations,
        "Profit",
        f"Prioritize high-profit product: {most_profitable['Product']}",
        "Medium",
        f"{most_profitable['Product']} generated the highest "
        f"total profit of ₹{most_profitable['Profit']:,.2f}.",
        "Protect inventory availability and explore opportunities "
        "to increase sales volume for this product."
    )

    # --------------------------------------------------------
    # Least profitable product
    # --------------------------------------------------------

    if least_profitable["Profit"] <= 0:

        add_recommendation(
            recommendations,
            "Profit",
            f"Investigate profitability of {least_profitable['Product']}",
            "High",
            f"{least_profitable['Product']} generated "
            f"₹{least_profitable['Profit']:,.2f} profit.",
            "Review unit cost, pricing, discount levels and sales "
            "volume to identify the cause of weak profitability."
        )

    else:

        add_recommendation(
            recommendations,
            "Profit",
            f"Improve margins for {least_profitable['Product']}",
            "Medium",
            f"{least_profitable['Product']} has the lowest total "
            f"profit at ₹{least_profitable['Profit']:,.2f}.",
            "Review pricing and discount policies and identify "
            "ways to reduce product or distribution costs."
        )


# ============================================================
# 4. CUSTOMER SEGMENT RECOMMENDATIONS
# ============================================================

def generate_segment_recommendations(df, recommendations):

    if "Customer_Segment" not in df.columns:
        return

    segment_data = customer_segment_performance(df)

    if segment_data.empty or len(segment_data) < 2:
        return

    best_segment = segment_data.iloc[0]
    worst_segment = segment_data.iloc[-1]

    # --------------------------------------------------------
    # Best segment
    # --------------------------------------------------------

    add_recommendation(
        recommendations,
        "Customer Segment",
        f"Strengthen engagement with {best_segment['Customer_Segment']} customers",
        "Medium",
        f"{best_segment['Customer_Segment']} is the highest-revenue "
        f"customer segment with revenue of "
        f"₹{best_segment['Revenue']:,.2f}.",
        "Create targeted retention campaigns, cross-selling "
        "offers and personalized product recommendations."
    )

    # --------------------------------------------------------
    # Weak segment
    # --------------------------------------------------------

    add_recommendation(
        recommendations,
        "Customer Segment",
        f"Improve engagement with {worst_segment['Customer_Segment']} customers",
        "Medium",
        f"{worst_segment['Customer_Segment']} generated the lowest "
        f"segment revenue at ₹{worst_segment['Revenue']:,.2f}.",
        "Analyze purchasing behavior and test targeted promotions "
        "or personalized offers."
    )


# ============================================================
# 5. ANOMALY-BASED RECOMMENDATIONS
# ============================================================

def generate_anomaly_recommendations(df, recommendations):

    anomaly_records = get_anomaly_records(df)

    if anomaly_records.empty:
        return

    for _, anomaly in anomaly_records.iterrows():

        anomaly_type = anomaly["Anomaly"]
        metric = anomaly["Metric"]
        severity = anomaly["Severity"]

        # ----------------------------------------------------
        # Sales spike
        # ----------------------------------------------------

        if anomaly_type == "Sales Spike":

            priority = "High" if severity == "High" else "Medium"

            add_recommendation(
                recommendations,
                "Anomaly Action",
                f"Investigate sales spike in {metric}",
                priority,
                f"Sales in {metric} were detected as an unusual "
                f"positive deviation.",
                "Identify the drivers behind the increase and "
                "determine whether the growth can be replicated."
            )

        # ----------------------------------------------------
        # Sales drop
        # ----------------------------------------------------

        elif anomaly_type == "Sales Drop":

            add_recommendation(
                recommendations,
                "Anomaly Action",
                f"Investigate sales drop in {metric}",
                "High",
                f"Sales in {metric} were detected as an unusual "
                f"negative deviation.",
                "Check demand, pricing, inventory, promotions, "
                "regional performance and sales-channel activity."
            )

        # ----------------------------------------------------
        # Profit spike
        # ----------------------------------------------------

        elif anomaly_type == "Profit Spike":

            add_recommendation(
                recommendations,
                "Anomaly Action",
                f"Investigate profit spike in {metric}",
                "Medium",
                f"Profit in {metric} was unusually high.",
                "Identify pricing, product mix, cost or sales factors "
                "responsible for the improvement."
            )

        # ----------------------------------------------------
        # Profit drop
        # ----------------------------------------------------

        elif anomaly_type == "Profit Drop":

            add_recommendation(
                recommendations,
                "Anomaly Action",
                f"Investigate profit drop in {metric}",
                "High",
                f"Profit in {metric} was detected as unusually low.",
                "Review discounts, costs, pricing, product mix and "
                "low-margin transactions."
            )

        # ----------------------------------------------------
        # Low region revenue
        # ----------------------------------------------------

        elif anomaly_type == "Low Revenue":

            add_recommendation(
                recommendations,
                "Anomaly Action",
                f"Investigate low revenue in {metric}",
                "High",
                f"The {metric} region has unusually low revenue.",
                "Review regional demand, sales coverage, product "
                "availability and customer acquisition."
            )

        # ----------------------------------------------------
        # High region revenue
        # ----------------------------------------------------

        elif anomaly_type == "High Revenue":

            add_recommendation(
                recommendations,
                "Anomaly Action",
                f"Scale successful strategy in {metric}",
                "Medium",
                f"The {metric} region has unusually high revenue.",
                "Identify successful products, channels and sales "
                "strategies that can be replicated elsewhere."
            )

        # ----------------------------------------------------
        # Low product sales
        # ----------------------------------------------------

        elif anomaly_type == "Low Product Sales":

            add_recommendation(
                recommendations,
                "Anomaly Action",
                f"Review low sales for {metric}",
                "High",
                f"{metric} has unusually low revenue compared "
                f"with other products.",
                "Review pricing, demand, visibility, inventory and "
                "product positioning."
            )

        # ----------------------------------------------------
        # High product sales
        # ----------------------------------------------------

        elif anomaly_type == "High Product Sales":

            add_recommendation(
                recommendations,
                "Anomaly Action",
                f"Scale the high-performing product {metric}",
                "Medium",
                f"{metric} has unusually high revenue.",
                "Maintain inventory and explore opportunities for "
                "bundling, upselling and wider distribution."
            )


# ============================================================
# 6. DATA QUALITY RECOMMENDATIONS
# ============================================================

def generate_data_quality_recommendations(df, recommendations):

    total_cells = df.shape[0] * df.shape[1]

    if total_cells == 0:
        return

    missing_cells = df.isnull().sum().sum()

    missing_percentage = (
        missing_cells / total_cells
    ) * 100

    if missing_percentage > 1:

        add_recommendation(
            recommendations,
            "Data Quality",
            "Improve missing-value handling",
            "High",
            f"The dataset contains {missing_cells:,} missing cells "
            f"({missing_percentage:.2f}% of all cells).",
            "Define appropriate rules for imputing, removing or "
            "reviewing missing values before business decisions."
        )


# ============================================================
# 7. MAIN RECOMMENDATION ENGINE
# ============================================================

def generate_recommendations(df):

    recommendations = []

    if df is None or df.empty:
        return pd.DataFrame(
            columns=[
                "Category",
                "Recommendation",
                "Priority",
                "Why",
                "Recommended Action"
            ]
        )

    # Generate all recommendation categories

    generate_sales_recommendations(
        df,
        recommendations
    )

    generate_product_recommendations(
        df,
        recommendations
    )

    generate_profit_recommendations(
        df,
        recommendations
    )

    generate_segment_recommendations(
        df,
        recommendations
    )

    generate_anomaly_recommendations(
        df,
        recommendations
    )

    generate_data_quality_recommendations(
        df,
        recommendations
    )

    result = pd.DataFrame(recommendations)

    if result.empty:
        return result

    # Priority ordering

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    result["Priority Order"] = (
        result["Priority"]
        .map(priority_order)
        .fillna(4)
    )

    result = result.sort_values(
        "Priority Order"
    ).drop(
        columns=["Priority Order"]
    )

    result = result.reset_index(drop=True)

    return result


# ============================================================
# 8. SUMMARY
# ============================================================

def generate_recommendation_summary(df):

    recommendations = generate_recommendations(df)

    if recommendations.empty:

        return {
            "total": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

    return {
        "total": len(recommendations),

        "high": (
            recommendations["Priority"] == "High"
        ).sum(),

        "medium": (
            recommendations["Priority"] == "Medium"
        ).sum(),

        "low": (
            recommendations["Priority"] == "Low"
        ).sum()
    }