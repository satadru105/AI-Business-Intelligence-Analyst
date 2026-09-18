
import pandas as pd


# =========================================================
# BASIC BUSINESS CALCULATIONS
# =========================================================

def get_basic_summary(df):

    summary = {}

    if "Sales" in df.columns:
        summary["total_revenue"] = df["Sales"].sum()
    else:
        summary["total_revenue"] = 0

    if "Profit" in df.columns:
        summary["total_profit"] = df["Profit"].sum()
    else:
        summary["total_profit"] = 0

    if "Order_ID" in df.columns:
        summary["total_orders"] = df["Order_ID"].nunique()
    else:
        summary["total_orders"] = len(df)

    if "Quantity" in df.columns:
        summary["total_quantity"] = df["Quantity"].sum()
    else:
        summary["total_quantity"] = 0

    if summary["total_orders"] > 0:
        summary["average_order_value"] = (
            summary["total_revenue"]
            / summary["total_orders"]
        )
    else:
        summary["average_order_value"] = 0

    if summary["total_revenue"] > 0:
        summary["profit_margin"] = (
            summary["total_profit"]
            / summary["total_revenue"]
        ) * 100
    else:
        summary["profit_margin"] = 0

    return summary


# =========================================================
# REGION ANALYSIS
# =========================================================

