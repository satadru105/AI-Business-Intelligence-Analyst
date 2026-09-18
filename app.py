import streamlit as st
import pandas as pd
import plotly.express as px

from modules.data_loader import load_file

from modules.data_quality import (
    generate_quality_summary,
    clean_dataset
)

from modules.analytics import generate_analytics

from modules.ai_analyst import answer_question

from modules.anomaly_detection import (
    detect_all_anomalies,
    get_anomaly_records,
    generate_anomaly_summary
)

from modules.recommendations import (
    generate_recommendations,
    generate_recommendation_summary
)

from modules.report_generator import generate_management_report

from modules.email_alert import create_alert_email, send_email_alert

from modules.chat_assistant import render_ai_chat_assistant

from modules.schema_detector import detect_schema


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AI Business Intelligence Analyst",
    page_icon="🤖",
    layout="wide",
)


# ==================================================
# THEME
# ==================================================

THEMES = {
    "Light": {
        "page": "linear-gradient(135deg, #f8fbfc 0%, #ffffff 48%, #f2f7f5 100%)",
        "surface": "rgba(255, 255, 255, 0.86)",
        "ink": "#172033",
        "muted": "#667085",
        "accent": "#0f766e",
        "line": "#d9e2ec",
        "shadow": "rgba(23, 32, 51, 0.06)",
    },
    "Dark": {
        "page": "linear-gradient(135deg, #101827 0%, #172333 52%, #102c2a 100%)",
        "surface": "rgba(27, 41, 58, 0.92)",
        "ink": "#eef6f5",
        "muted": "#a9b9c8",
        "accent": "#2dd4bf",
        "line": "#385064",
        "shadow": "rgba(0, 0, 0, 0.28)",
    },
}


def apply_theme(theme_name):
    colors = THEMES[theme_name]
    st.markdown(
        f"""
    <style>

    :root {{
        --ink: {colors['ink']};
        --muted: {colors['muted']};
        --accent: {colors['accent']};
        --line: {colors['line']};
        --surface: {colors['surface']};
        --shadow: {colors['shadow']};
    }}

    .stApp {{
        background: {colors['page']};
        color: var(--ink);
    }}

    [data-testid="stSidebar"] {{
        background: var(--surface);
    }}

    [data-testid="stSidebar"] * {{
        color: var(--ink);
    }}

    .main-title {{
        color: var(--ink);
        font-size: 40px;
        font-weight: 700;
        letter-spacing: 0;
        margin-bottom: 4px;
    }}

    .subtitle {{
        color: var(--muted);
        font-size: 17px;
        margin-bottom: 26px;
    }}

    [data-testid="stMetric"] {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 8px;
        box-shadow: 0 4px 16px var(--shadow);
        padding: 14px 16px;
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid var(--line);
    }}

    .stTextInput input,
    .stTextArea textarea,
    [data-baseweb="select"] > div {{
        background: var(--surface);
        color: var(--ink);
        border-color: var(--line);
    }}

    .stButton > button[kind="primary"] {{
        background: var(--accent);
        border-color: var(--accent);
        color: #ffffff;
    }}

    .stCaption {{
        color: var(--muted);
    }}

    </style>
    """,
        unsafe_allow_html=True,
    )


# ==================================================
# HEADER
# ==================================================

def render_header():

    st.markdown(
        '<div class="main-title">'
        '🤖 AI-Powered Business Intelligence Analyst'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        'Upload your business data and let AI analyze it.'
        '</div>',
        unsafe_allow_html=True,
    )


# ==================================================
# SIDEBAR
# ==================================================

def render_sidebar():

    with st.sidebar:

        st.header("📂 Data Upload")

        theme_name = st.radio(
            "Appearance",
            options=["Light", "Dark"],
            index=0 if st.session_state.get("theme", "Light") == "Light" else 1,
            horizontal=True,
            key="theme",
        )

        apply_theme(theme_name)

        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file",
            type=["csv", "xlsx", "xls"],
        )

        st.markdown("---")

        st.info(
            "Supported formats:\n"
            "• CSV\n"
            "• Excel (.xlsx)\n"
            "• Excel (.xls)"
        )

    return uploaded_file


# ==================================================
# DATASET OVERVIEW
# ==================================================

def render_dataset_overview(df):

    st.subheader("📊 Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Rows",
            f"{df.shape[0]:,}"
        )

    with col2:

        st.metric(
            "Columns",
            f"{df.shape[1]:,}"
        )

    with col3:

        st.metric(
            "Missing Values",
            f"{df.isnull().sum().sum():,}"
        )

    with col4:

        st.metric(
            "Duplicate Rows",
            f"{df.duplicated().sum():,}"
        )

    st.subheader("🔍 Data Preview")

    st.dataframe(
        df.head(100),
        use_container_width=True
    )

    st.subheader("📋 Column Information")

    column_info = pd.DataFrame(
        {
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values,
            "Missing Values": df.isnull().sum().values,
            "Unique Values": [
                df[column].nunique()
                for column in df.columns
            ],
        }
    )

    st.dataframe(
        column_info,
        use_container_width=True
    )


def render_detected_schema(df):
    """Explain how flexible source columns were mapped for analysis."""
    schema = detect_schema(df)
    mapping = schema.get("business_mapping", {})

    st.subheader("🧭 Analysis Readiness")

    if mapping:
        mapping_df = pd.DataFrame(
            [
                {"Analysis Role": role, "Source Column": source}
                for role, source in mapping.items()
            ]
        )
        st.dataframe(mapping_df, use_container_width=True, hide_index=True)
        st.caption(
            "The original columns are preserved. Common business fields are mapped automatically so different CSV naming styles can be analyzed together."
        )
    else:
        st.info("No standard business fields were detected. Use the data-quality and preview sections to inspect this file.")


# ==================================================
# DATA QUALITY ANALYSIS
# ==================================================

def render_data_quality_analysis(df):

    st.markdown("---")

    st.header("🧹 Data Quality Analysis")

    quality = generate_quality_summary(df)

    score = quality["score"]
    status = quality["status"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Data Quality Score",
            f"{score}/100"
        )

    with col2:

        st.metric(
            "Missing Values",
            f"{df.isnull().sum().sum():,}"
        )

    with col3:

        st.metric(
            "Duplicate Rows",
            f"{quality['duplicates']:,}"
        )

    with col4:

        st.metric(
            "Quality Status",
            status
        )

    if score >= 90:

        st.success(
            f"🟢 Data quality is {status}."
        )

    elif score >= 75:

        st.info(
            f"🟡 Data quality is {status}."
        )

    elif score >= 60:

        st.warning(
            f"🟠 Data quality {status}."
        )

    else:

        st.error(
            f"🔴 Data quality is {status}."
        )

    # --------------------------------------------------
    # Missing Values
    # --------------------------------------------------

    st.subheader("🔴 Missing Values")

    if quality["missing"].empty:

        st.success(
            "No missing values detected."
        )

    else:

        st.dataframe(
            quality["missing"],
            use_container_width=True
        )

    # --------------------------------------------------
    # Duplicate Rows
    # --------------------------------------------------

    st.subheader("🔁 Duplicate Rows")

    if quality["duplicates"] == 0:

        st.success(
            "No duplicate rows detected."
        )

    else:

        st.warning(
            f"{quality['duplicates']} duplicate rows detected."
        )

    # --------------------------------------------------
    # Duplicate IDs
    # --------------------------------------------------

    st.subheader("🆔 Duplicate IDs")

    if quality["duplicate_ids"].empty:

        st.info(
            "No ID columns were detected."
        )

    else:

        st.dataframe(
            quality["duplicate_ids"],
            use_container_width=True
        )

    # --------------------------------------------------
    # Text Consistency
    # --------------------------------------------------

    st.subheader("🔤 Text Consistency")

    if quality["inconsistencies"].empty:

        st.success(
            "No obvious text inconsistencies detected."
        )

    else:

        st.warning(
            "Potential inconsistent text values detected."
        )

        st.dataframe(
            quality["inconsistencies"],
            use_container_width=True
        )

    # --------------------------------------------------
    # Outliers
    # --------------------------------------------------

    st.subheader("📈 Numeric Outliers")

    if quality["outliers"].empty:

        st.success(
            "No significant numeric outliers detected."
        )

    else:

        st.warning(
            "Potential numeric outliers detected."
        )

        st.dataframe(
            quality["outliers"],
            use_container_width=True
        )

    # --------------------------------------------------
    # Date Validation
    # --------------------------------------------------

    st.subheader("📅 Date Validation")

    if quality["invalid_dates"].empty:

        st.info(
            "No date columns detected."
        )

    else:

        st.dataframe(
            quality["invalid_dates"],
            use_container_width=True
        )


# ==================================================
# DATA CLEANING
# ==================================================

def render_cleaning_section(df):

    st.markdown("---")

    st.subheader("🧹 Automatic Data Cleaning")

    st.write(
        "The cleaning engine can safely remove duplicate rows, "
        "remove unnecessary spaces, and standardize common "
        "categorical values."
    )

    if st.button(
        "✨ Clean Dataset",
        type="primary"
    ):

        cleaned_df = clean_dataset(df)

        st.session_state["cleaned_df"] = cleaned_df

        st.success(
            "Dataset cleaned successfully!"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Original Rows",
                len(df)
            )

        with col2:

            st.metric(
                "Cleaned Rows",
                len(cleaned_df)
            )

        st.subheader(
            "📊 Cleaned Dataset Preview"
        )

        st.dataframe(
            cleaned_df.head(100),
            use_container_width=True
        )

        csv_data = cleaned_df.to_csv(
            index=False
        )

        st.download_button(
            label="⬇️ Download Cleaned CSV",
            data=csv_data,
            file_name="cleaned_sales_data.csv",
            mime="text/csv",
        )


# ==================================================
# PART 4
# INTERACTIVE BUSINESS DASHBOARD
# ==================================================