def analyze_regions(df):

    if "Region" not in df.columns or "Sales" not in df.columns:
        return None

    result = (
        df.groupby("Region", dropna=False)["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    if result.empty:
        return None

    best_region = result.index[0]
    best_revenue = result.iloc[0]

    worst_region = result.index[-1]
    worst_revenue = result.iloc[-1]

    return {
        "best_region": best_region,
        "best_revenue": best_revenue,
        "worst_region": worst_region,
        "worst_revenue": worst_revenue,
        "table": result
    }


# =========================================================
# PRODUCT ANALYSIS
# =========================================================

def analyze_products(df):

    if "Product" not in df.columns:
        return None

    result = {}

    if "Sales" in df.columns:

        sales_by_product = (
            df.groupby("Product")["Sales"]
            .sum()
            .sort_values(ascending=False)
        )

        result["sales"] = sales_by_product

        if not sales_by_product.empty:

            result["best_product"] = sales_by_product.index[0]
            result["best_product_sales"] = sales_by_product.iloc[0]

            result["worst_product"] = sales_by_product.index[-1]
            result["worst_product_sales"] = sales_by_product.iloc[-1]

    if "Profit" in df.columns:

        profit_by_product = (
            df.groupby("Product")["Profit"]
            .sum()
            .sort_values(ascending=False)
        )

        result["profit"] = profit_by_product

        if not profit_by_product.empty:

            result["most_profitable_product"] = (
                profit_by_product.index[0]
            )

            result["highest_product_profit"] = (
                profit_by_product.iloc[0]
            )

            result["least_profitable_product"] = (
                profit_by_product.index[-1]
            )

            result["lowest_product_profit"] = (
                profit_by_product.iloc[-1]
            )

    return result


# =========================================================
# CUSTOMER SEGMENT ANALYSIS
# =========================================================

def analyze_segments(df):

    if (
        "Customer_Segment" not in df.columns
        or "Sales" not in df.columns
    ):
        return None

    result = (
        df.groupby("Customer_Segment", dropna=False)
        .agg(
            Revenue=("Sales", "sum"),
            Profit=("Profit", "sum")
            if "Profit" in df.columns
            else ("Sales", "sum")
        )
        .sort_values("Revenue", ascending=False)
    )

    if result.empty:
        return None

    best_segment = result.index[0]

    return {
        "best_segment": best_segment,
        "table": result
    }


# =========================================================
# MONTHLY SALES ANALYSIS
# =========================================================

def analyze_monthly_sales(df):

    if (
        "Order_Date" not in df.columns
        or "Sales" not in df.columns
    ):
        return None

    temp = df.copy()

    temp["Order_Date"] = pd.to_datetime(
        temp["Order_Date"],
        errors="coerce"
    )

    temp = temp.dropna(
        subset=["Order_Date"]
    )

    if temp.empty:
        return None

    temp["Month"] = (
        temp["Order_Date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly = (
        temp.groupby("Month")["Sales"]
        .sum()
        .sort_index()
    )

    if monthly.empty:
        return None

    highest_month = monthly.idxmax()
    lowest_month = monthly.idxmin()

    # Compare first and last month
    if len(monthly) >= 2:

        first_month = monthly.iloc[0]
        last_month = monthly.iloc[-1]

        if first_month != 0:

            change_percentage = (
                (last_month - first_month)
                / first_month
            ) * 100

        else:
            change_percentage = 0

    else:
        change_percentage = 0

    return {
        "monthly": monthly,
        "highest_month": highest_month,
        "highest_month_sales": monthly.max(),
        "lowest_month": lowest_month,
        "lowest_month_sales": monthly.min(),
        "change_percentage": change_percentage
    }


# =========================================================
# BUSINESS INSIGHTS
# =========================================================

def generate_business_insights(df):

    insights = []

    summary = get_basic_summary(df)

    # Revenue insight
    insights.append(
        f"Total revenue is ₹{summary['total_revenue']:,.2f} "
        f"across {summary['total_orders']:,} orders."
    )

    # Profit insight
    insights.append(
        f"Total profit is ₹{summary['total_profit']:,.2f}, "
        f"with a profit margin of "
        f"{summary['profit_margin']:.2f}%."
    )

    # Region insight
    region_analysis = analyze_regions(df)

    if region_analysis:

        insights.append(
            f"{region_analysis['best_region']} is the "
            f"highest-revenue region with revenue of "
            f"₹{region_analysis['best_revenue']:,.2f}."
        )

        insights.append(
            f"{region_analysis['worst_region']} is the "
            f"lowest-revenue region with revenue of "
            f"₹{region_analysis['worst_revenue']:,.2f}."
        )

    # Product insight
    product_analysis = analyze_products(df)

    if product_analysis:

        if "best_product" in product_analysis:

            insights.append(
                f"{product_analysis['best_product']} is the "
                f"top product by revenue, generating "
                f"₹{product_analysis['best_product_sales']:,.2f}."
            )

        if "most_profitable_product" in product_analysis:

            insights.append(
                f"{product_analysis['most_profitable_product']} "
                f"is the most profitable product with profit "
                f"of ₹{product_analysis['highest_product_profit']:,.2f}."
            )

    # Segment insight
    segment_analysis = analyze_segments(df)

    if segment_analysis:

        insights.append(
            f"{segment_analysis['best_segment']} is the "
            f"highest-revenue customer segment."
        )

    # Monthly insight
    monthly_analysis = analyze_monthly_sales(df)

    if monthly_analysis:

        insights.append(
            f"{monthly_analysis['highest_month']} recorded "
            f"the highest monthly revenue of "
            f"₹{monthly_analysis['highest_month_sales']:,.2f}."
        )

        if len(monthly_analysis["monthly"]) >= 2:

            change = monthly_analysis["change_percentage"]

            if change > 0:

                insights.append(
                    f"Revenue increased by approximately "
                    f"{change:.2f}% from the first month "
                    f"to the last month."
                )

            elif change < 0:

                insights.append(
                    f"Revenue decreased by approximately "
                    f"{abs(change):.2f}% from the first month "
                    f"to the last month."
                )

            else:

                insights.append(
                    "Revenue remained approximately stable "
                    "between the first and last month."
                )

    return insights


# =========================================================
# QUESTION ANSWERING ENGINE
# =========================================================

def answer_question(df, question):

    question = question.lower().strip()

    summary = get_basic_summary(df)


    # -----------------------------------------------------
    # TOTAL REVENUE
    # -----------------------------------------------------

    if (
        "total revenue" in question
        or "total sales" in question
        or "how much revenue" in question
    ):

        return (
            f"💰 Total revenue is "
            f"₹{summary['total_revenue']:,.2f}."
        )


    # -----------------------------------------------------
    # TOTAL PROFIT
    # -----------------------------------------------------

    if (
        "total profit" in question
        or "how much profit" in question
    ):

        return (
            f"📈 Total profit is "
            f"₹{summary['total_profit']:,.2f}."
        )


    # -----------------------------------------------------
    # TOTAL ORDERS
    # -----------------------------------------------------

    if (
        "total orders" in question
        or "number of orders" in question
        or "how many orders" in question
    ):

        return (
            f"📦 There are "
            f"{summary['total_orders']:,} unique orders."
        )


    # -----------------------------------------------------
    # AVERAGE ORDER VALUE
    # -----------------------------------------------------

    if (
        "average order value" in question
        or "average order" in question
    ):

        return (
            f"💵 The average order value is "
            f"₹{summary['average_order_value']:,.2f}."
        )


    # -----------------------------------------------------
    # PROFIT MARGIN
    # -----------------------------------------------------

    if (
        "profit margin" in question
        or "margin" in question
    ):

        return (
            f"📊 The overall profit margin is "
            f"{summary['profit_margin']:.2f}%."
        )


    # -----------------------------------------------------
    # BEST / HIGHEST REVENUE REGION
    # -----------------------------------------------------

    if (
        "highest revenue" in question
        or "most revenue" in question
        or "best region" in question
        or "top region" in question
        or "highest sales region" in question
    ):

        region_analysis = analyze_regions(df)

        if region_analysis:

            return (
                f"🏆 **{region_analysis['best_region']}** "
                f"generated the highest revenue with "
                f"₹{region_analysis['best_revenue']:,.2f}."
            )


    # -----------------------------------------------------
    # LOWEST REVENUE REGION
    # -----------------------------------------------------

    if (
        "lowest revenue" in question
        or "least revenue" in question
        or "worst region" in question
        or "lowest sales region" in question
    ):

        region_analysis = analyze_regions(df)

        if region_analysis:

            return (
                f"⚠️ **{region_analysis['worst_region']}** "
                f"generated the lowest revenue with "
                f"₹{region_analysis['worst_revenue']:,.2f}."
            )


    # -----------------------------------------------------
    # TOP PRODUCT
    # -----------------------------------------------------

    if (
        "top product" in question
        or "best product" in question
        or "highest selling product" in question
        or "most sold product" in question
    ):

        product_analysis = analyze_products(df)

        if product_analysis:

            return (
                f"🏆 **{product_analysis['best_product']}** "
                f"is the top product by revenue, generating "
                f"₹{product_analysis['best_product_sales']:,.2f}."
            )


    # -----------------------------------------------------
    # UNDERPERFORMING PRODUCT
    # -----------------------------------------------------

    if (
        "underperforming product" in question
        or "worst product" in question
        or "lowest selling product" in question
        or "least selling product" in question
    ):

        product_analysis = analyze_products(df)

        if product_analysis:

            return (
                f"⚠️ **{product_analysis['worst_product']}** "
                f"has the lowest revenue at "
                f"₹{product_analysis['worst_product_sales']:,.2f}."
            )


    # -----------------------------------------------------
    # MOST PROFITABLE PRODUCT
    # -----------------------------------------------------

    if (
        "most profitable product" in question
        or "highest profit product" in question
    ):

        product_analysis = analyze_products(df)

        if product_analysis:

            return (
                f"💰 **{product_analysis['most_profitable_product']}** "
                f"is the most profitable product with "
                f"₹{product_analysis['highest_product_profit']:,.2f} "
                f"in profit."
            )


    # -----------------------------------------------------
    # CUSTOMER SEGMENT
    # -----------------------------------------------------

    if (
        "customer segment" in question
        or "best segment" in question
        or "most profitable segment" in question
    ):

        segment_analysis = analyze_segments(df)

        if segment_analysis:

            best_segment = segment_analysis["best_segment"]

            revenue = segment_analysis["table"].loc[
                best_segment,
                "Revenue"
            ]

            return (
                f"👥 **{best_segment}** is the highest-revenue "
                f"customer segment with revenue of "
                f"₹{revenue:,.2f}."
            )


    # -----------------------------------------------------
    # KEY INSIGHTS
    # -----------------------------------------------------

    if (
        "key insights" in question
        or "business insights" in question
        or "important insights" in question
        or "analyze the business" in question
        or "overall analysis" in question
    ):

        insights = generate_business_insights(df)

        if insights:

            response = "🧠 **Key Business Insights**\n\n"

            for i, insight in enumerate(
                insights,
                start=1
            ):

                response += (
                    f"{i}. {insight}\n\n"
                )

            return response


    # -----------------------------------------------------
    # SALES DECREASE
    # -----------------------------------------------------

    if (
        "sales decrease" in question
        or "sales declined" in question
        or "sales dropped" in question
        or "sales falling" in question
        or "why did sales" in question
    ):

        monthly_analysis = analyze_monthly_sales(df)

        if monthly_analysis:

            change = monthly_analysis[
                "change_percentage"
            ]

            if change < 0:

                return (
                    f"📉 Revenue decreased by approximately "
                    f"{abs(change):.2f}% from the first month "
                    f"to the last month. "
                    f"The lowest-revenue month was "
                    f"**{monthly_analysis['lowest_month']}**, "
                    f"with revenue of "
                    f"₹{monthly_analysis['lowest_month_sales']:,.2f}."
                )

            elif change > 0:

                return (
                    f"📈 The dataset does not show an overall "
                    f"sales decrease from the first month "
                    f"to the last month. Instead, revenue "
                    f"increased by approximately "
                    f"{change:.2f}%."
                )

            else:

                return (
                    "📊 Revenue remained approximately "
                    "stable between the first and last month."
                )


    # -----------------------------------------------------
    # UNKNOWN QUESTION
    # -----------------------------------------------------

    return (
        "🤔 I couldn't identify that question yet.\n\n"
        "Try asking one of these:\n\n"
        "• Which region generated the most revenue?\n"
        "• Which product is underperforming?\n"
        "• What is the total revenue?\n"
        "• What is the total profit?\n"
        "• Which product is most profitable?\n"
        "• Which customer segment performs best?\n"
        "• Why did sales decrease?\n"
        "• What are the key business insights?"
    )