def render_interactive_dashboard(df):

    st.markdown("---")

    st.header("🎛️ Interactive Business Dashboard")

    st.write(
        "Use the filters below to dynamically analyze "
        "different parts of your business data."
    )

    filtered_df = df.copy()

    # ==================================================
    # FILTER ROW 1
    # ==================================================

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    # --------------------------------------------------
    # REGION
    # --------------------------------------------------

    with filter_col1:

        if "Region" in filtered_df.columns:

            regions = sorted(
                filtered_df["Region"]
                .dropna()
                .astype(str)
                .unique()
            )

            selected_regions = st.multiselect(
                "🌎 Select Region",
                regions,
                default=regions,
                key="region_filter"
            )

            filtered_df = filtered_df[
                filtered_df["Region"]
                .astype(str)
                .isin(selected_regions)
            ]

    # --------------------------------------------------
    # CATEGORY
    # --------------------------------------------------

    with filter_col2:

        if "Category" in filtered_df.columns:

            categories = sorted(
                filtered_df["Category"]
                .dropna()
                .astype(str)
                .unique()
            )

            selected_categories = st.multiselect(
                "🛍️ Select Category",
                categories,
                default=categories,
                key="category_filter"
            )

            filtered_df = filtered_df[
                filtered_df["Category"]
                .astype(str)
                .isin(selected_categories)
            ]

    # --------------------------------------------------
    # CUSTOMER SEGMENT
    # --------------------------------------------------

    with filter_col3:

        if "Customer_Segment" in filtered_df.columns:

            segments = sorted(
                filtered_df["Customer_Segment"]
                .dropna()
                .astype(str)
                .unique()
            )

            selected_segments = st.multiselect(
                "👥 Customer Segment",
                segments,
                default=segments,
                key="segment_filter"
            )

            filtered_df = filtered_df[
                filtered_df["Customer_Segment"]
                .astype(str)
                .isin(selected_segments)
            ]

    # ==================================================
    # FILTER ROW 2
    # ==================================================

    filter_col4, filter_col5 = st.columns(2)

    # --------------------------------------------------
    # SALES CHANNEL
    # --------------------------------------------------

    with filter_col4:

        if "Sales_Channel" in filtered_df.columns:

            channels = sorted(
                filtered_df["Sales_Channel"]
                .dropna()
                .astype(str)
                .unique()
            )

            selected_channels = st.multiselect(
                "🛒 Sales Channel",
                channels,
                default=channels,
                key="channel_filter"
            )

            filtered_df = filtered_df[
                filtered_df["Sales_Channel"]
                .astype(str)
                .isin(selected_channels)
            ]

    # --------------------------------------------------
    # DATE
    # --------------------------------------------------

    with filter_col5:

        if "Order_Date" in filtered_df.columns:

            filtered_df["Order_Date"] = pd.to_datetime(
                filtered_df["Order_Date"],
                errors="coerce"
            )

            min_date = filtered_df["Order_Date"].min()
            max_date = filtered_df["Order_Date"].max()

            if pd.notna(min_date) and pd.notna(max_date):

                selected_dates = st.date_input(
                    "📅 Select Date Range",
                    value=(
                        min_date.date(),
                        max_date.date()
                    ),
                    key="date_filter"
                )

                if (
                    isinstance(selected_dates, tuple)
                    and len(selected_dates) == 2
                ):

                    start_date, end_date = selected_dates

                    filtered_df = filtered_df[
                        (
                            filtered_df["Order_Date"]
                            .dt.date >= start_date
                        )
                        &
                        (
                            filtered_df["Order_Date"]
                            .dt.date <= end_date
                        )
                    ]

    # ==================================================
    # FILTER RESULT
    # ==================================================

    st.success(
        f"Showing **{len(filtered_df):,} records** "
        f"after applying filters."
    )

    # ==================================================
    # ANALYTICS
    # ==================================================

    analytics = generate_analytics(
        filtered_df
    )

    kpis = analytics["kpis"]

    # ==================================================
    # KPI SECTION
    # ==================================================

    st.markdown("---")

    st.subheader("💰 Business KPIs")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "💰 Total Revenue",
            f"₹{kpis['Total Revenue']:,.2f}"
        )

    with col2:

        st.metric(
            "📈 Total Profit",
            f"₹{kpis['Total Profit']:,.2f}"
        )

    with col3:

        st.metric(
            "📦 Total Orders",
            f"{kpis['Total Orders']:,}"
        )

    col4, col5, col6 = st.columns(3)

    with col4:

        st.metric(
            "🛒 Quantity Sold",
            f"{kpis['Total Quantity']:,}"
        )

    with col5:

        st.metric(
            "💵 Average Order Value",
            f"₹{kpis['Average Order Value']:,.2f}"
        )

    with col6:

        st.metric(
            "📊 Profit Margin",
            f"{kpis['Profit Margin']:.2f}%"
        )

    # ==================================================
    # CHARTS
    # ==================================================

    st.markdown("---")

    st.subheader("📊 Business Performance")

    # --------------------------------------------------
    # REGION
    # --------------------------------------------------

    region_data = analytics["region"]

    if not region_data.empty:

        fig_region = px.bar(
            region_data,
            x="Region",
            y="Sales",
            title="🌎 Revenue by Region",
            text_auto=".2s"
        )

        fig_region.update_layout(
            xaxis_title="Region",
            yaxis_title="Revenue",
            template="plotly_white"
        )

        st.plotly_chart(
            fig_region,
            use_container_width=True
        )

    # --------------------------------------------------
    # CATEGORY
    # --------------------------------------------------

    category_data = analytics["category"]

    if not category_data.empty:

        fig_category = px.bar(
            category_data,
            x="Category",
            y="Sales",
            title="🛍️ Revenue by Product Category",
            text_auto=".2s"
        )

        fig_category.update_layout(
            xaxis_title="Category",
            yaxis_title="Revenue",
            template="plotly_white"
        )

        st.plotly_chart(
            fig_category,
            use_container_width=True
        )

    # --------------------------------------------------
    # MONTHLY
    # --------------------------------------------------

    monthly_data = analytics["monthly"]

    if not monthly_data.empty:

        fig_monthly = px.line(
            monthly_data,
            x="Month",
            y="Sales",
            markers=True,
            title="📅 Monthly Revenue Trend"
        )

        fig_monthly.update_layout(
            xaxis_title="Month",
            yaxis_title="Revenue",
            template="plotly_white"
        )

        st.plotly_chart(
            fig_monthly,
            use_container_width=True
        )

    # --------------------------------------------------
    # TOP PRODUCTS
    # --------------------------------------------------

    top_product_data = analytics["top_products"]

    if not top_product_data.empty:

        fig_products = px.bar(
            top_product_data,
            x="Sales",
            y="Product",
            orientation="h",
            title="🏆 Top 10 Products by Revenue",
            text_auto=".2s"
        )

        fig_products.update_layout(
            yaxis={
                "categoryorder": "total ascending"
            },
            xaxis_title="Revenue",
            yaxis_title="Product",
            template="plotly_white"
        )

        st.plotly_chart(
            fig_products,
            use_container_width=True
        )

    # --------------------------------------------------
    # PROFIT
    # --------------------------------------------------

    profit_product_data = analytics["product_profit"]

    if not profit_product_data.empty:

        fig_profit = px.bar(
            profit_product_data,
            x="Profit",
            y="Product",
            orientation="h",
            title="💹 Profit by Product",
            text_auto=".2s"
        )

        fig_profit.update_layout(
            yaxis={
                "categoryorder": "total ascending"
            },
            xaxis_title="Profit",
            yaxis_title="Product",
            template="plotly_white"
        )

        st.plotly_chart(
            fig_profit,
            use_container_width=True
        )

    # --------------------------------------------------
    # CUSTOMER SEGMENT
    # --------------------------------------------------

    segment_data = analytics["segments"]

    if not segment_data.empty:

        fig_segment = px.bar(
            segment_data,
            x="Customer_Segment",
            y="Revenue",
            title="👥 Revenue by Customer Segment",
            text_auto=".2s"
        )

        fig_segment.update_layout(
            xaxis_title="Customer Segment",
            yaxis_title="Revenue",
            template="plotly_white"
        )

        st.plotly_chart(
            fig_segment,
            use_container_width=True
        )

    # ==================================================
    # BUSINESS SUMMARY
    # ==================================================

    st.markdown("---")

    st.subheader("🧠 Automated Business Summary")

    best_region = analytics["regions"]["best_region"]
    worst_region = analytics["regions"]["worst_region"]

    summary_col1, summary_col2 = st.columns(2)

    with summary_col1:

        if best_region:

            st.success(
                f"🏆 **Best Performing Region:** "
                f"{best_region}"
            )

        else:

            st.info(
                "No region data available."
            )

    with summary_col2:

        if worst_region:

            st.warning(
                f"⚠️ **Lowest Performing Region:** "
                f"{worst_region}"
            )

        else:

            st.info(
                "No region data available."
            )

    st.info(
        f"""
        **Business Overview**

        The filtered dataset contains
        **{kpis['Total Orders']:,} orders**.

        Total revenue is
        **₹{kpis['Total Revenue']:,.2f}**.

        Total profit is
        **₹{kpis['Total Profit']:,.2f}**.

        Profit margin is
        **{kpis['Profit Margin']:.2f}%**.

        Average order value is
        **₹{kpis['Average Order Value']:,.2f}**.
        """
    )


# ==================================================
# PART 5
# AI BUSINESS ANALYST
# ==================================================

def render_ai_analyst(df):

    st.markdown("---")

    st.header("🤖 AI Business Analyst")

    st.write(
        "Ask questions about your business data "
        "and receive data-backed answers automatically."
    )

    # ==================================================
    # EXAMPLE QUESTIONS
    # ==================================================

    st.subheader("💡 Example Questions")

    example_col1, example_col2 = st.columns(2)

    with example_col1:

        st.markdown(
            """
            **📊 Business Performance**

            • Which region generated the most revenue?

            • What is the total revenue?

            • What is the total profit?

            • What is the profit margin?
            """
        )

    with example_col2:

        st.markdown(
            """
            **📦 Product & Customer Analysis**

            • Which product is underperforming?

            • Which product is most profitable?

            • Which customer segment performs best?

            • Why did sales decrease?
            """
        )

    # ==================================================
    # QUESTION INPUT
    # ==================================================

    st.subheader("💬 Ask Your Business Question")

    question = st.text_input(
        "Enter your question:",
        placeholder=(
            "Example: Which region generated "
            "the most revenue?"
        ),
        key="ai_question"
    )

    # ==================================================
    # ASK BUTTON
    # ==================================================

    if st.button(
        "🤖 Ask AI Analyst",
        type="primary",
        key="ask_ai_button"
    ):

        if not question.strip():

            st.warning(
                "⚠️ Please enter a question first."
            )

        else:

            with st.spinner(
                "🤖 Analyzing your business data..."
            ):

                answer = answer_question(
                    df,
                    question
                )

            st.markdown("---")

            st.subheader(
                "🧠 AI Analyst Answer"
            )

            st.success(answer)

    # ==================================================
    # SUPPORTED QUESTIONS
    # ==================================================

    with st.expander(
        "📚 What can I ask?"
    ):

        st.markdown(
            """
            ### 💰 Revenue & Profit

            - What is the total revenue?
            - What is the total profit?
            - What is the profit margin?
            - What is the average order value?

            ### 🌎 Regional Analysis

            - Which region generated the most revenue?
            - Which region generated the least revenue?
            - What is the best region?
            - What is the worst region?

            ### 📦 Product Analysis

            - Which product is the best?
            - Which product is underperforming?
            - Which product is most profitable?
            - Which product has the highest profit?

            ### 👥 Customer Analysis

            - Which customer segment performs best?
            - Which customer segment generates the most revenue?

            ### 📈 Trend Analysis

            - Why did sales decrease?
            - What are the key business insights?
            - Give me an overall analysis.
            """
        )


# ==================================================
# PART 6
# ANOMALY DETECTION
# ==================================================

def render_anomaly_detection(df):

    st.markdown("---")

    st.header("🚨 AI-Powered Anomaly Detection")

    st.write(
        "Automatically identify unusual changes in sales, "
        "profit, regional performance, and product performance."
    )

    # ==================================================
    # RUN ANOMALY DETECTION
    # ==================================================

    with st.spinner(
        "🔎 Scanning business data for anomalies..."
    ):

        anomalies = detect_all_anomalies(df)

        anomaly_records = get_anomaly_records(df)

        summary = generate_anomaly_summary(df)

    # ==================================================
    # ANOMALY SUMMARY
    # ==================================================

    st.subheader("📊 Anomaly Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "🚨 Total Anomalies",
            f"{summary['total']:,}"
        )

    with col2:

        st.metric(
            "🔴 High Severity",
            f"{summary['high']:,}"
        )

    with col3:

        st.metric(
            "🟠 Medium Severity",
            f"{summary['medium']:,}"
        )

    with col4:

        st.metric(
            "🟡 Low Severity",
            f"{summary['low']:,}"
        )

    # ==================================================
    # OVERALL STATUS
    # ==================================================

    if summary["total"] == 0:

        st.success(
            "✅ No significant business anomalies were detected."
        )

    elif summary["high"] > 0:

        st.error(
            f"🔴 Attention required: "
            f"{summary['high']} high-severity anomaly/anomalies detected."
        )

    elif summary["medium"] > 0:

        st.warning(
            f"🟠 {summary['medium']} medium-severity "
            "anomaly/anomalies detected."
        )

    else:

        st.info(
            f"🟡 {summary['low']} low-severity "
            "anomaly/anomalies detected."
        )

    # ==================================================
    # DETECTED ANOMALIES TABLE
    # ==================================================

    st.subheader("⚠️ Detected Anomalies")

    if not anomaly_records.empty:

        display_df = anomaly_records.copy()

        display_df["Value"] = display_df["Value"].apply(
            lambda x: f"₹{x:,.2f}"
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "🎉 No unusual records were identified."
        )

    # ==================================================
    # MONTHLY SALES ANOMALIES
    # ==================================================

    st.subheader("📉 Monthly Sales Anomaly Analysis")

    sales_data = anomalies["sales"]

    if not sales_data.empty:

        fig_sales = px.line(
            sales_data,
            x="Month",
            y="Sales",
            markers=True,
            title="Monthly Sales Monitoring"
        )

        fig_sales.update_layout(
            xaxis_title="Month",
            yaxis_title="Sales",
            template="plotly_white"
        )

        st.plotly_chart(
            fig_sales,
            use_container_width=True
        )

        abnormal_sales = sales_data[
            sales_data["Anomaly"] == True
        ]

        if not abnormal_sales.empty:

            st.warning(
                f"⚠️ {len(abnormal_sales)} unusual "
                "monthly sales period(s) detected."
            )

        else:

            st.success(
                "✅ Monthly sales are within the expected range."
            )

    else:

        st.info(
            "Not enough date-based data to perform "
            "monthly sales anomaly detection."
        )

    # ==================================================
    # MONTHLY PROFIT ANOMALIES
    # ==================================================

    st.subheader("💰 Monthly Profit Anomaly Analysis")

    profit_data = anomalies["profit"]

    if not profit_data.empty:

        fig_profit = px.line(
            profit_data,
            x="Month",
            y="Profit",
            markers=True,
            title="Monthly Profit Monitoring"
        )

        fig_profit.update_layout(
            xaxis_title="Month",
            yaxis_title="Profit",
            template="plotly_white"
        )

        st.plotly_chart(
            fig_profit,
            use_container_width=True
        )

        abnormal_profit = profit_data[
            profit_data["Anomaly"] == True
        ]

        if not abnormal_profit.empty:

            st.warning(
                f"⚠️ {len(abnormal_profit)} unusual "
                "monthly profit period(s) detected."
            )

        else:

            st.success(
                "✅ Monthly profit is within the expected range."
            )

    else:

        st.info(
            "Not enough data to perform monthly profit "
            "anomaly detection."
        )

    # ==================================================
    # REGIONAL ANOMALIES
    # ==================================================

    st.subheader("🌎 Regional Performance Anomalies")

    region_data = anomalies["region"]

    if not region_data.empty:

        st.dataframe(
            region_data,
            use_container_width=True,
            hide_index=True
        )

        abnormal_regions = region_data[
            region_data["Anomaly"] == True
        ]

        if not abnormal_regions.empty:

            st.warning(
                f"⚠️ {len(abnormal_regions)} region(s) "
                "show unusual revenue performance."
            )

        else:

            st.success(
                "✅ Regional revenue is within the expected range."
            )

    else:

        st.info(
            "Not enough regional data to detect anomalies."
        )

    # ==================================================
    # PRODUCT ANOMALIES
    # ==================================================

    st.subheader("📦 Product Performance Anomalies")

    product_data = anomalies["product"]

    if not product_data.empty:

        st.dataframe(
            product_data,
            use_container_width=True,
            hide_index=True
        )

        abnormal_products = product_data[
            product_data["Anomaly"] == True
        ]

        if not abnormal_products.empty:

            st.warning(
                f"⚠️ {len(abnormal_products)} product(s) "
                "show unusual sales performance."
            )

        else:

            st.success(
                "✅ Product performance is within the expected range."
            )

    else:

        st.info(
            "Not enough product data to detect anomalies."
        )

    # ==================================================
    # BUSINESS INTERPRETATION
    # ==================================================

    st.subheader("🧠 Business Interpretation")

    if anomaly_records.empty:

        st.success(
            """
            The anomaly engine did not identify significant
            statistical abnormalities in the current dataset.

            The system continuously evaluates sales, profit,
            regional performance, and product performance.
            """
        )

    else:

        for _, row in anomaly_records.iterrows():

            severity = row["Severity"]

            if severity == "High":

                icon = "🔴"

            elif severity == "Medium":

                icon = "🟠"

            else:

                icon = "🟡"

            st.markdown(
                f"""
                {icon} **{row['Type']} — {row['Metric']}**

                - Detected issue: **{row['Anomaly']}**
                - Value: **₹{row['Value']:,.2f}**
                - Severity: **{severity}**
                """
            )

    # ==================================================
    # ANOMALY METHODOLOGY
    # ==================================================

    with st.expander(
        "🔬 How does anomaly detection work?"
    ):

        st.markdown(
            """
            ### Statistical Detection Method

            This module uses the **Interquartile Range (IQR)**
            method to identify unusual business values.

            **IQR = Q3 − Q1**

            Values outside the statistical range are flagged
            as potential anomalies.

            The system evaluates:

            - 📉 Monthly sales
            - 💰 Monthly profit
            - 🌎 Regional revenue
            - 📦 Product revenue

            ### Severity

            **🔴 High**

            Strong deviation from the expected range.

            **🟠 Medium**

            Moderate deviation from the expected range.

            **🟡 Low**

            Smaller deviation that should be monitored.

            **Normal**

            Value falls within the expected statistical range.
            """
        )


# ==================================================
# PART 7
# AI BUSINESS RECOMMENDATIONS
# ==================================================

def render_business_recommendations(df):

    st.markdown("---")

    st.header("🧠 AI Business Recommendations")

    st.write(
        "Automatically generate data-driven business recommendations "
        "from sales, products, profitability, customer segments, "
        "data quality, and detected anomalies."
    )

    # ==================================================
    # GENERATE RECOMMENDATIONS
    # ==================================================

    with st.spinner(
        "🧠 Generating business recommendations..."
    ):

        recommendations = generate_recommendations(df)

        recommendation_summary = generate_recommendation_summary(df)

    # ==================================================
    # RECOMMENDATION SUMMARY
    # ==================================================

    st.subheader("🎯 Recommendation Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "💡 Total Recommendations",
            f"{recommendation_summary['total']:,}"
        )

    with col2:

        st.metric(
            "🔴 High Priority",
            f"{recommendation_summary['high']:,}"
        )

    with col3:

        st.metric(
            "🟠 Medium Priority",
            f"{recommendation_summary['medium']:,}"
        )

    with col4:

        st.metric(
            "🟢 Low Priority",
            f"{recommendation_summary['low']:,}"
        )

    # ==================================================
    # OVERALL STATUS
    # ==================================================

    if recommendation_summary["high"] > 0:

        st.error(
            f"🔴 **Immediate attention required:** "
            f"{recommendation_summary['high']} high-priority "
            "recommendation(s) were generated."
        )

    elif recommendation_summary["medium"] > 0:

        st.warning(
            f"🟠 **Strategic opportunities identified:** "
            f"{recommendation_summary['medium']} medium-priority "
            "recommendation(s) were generated."
        )

    else:

        st.success(
            "🟢 No major business actions were identified."
        )

    # ==================================================
    # NO RECOMMENDATIONS
    # ==================================================

    if recommendations.empty:

        st.info(
            "No recommendations could be generated from "
            "the current dataset."
        )

        return

    # ==================================================
    # ALL RECOMMENDATIONS
    # ==================================================

    st.subheader("📋 AI-Generated Recommendations")

    st.dataframe(
        recommendations[
            [
                "Category",
                "Recommendation",
                "Priority",
                "Why",
                "Recommended Action"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # ==================================================
    # PRIORITY FILTER
    # ==================================================

    st.subheader("🎯 Filter by Priority")

    selected_priority = st.multiselect(
        "Select recommendation priority:",
        options=["High", "Medium", "Low"],
        default=["High", "Medium", "Low"],
        key="recommendation_priority_filter"
    )

    filtered_recommendations = recommendations[
        recommendations["Priority"].isin(selected_priority)
    ]

    if filtered_recommendations.empty:

        st.info(
            "No recommendations match the selected priority."
        )

    else:

        st.dataframe(
            filtered_recommendations[
                [
                    "Category",
                    "Recommendation",
                    "Priority",
                    "Why",
                    "Recommended Action"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    # ==================================================
    # RECOMMENDATION CATEGORY ANALYSIS
    # ==================================================

    st.subheader("📊 Recommendations by Business Area")

    category_counts = (
        recommendations["Category"]
        .value_counts()
        .reset_index()
    )

    category_counts.columns = [
        "Category",
        "Recommendations"
    ]

    if not category_counts.empty:

        fig_category = px.bar(
            category_counts,
            x="Category",
            y="Recommendations",
            title="Recommendation Distribution by Business Area",
            text="Recommendations"
        )

        fig_category.update_layout(
            xaxis_title="Business Area",
            yaxis_title="Number of Recommendations",
            template="plotly_white"
        )

        st.plotly_chart(
            fig_category,
            use_container_width=True
        )

    # ==================================================
    # PRIORITY DISTRIBUTION
    # ==================================================

    st.subheader("🚦 Recommendation Priority Distribution")

    priority_counts = (
        recommendations["Priority"]
        .value_counts()
        .reindex(
            ["High", "Medium", "Low"],
            fill_value=0
        )
        .reset_index()
    )

    priority_counts.columns = [
        "Priority",
        "Recommendations"
    ]

    fig_priority = px.bar(
        priority_counts,
        x="Priority",
        y="Recommendations",
        title="Business Recommendation Priority",
        text="Recommendations"
    )

    fig_priority.update_layout(
        xaxis_title="Priority",
        yaxis_title="Number of Recommendations",
        template="plotly_white"
    )

    st.plotly_chart(
        fig_priority,
        use_container_width=True
    )

    # ==================================================
    # EXECUTIVE ACTION PLAN
    # ==================================================

    st.subheader("🚀 Executive Action Plan")

    high_priority = recommendations[
        recommendations["Priority"] == "High"
    ]

    if not high_priority.empty:

        st.error("### 🔴 Immediate Actions")

        for _, row in high_priority.iterrows():

            st.markdown(
                f"""
**{row['Recommendation']}**

**Why:** {row['Why']}

**Recommended Action:** {row['Recommended Action']}
"""
            )

    medium_priority = recommendations[
        recommendations["Priority"] == "Medium"
    ]

    if not medium_priority.empty:

        st.warning("### 🟠 Strategic Improvements")

        for _, row in medium_priority.iterrows():

            st.markdown(
                f"""
**{row['Recommendation']}**

**Why:** {row['Why']}

**Recommended Action:** {row['Recommended Action']}
"""
            )

    low_priority = recommendations[
        recommendations["Priority"] == "Low"
    ]

    if not low_priority.empty:

        st.info("### 🟢 Optimization Opportunities")

        for _, row in low_priority.iterrows():

            st.markdown(
                f"""
**{row['Recommendation']}**

**Why:** {row['Why']}

**Recommended Action:** {row['Recommended Action']}
"""
            )

    # ==================================================
    # CATEGORY-SPECIFIC INSIGHTS
    # ==================================================

    st.subheader("🧠 Business Intelligence Breakdown")

    categories = [
        ("Sales Growth", "📈"),
        ("Product", "📦"),
        ("Profit", "💰"),
        ("Customer Segment", "👥"),
        ("Anomaly Action", "🚨"),
        ("Data Quality", "🧹")
    ]

    for category_name, icon in categories:

        category_rows = recommendations[
            recommendations["Category"] == category_name
        ]

        if not category_rows.empty:

            with st.expander(
                f"{icon} {category_name} Recommendations"
            ):

                for _, row in category_rows.iterrows():

                    st.markdown(
                        f"""
### {row['Recommendation']}

**Priority:** {row['Priority']}

**Why this recommendation was generated:**  
{row['Why']}

**Recommended Action:**  
{row['Recommended Action']}
"""
                    )

    # ==================================================
    # METHODOLOGY
    # ==================================================

    with st.expander(
        "🔬 How are these recommendations generated?"
    ):

        st.markdown(
            """
### Data-Driven Recommendation Engine

The recommendation engine analyzes the uploaded dataset and
automatically identifies business opportunities and risks.

**📈 Sales Growth**
- Regional revenue performance
- Category contribution
- Revenue concentration
- Weak-performing business areas

**📦 Product Performance**
- Top-selling products
- Underperforming products
- Product revenue opportunities

**💰 Profitability**
- Most profitable products
- Lowest-profit products
- Pricing and cost improvement opportunities

**👥 Customer Segments**
- Highest-revenue customer segment
- Lowest-revenue customer segment
- Customer engagement opportunities

**🚨 Anomaly Actions**
- Sales spikes
- Sales drops
- Profit spikes
- Profit drops
- High/low regional performance
- High/low product performance

**🧹 Data Quality**
- Missing-value issues
- Data reliability concerns

### Priority Logic

**🔴 High**  
Requires immediate business attention.

**🟠 Medium**  
Represents a strategic improvement opportunity.

**🟢 Low**  
Represents an optional optimization opportunity.

Every recommendation contains an explanation of **why it was
generated** and a suggested **business action**.
"""
        )

        # ==================================================
# PART 8
# AI EXECUTIVE MANAGEMENT REPORT
# ==================================================

def render_management_report(df):

    st.markdown("---")

    st.header("📋 AI Executive Management Report")

    st.write(
        "Generate a management-ready business report containing "
        "key performance indicators, business insights, anomalies, "
        "recommendations, and suggested management actions."
    )

    # ==================================================
    # GENERATE REPORT
    # ==================================================

    if st.button(
        "📄 Generate Executive Report",
        type="primary",
        key="generate_management_report_button"
    ):

        with st.spinner(
            "🤖 AI is preparing the executive management report..."
        ):

            try:

                # --------------------------------------------------
                # Generate report using report generator module
                # --------------------------------------------------

                analytics = generate_analytics(df)
                anomaly_summary = generate_anomaly_summary(df)
                anomaly_records = get_anomaly_records(df)
                recommendations = generate_recommendations(df)

                report = generate_management_report(
                    df,
                    analytics,
                    anomaly_summary,
                    anomaly_records,
                    recommendations
                )

                # Store report in session
                st.session_state["management_report"] = report

                st.success(
                    "✅ Executive management report generated successfully!"
                )

            except Exception as e:

                st.error(
                    f"❌ Unable to generate management report: {str(e)}"
                )

    # ==================================================
    # DISPLAY REPORT
    # ==================================================

    if "management_report" not in st.session_state:

        st.info(
            "👆 Click **Generate Executive Report** to create "
            "a complete management report."
        )

        return

    report = st.session_state["management_report"]

    # ==================================================
    # REPORT PREVIEW
    # ==================================================

    st.subheader("📑 Executive Report")

    # --------------------------------------------------
    # If report is a PDF
    # --------------------------------------------------

    if isinstance(report, (bytes, bytearray)):

        st.success(
            "✅ Your executive report is ready as a PDF."
        )

        st.download_button(
            label="⬇️ Download Executive Report PDF",
            data=report,
            file_name="AI_Executive_Management_Report.pdf",
            mime="application/pdf",
            key="download_management_report_pdf"
        )

        return

    # --------------------------------------------------
    # If report is a string
    # --------------------------------------------------

    if isinstance(report, str):

        st.markdown(report)

        # Download Markdown report
        st.download_button(
            label="⬇️ Download Management Report",
            data=report,
            file_name="AI_Executive_Management_Report.md",
            mime="text/markdown",
            key="download_management_report"
        )

        # Download TXT version
        st.download_button(
            label="⬇️ Download Report as TXT",
            data=report,
            file_name="AI_Executive_Management_Report.txt",
            mime="text/plain",
            key="download_management_report_txt"
        )

    # --------------------------------------------------
    # If report is a dictionary
    # --------------------------------------------------

    elif isinstance(report, dict):

        for section_name, section_content in report.items():

            st.subheader(
                f"📌 {str(section_name).replace('_', ' ').title()}"
            )

            if isinstance(section_content, list):

                for item in section_content:

                    st.markdown(
                        f"- {item}"
                    )

            else:

                st.markdown(
                    str(section_content)
                )

        # Convert dictionary to downloadable text
        report_text = ""

        for section_name, section_content in report.items():

            report_text += (
                f"\n{'=' * 60}\n"
                f"{str(section_name).upper()}\n"
                f"{'=' * 60}\n"
            )

            if isinstance(section_content, list):

                for item in section_content:

                    report_text += f"- {item}\n"

            else:

                report_text += f"{section_content}\n"

        st.download_button(
            label="⬇️ Download Management Report",
            data=report_text,
            file_name="AI_Executive_Management_Report.txt",
            mime="text/plain",
            key="download_management_report_dict"
        )

    # --------------------------------------------------
    # Other report formats
    # --------------------------------------------------

    else:

        report_text = str(report)

        st.markdown(report_text)

        st.download_button(
            label="⬇️ Download Management Report",
            data=report_text,
            file_name="AI_Executive_Management_Report.txt",
            mime="text/plain",
            key="download_management_report_other"
        )

    # ==================================================
    # MANAGEMENT DASHBOARD
    # ==================================================

    st.markdown("---")

    st.subheader("📊 Management Performance Snapshot")

    try:

        analytics = generate_analytics(df)

        kpis = analytics["kpis"]

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "💰 Total Revenue",
                f"₹{kpis['Total Revenue']:,.2f}"
            )

        with col2:

            st.metric(
                "📈 Total Profit",
                f"₹{kpis['Total Profit']:,.2f}"
            )

        with col3:

            st.metric(
                "📦 Total Orders",
                f"{kpis['Total Orders']:,}"
            )

        with col4:

            st.metric(
                "📊 Profit Margin",
                f"{kpis['Profit Margin']:.2f}%"
            )

        col5, col6, col7 = st.columns(3)

        with col5:

            st.metric(
                "🛒 Quantity Sold",
                f"{kpis['Total Quantity']:,}"
            )

        with col6:

            st.metric(
                "💵 Average Order Value",
                f"₹{kpis['Average Order Value']:,.2f}"
            )

        with col7:

            best_region = analytics["regions"].get(
                "best_region",
                "N/A"
            )

            st.metric(
                "🏆 Best Region",
                str(best_region)
            )

    except Exception as e:

        st.warning(
            f"Could not generate KPI snapshot: {str(e)}"
        )

    # ==================================================
    # ANOMALY MANAGEMENT SUMMARY
    # ==================================================

    st.markdown("---")

    st.subheader("🚨 Risk & Anomaly Summary")

    try:

        anomaly_summary = generate_anomaly_summary(df)

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Anomalies",
                f"{anomaly_summary['total']:,}"
            )

        with col2:

            st.metric(
                "🔴 High Risk",
                f"{anomaly_summary['high']:,}"
            )

        with col3:

            st.metric(
                "🟠 Medium Risk",
                f"{anomaly_summary['medium']:,}"
            )

        with col4:

            st.metric(
                "🟡 Low Risk",
                f"{anomaly_summary['low']:,}"
            )

        if anomaly_summary["high"] > 0:

            st.error(
                "🔴 Management attention is required because "
                f"{anomaly_summary['high']} high-severity anomalies "
                "were detected."
            )

        elif anomaly_summary["medium"] > 0:

            st.warning(
                "🟠 Several medium-severity anomalies require "
                "management monitoring."
            )

        else:

            st.success(
                "🟢 No high-risk anomalies require immediate attention."
            )

    except Exception as e:

        st.warning(
            f"Could not generate anomaly summary: {str(e)}"
        )

    # ==================================================
    # RECOMMENDATION SUMMARY
    # ==================================================

    st.markdown("---")

    st.subheader("🧠 AI Recommendation Summary")

    try:

        recommendations = generate_recommendations(df)

        recommendation_summary = generate_recommendation_summary(df)

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Recommendations",
                f"{recommendation_summary['total']:,}"
            )

        with col2:

            st.metric(
                "🔴 High Priority",
                f"{recommendation_summary['high']:,}"
            )

        with col3:

            st.metric(
                "🟠 Medium Priority",
                f"{recommendation_summary['medium']:,}"
            )

        with col4:

            st.metric(
                "🟢 Low Priority",
                f"{recommendation_summary['low']:,}"
            )

        if not recommendations.empty:

            st.dataframe(
                recommendations[
                    [
                        "Category",
                        "Recommendation",
                        "Priority",
                        "Why",
                        "Recommended Action"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No business recommendations were generated."
            )

    except Exception as e:

        st.warning(
            f"Could not generate recommendation summary: {str(e)}"
        )

    # ==================================================
    # MANAGEMENT ACTION PLAN
    # ==================================================

    st.markdown("---")

    st.subheader("🎯 Recommended Management Action Plan")

    try:

        recommendations = generate_recommendations(df)

        if recommendations.empty:

            st.info(
                "No immediate management actions were identified."
            )

        else:

            high_actions = recommendations[
                recommendations["Priority"] == "High"
            ]

            medium_actions = recommendations[
                recommendations["Priority"] == "Medium"
            ]

            low_actions = recommendations[
                recommendations["Priority"] == "Low"
            ]

            # --------------------------------------------------
            # HIGH PRIORITY
            # --------------------------------------------------

            if not high_actions.empty:

                st.error(
                    "### 🔴 Immediate Management Actions"
                )

                for index, row in high_actions.iterrows():

                    st.markdown(
                        f"""
**{row['Recommendation']}**

**Business Reason:**  
{row['Why']}

**Recommended Action:**  
{row['Recommended Action']}
"""
                    )

            # --------------------------------------------------
            # MEDIUM PRIORITY
            # --------------------------------------------------

            if not medium_actions.empty:

                st.warning(
                    "### 🟠 Strategic Management Actions"
                )

                for index, row in medium_actions.iterrows():

                    st.markdown(
                        f"""
**{row['Recommendation']}**

**Business Reason:**  
{row['Why']}

**Recommended Action:**  
{row['Recommended Action']}
"""
                    )

            # --------------------------------------------------
            # LOW PRIORITY
            # --------------------------------------------------

            if not low_actions.empty:

                st.info(
                    "### 🟢 Optimization Opportunities"
                )

                for index, row in low_actions.iterrows():

                    st.markdown(
                        f"""
**{row['Recommendation']}**

**Business Reason:**  
{row['Why']}

**Recommended Action:**  
{row['Recommended Action']}
"""
                    )

    except Exception as e:

        st.warning(
            f"Could not create action plan: {str(e)}"
        )

    # ==================================================
    # REPORT METHODOLOGY
    # ==================================================

    with st.expander(
        "🔬 How is the management report generated?"
    ):

        st.markdown(
            """
### AI Executive Reporting Pipeline

The management report combines information from all
major components of the AI Business Intelligence Analyst.

#### 1️⃣ Dataset Analysis

The system examines:

- Dataset size
- Columns
- Data types
- Missing values
- Duplicate records
- Business metrics

#### 2️⃣ Business Analytics

The report evaluates:

- Revenue
- Profit
- Profit margin
- Orders
- Quantity
- Average order value
- Regional performance
- Product performance
- Customer segments
- Monthly trends

#### 3️⃣ Anomaly Detection

The system checks for unusual:

- Sales changes
- Profit changes
- Regional performance
- Product performance

#### 4️⃣ AI Recommendations

The recommendation engine identifies:

- Sales opportunities
- Product opportunities
- Profitability improvements
- Customer segment opportunities
- Anomaly-related actions
- Data quality issues

#### 5️⃣ Executive Decision Support

The final report converts the analysis into:

- Key business findings
- Business risks
- Opportunities
- Recommended actions
- Management priorities

### 🎯 Objective

The goal is to transform raw business data into a
management-ready decision-support report.
"""
        )

        # ============================================================
# PART 9 — AI-POWERED EMAIL ALERT SYSTEM
# ============================================================

def render_email_alert(df):

    st.markdown("---")

    st.header("📧 AI-Powered Email Alert System")

    st.write(
        "Automatically prepare and send an executive email "
        "when important business anomalies are detected."
    )

    # --------------------------------------------------------
    # Detect anomalies
    # --------------------------------------------------------

    try:

        anomalies = detect_all_anomalies(df)

        anomaly_records = get_anomaly_records(df)

        anomaly_summary = generate_anomaly_summary(df)

        recommendations = generate_recommendations(df)

    except Exception as e:

        st.error(
            f"❌ Unable to generate anomaly information: {e}"
        )

        return

    # --------------------------------------------------------
    # Check whether anomalies exist
    # --------------------------------------------------------

    if anomaly_records is None:

        st.info(
            "✅ No significant anomalies were detected. "
            "An email alert is not required."
        )

        return

    # Convert different possible formats safely
    if isinstance(anomaly_records, pd.DataFrame):

        anomaly_count = len(anomaly_records)

    elif isinstance(anomaly_records, list):

        anomaly_count = len(anomaly_records)

    elif isinstance(anomaly_records, dict):

        anomaly_count = len(anomaly_records)

    else:

        anomaly_count = 1

    # --------------------------------------------------------
    # Alert status
    # --------------------------------------------------------

    st.subheader("🚨 Alert Status")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Detected Anomalies",
            anomaly_count
        )

    with col2:

        if anomaly_count > 0:

            st.success(
                "⚠️ Management attention recommended"
            )

        else:

            st.success(
                "✅ No alert required"
            )

    # --------------------------------------------------------
    # Show anomaly records
    # --------------------------------------------------------

    if isinstance(anomaly_records, pd.DataFrame):

        if not anomaly_records.empty:

            with st.expander(
                "🔎 View Detected Anomalies"
            ):

                st.dataframe(
                    anomaly_records,
                    use_container_width=True
                )

    elif isinstance(anomaly_records, list):

        with st.expander(
            "🔎 View Detected Anomalies"
        ):

            for item in anomaly_records:

                st.write(
                    f"• {item}"
                )

    # --------------------------------------------------------
    # Generate email
    # --------------------------------------------------------

    st.subheader("📨 Executive Alert")

    st.write(
        "Enter the recipient details below to prepare "
        "the automated management alert."
    )

    col1, col2 = st.columns(2)

    with col1:

        sender_email = st.text_input(
            "Sender Gmail",
            placeholder="your-email@gmail.com",
            key="alert_sender_email"
        )

    with col2:

        receiver_email = st.text_input(
            "Receiver Email",
            placeholder="manager@company.com",
            key="alert_receiver_email"
        )

    sender_password = st.text_input(
        "Gmail App Password",
        type="password",
        placeholder="Enter your Gmail App Password",
        key="alert_sender_password"
    )

    subject = st.text_input(
        "Email Subject",
        value="🚨 AI Business Intelligence Alert — Anomaly Detected",
        key="alert_subject"
    )

    # --------------------------------------------------------
    # Generate email preview
    # --------------------------------------------------------

    if st.button(
        "👁️ Generate Email Preview",
        use_container_width=True,
        key="generate_email_preview"
    ):

        try:

            email_content = create_alert_email(
                anomaly_summary,
                recommendations
            )

            st.session_state[
                "email_alert_content"
            ] = email_content

            st.success(
                "✅ Executive email generated."
            )

        except Exception as e:

            st.error(
                f"❌ Email generation failed: {e}"
            )

    # --------------------------------------------------------
    # Display email preview
    # --------------------------------------------------------

    if "email_alert_content" in st.session_state:

        st.subheader("📋 Email Preview")

        st.components.v1.html(
            st.session_state[
                "email_alert_content"
            ],
            height=500,
            scrolling=True
        )

        st.markdown("---")

        # ----------------------------------------------------
        # Send email
        # ----------------------------------------------------

        if st.button(
            "📩 Send Executive Alert",
            use_container_width=True,
            type="primary",
            key="send_executive_alert"
        ):

            if not sender_email:

                st.warning(
                    "⚠️ Please enter the sender Gmail address."
                )

                return

            if not sender_password:

                st.warning(
                    "⚠️ Please enter the Gmail App Password."
                )

                return

            if not receiver_email:

                st.warning(
                    "⚠️ Please enter the receiver email."
                )

                return

            success, message = send_email_alert(
                sender_email=sender_email,
                sender_password=sender_password,
                receiver_email=receiver_email,
                subject=subject,
                html_content=st.session_state[
                    "email_alert_content"
                ]
            )

            if success:

                st.success(
                    f"✅ {message}"
                )

                st.balloons()

            else:

                st.error(
                    f"❌ {message}"
                )


# ==================================================
# EMPTY STATE
# ==================================================

def render_empty_state():

    st.info(
        "👈 Upload a CSV or Excel file from "
        "the sidebar to begin."
    )

    st.markdown(
        "### 🚀 What this AI Analyst will do"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            ### 📊 Analyze

            Automatically understand your business
            dataset, KPIs, trends and patterns.
            """
        )

    with col2:

        st.markdown(
            """
            ### 🤖 Explain

            Ask business questions in natural language
            and receive data-backed answers.
            """
        )

    with col3:

        st.markdown(
            """
            ### 💡 Recommend

            Generate actionable business recommendations
            from your data.
            """
        )


# ==================================================
# MAIN APPLICATION
# ==================================================

def main():

    render_header()

    uploaded_file = render_sidebar()

    if uploaded_file is not None:

        try:

            # ==================================================
            # LOAD DATA
            # ==================================================

            df = load_file(
                uploaded_file
            )

            st.success(
                f"✅ Successfully loaded: "
                f"{uploaded_file.name}"
            )

            render_detected_schema(df)

            # ==================================================
            # PART 1
            # DATASET OVERVIEW
            # ==================================================

            render_dataset_overview(df)

            # ==================================================
            # PART 2
            # DATA QUALITY
            # ==================================================

            render_data_quality_analysis(df)

            # ==================================================
            # PART 3
            # DATA CLEANING
            # ==================================================

            render_cleaning_section(df)

            # ==================================================
            # PART 4
            # INTERACTIVE DASHBOARD
            # ==================================================

            render_interactive_dashboard(df)

            # ==================================================
            # PART 5
            # AI BUSINESS ANALYST
            # ==================================================

            render_ai_analyst(df)

            # ==================================================
            # PART 6
            # ANOMALY DETECTION
            # ==================================================

            render_anomaly_detection(df)

            # ==================================================
            # PART 7
            # AI BUSINESS RECOMMENDATIONS
            # ==================================================

            render_business_recommendations(df)

            # ==================================================
            # PART 8
            # AI EXECUTIVE MANAGEMENT REPORT
            # ==================================================

            render_management_report(df)

            # PART 9
            render_email_alert(df)

            # PART 10
            render_ai_chat_assistant(df) 

        except Exception as e:

            st.error(
                f"❌ Error: {str(e)}"
            )


    else:

        render_empty_state()


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    main()