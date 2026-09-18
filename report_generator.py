# ============================================================
# AI BUSINESS INTELLIGENCE MANAGEMENT REPORT
# ============================================================

from io import BytesIO
from datetime import datetime

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_number(value, default=0):
    """
    Safely convert a value into a numeric value.
    """

    try:
        if pd.isna(value):
            return default

        return float(value)

    except Exception:
        return default


def safe_text(value):
    """
    Safely convert a value into text.
    """

    if value is None:
        return ""

    try:

        if pd.isna(value):
            return ""

    except Exception:
        pass

    return str(value)


def format_currency(value):
    """
    Format number as Indian currency.
    """

    try:

        return f"₹{safe_number(value):,.2f}"

    except Exception:

        return "₹0.00"


def format_number(value):
    """
    Format numeric value.
    """

    try:

        return f"{safe_number(value):,.0f}"

    except Exception:

        return "0"


# ============================================================
# PAGE HEADER / FOOTER
# ============================================================

def add_page_header_footer(canvas, doc):

    canvas.saveState()

    width, height = A4

    # Header line
    canvas.setStrokeColor(colors.HexColor("#D9E2F3"))
    canvas.line(
        18 * mm,
        height - 15 * mm,
        width - 18 * mm,
        height - 15 * mm
    )

    # Header title
    canvas.setFont(
        "Helvetica-Bold",
        8
    )

    canvas.setFillColor(
        colors.HexColor("#334155")
    )

    canvas.drawString(
        18 * mm,
        height - 11 * mm,
        "AI Business Intelligence Analyst"
    )

    # Footer line
    canvas.setStrokeColor(
        colors.HexColor("#D9E2F3")
    )

    canvas.line(
        18 * mm,
        14 * mm,
        width - 18 * mm,
        14 * mm
    )

    # Footer
    canvas.setFont(
        "Helvetica",
        8
    )

    canvas.setFillColor(
        colors.HexColor("#64748B")
    )

    canvas.drawString(
        18 * mm,
        9 * mm,
        "Automated Management Report"
    )

    canvas.drawRightString(
        width - 18 * mm,
        9 * mm,
        f"Page {doc.page}"
    )

    canvas.restoreState()


# ============================================================
# TABLE HELPER
# ============================================================

def create_table(
    data,
    col_widths=None,
    header=True
):

    table = Table(
        data,
        colWidths=col_widths,
        repeatRows=1 if header else 0
    )

    style_commands = [
        (
            "FONTNAME",
            (0, 0),
            (-1, -1),
            "Helvetica"
        ),
        (
            "FONTSIZE",
            (0, 0),
            (-1, -1),
            8
        ),
        (
            "VALIGN",
            (0, 0),
            (-1, -1),
            "TOP"
        ),
        (
            "LEFTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "RIGHTPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "TOPPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "BOTTOMPADDING",
            (0, 0),
            (-1, -1),
            6
        ),
        (
            "GRID",
            (0, 0),
            (-1, -1),
            0.4,
            colors.HexColor("#CBD5E1")
        ),
    ]

    if header:

        style_commands.extend(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1E3A5F")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
            ]
        )

        # Alternate rows

        for row in range(1, len(data)):

            if row % 2 == 0:

                style_commands.append(
                    (
                        "BACKGROUND",
                        (0, row),
                        (-1, row),
                        colors.HexColor("#F8FAFC")
                    )
                )

    table.setStyle(
        TableStyle(style_commands)
    )

    return table


# ============================================================
# SECTION TITLE
# ============================================================

def section_title(text, styles):

    return Paragraph(
        text,
        styles["SectionTitle"]
    )


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

def build_executive_summary(
    df,
    analytics,
    anomaly_summary,
    recommendations
):

    kpis = analytics.get(
        "kpis",
        {}
    )

    total_revenue = safe_number(
        kpis.get("Total Revenue")
    )

    total_profit = safe_number(
        kpis.get("Total Profit")
    )

    total_orders = safe_number(
        kpis.get("Total Orders")
    )

    profit_margin = safe_number(
        kpis.get("Profit Margin")
    )

    average_order_value = safe_number(
        kpis.get("Average Order Value")
    )

    best_region = analytics.get(
        "regions",
        {}
    ).get(
        "best_region"
    )

    worst_region = analytics.get(
        "regions",
        {}
    ).get(
        "worst_region"
    )

    anomaly_count = anomaly_summary.get(
        "total",
        0
    )

    high_anomalies = anomaly_summary.get(
        "high",
        0
    )

    recommendation_count = len(
        recommendations
    ) if isinstance(
        recommendations,
        pd.DataFrame
    ) else 0

    high_recommendations = 0

    if isinstance(
        recommendations,
        pd.DataFrame
    ) and not recommendations.empty:

        if "Priority" in recommendations.columns:

            high_recommendations = len(
                recommendations[
                    recommendations["Priority"]
                    .astype(str)
                    .str.lower()
                    == "high"
                ]
            )

    summary = []

    summary.append(
        f"The analyzed dataset contains "
        f"<b>{format_number(len(df))}</b> records "
        f"across <b>{format_number(len(df.columns))}</b> columns."
    )

    summary.append(
        f"The business generated "
        f"<b>{format_currency(total_revenue)}</b> in total revenue "
        f"and <b>{format_currency(total_profit)}</b> in total profit."
    )

    summary.append(
        f"A total of <b>{format_number(total_orders)}</b> orders "
        f"were recorded with an average order value of "
        f"<b>{format_currency(average_order_value)}</b>."
    )

    summary.append(
        f"The overall profit margin is "
        f"<b>{profit_margin:.2f}%</b>."
    )

    if best_region:

        summary.append(
            f"The strongest performing region is "
            f"<b>{safe_text(best_region)}</b>."
        )

    if worst_region:

        summary.append(
            f"The lowest-performing region is "
            f"<b>{safe_text(worst_region)}</b>, "
            f"which should be monitored for improvement opportunities."
        )

    if anomaly_count > 0:

        summary.append(
            f"The anomaly detection engine identified "
            f"<b>{format_number(anomaly_count)}</b> potential anomalies, "
            f"including <b>{format_number(high_anomalies)}</b> high-severity cases."
        )

    else:

        summary.append(
            "No significant statistical business anomalies "
            "were detected in the analyzed dataset."
        )

    summary.append(
        f"The recommendation engine generated "
        f"<b>{format_number(recommendation_count)}</b> "
        f"business recommendations."
    )

    if high_recommendations > 0:

        summary.append(
            f"<b>{format_number(high_recommendations)}</b> "
            f"recommendations require high priority attention."
        )

    return summary


# ============================================================
# KPI TABLE
# ============================================================

def build_kpi_table(analytics):

    kpis = analytics.get(
        "kpis",
        {}
    )

    return [
        [
            "KPI",
            "Value"
        ],
        [
            "Total Revenue",
            format_currency(
                kpis.get("Total Revenue")
            )
        ],
        [
            "Total Profit",
            format_currency(
                kpis.get("Total Profit")
            )
        ],
        [
            "Total Orders",
            format_number(
                kpis.get("Total Orders")
            )
        ],
        [
            "Total Quantity",
            format_number(
                kpis.get("Total Quantity")
            )
        ],
        [
            "Average Order Value",
            format_currency(
                kpis.get("Average Order Value")
            )
        ],
        [
            "Profit Margin",
            f"{safe_number(kpis.get('Profit Margin')):.2f}%"
        ],
    ]


# ============================================================
# REGIONAL PERFORMANCE
# ============================================================

def build_region_table(analytics):

    region_data = analytics.get(
        "region",
        pd.DataFrame()
    )

    if region_data.empty:

        return None

    data = [
        [
            "Region",
            "Revenue"
        ]
    ]

    temp = region_data.copy()

    if "Sales" in temp.columns:

        temp = temp.sort_values(
            "Sales",
            ascending=False
        )

        for _, row in temp.head(10).iterrows():

            data.append(
                [
                    safe_text(
                        row.get("Region")
                    ),
                    format_currency(
                        row.get("Sales")
                    )
                ]
            )

    return data


# ============================================================
# PRODUCT PERFORMANCE
# ============================================================

def build_product_table(analytics):

    product_data = analytics.get(
        "top_products",
        pd.DataFrame()
    )

    if product_data.empty:

        return None

    data = [
        [
            "Product",
            "Revenue"
        ]
    ]

    for _, row in product_data.head(10).iterrows():

        data.append(
            [
                safe_text(
                    row.get("Product")
                ),
                format_currency(
                    row.get("Sales")
                )
            ]
        )

    return data


# ============================================================
# PROFIT PERFORMANCE
# ============================================================

def build_profit_table(analytics):

    profit_data = analytics.get(
        "product_profit",
        pd.DataFrame()
    )

    if profit_data.empty:

        return None

    data = [
        [
            "Product",
            "Profit"
        ]
    ]

    temp = profit_data.copy()

    if "Profit" in temp.columns:

        temp = temp.sort_values(
            "Profit",
            ascending=False
        )

        for _, row in temp.head(10).iterrows():

            data.append(
                [
                    safe_text(
                        row.get("Product")
                    ),
                    format_currency(
                        row.get("Profit")
                    )
                ]
            )

    return data


# ============================================================
# CUSTOMER SEGMENT
# ============================================================

def build_segment_table(analytics):

    segment_data = analytics.get(
        "segments",
        pd.DataFrame()
    )

    if segment_data.empty:

        return None

    data = [
        [
            "Customer Segment",
            "Revenue"
        ]
    ]

    temp = segment_data.copy()

    if "Revenue" in temp.columns:

        temp = temp.sort_values(
            "Revenue",
            ascending=False
        )

        for _, row in temp.iterrows():

            data.append(
                [
                    safe_text(
                        row.get("Customer_Segment")
                    ),
                    format_currency(
                        row.get("Revenue")
                    )
                ]
            )

    return data


# ============================================================
# ANOMALY TABLE
# ============================================================

def build_anomaly_table(anomaly_records):

    if anomaly_records is None:

        return None

    if anomaly_records.empty:

        return None

    data = [
        [
            "Type",
            "Metric",
            "Value",
            "Severity",
            "Issue"
        ]
    ]

    for _, row in anomaly_records.head(20).iterrows():

        value = row.get(
            "Value",
            0
        )

        data.append(
            [
                safe_text(
                    row.get("Type")
                ),
                safe_text(
                    row.get("Metric")
                ),
                format_currency(
                    value
                ),
                safe_text(
                    row.get("Severity")
                ),
                safe_text(
                    row.get("Anomaly")
                )
            ]
        )

    return data


# ============================================================
# RECOMMENDATION TABLE
# ============================================================

def build_recommendation_table(
    recommendations
):

    if recommendations is None:

        return None

    if not isinstance(
        recommendations,
        pd.DataFrame
    ):

        return None

    if recommendations.empty:

        return None

    data = [
        [
            "Category",
            "Recommendation",
            "Priority",
            "Recommended Action"
        ]
    ]

    for _, row in recommendations.head(20).iterrows():

        data.append(
            [
                safe_text(
                    row.get("Category")
                ),
                safe_text(
                    row.get("Recommendation")
                ),
                safe_text(
                    row.get("Priority")
                ),
                safe_text(
                    row.get("Recommended Action")
                )
            ]
        )

    return data


# ============================================================
# MAIN PDF GENERATOR
# ============================================================

def generate_management_report(
    df,
    analytics,
    anomaly_summary,
    anomaly_records,
    recommendations
):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17365D"),
            spaceAfter=8
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=18
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#17365D"),
            spaceBefore=12,
            spaceAfter=10
        )
    )

    styles.add(
        ParagraphStyle(
            name="BodyTextCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#334155"),
            spaceAfter=8
        )
    )

    styles.add(
        ParagraphStyle(
            name="SmallText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#475569")
        )
    )

    styles.add(
        ParagraphStyle(
            name="ActionTitle",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#17365D"),
            spaceAfter=4
        )
    )

    story = []

    # ========================================================
    # COVER
    # ========================================================

    story.append(
        Spacer(
            1,
            30 * mm
        )
    )

    story.append(
        Paragraph(
            "AI BUSINESS INTELLIGENCE",
            styles["ReportTitle"]
        )
    )

    story.append(
        Paragraph(
            "Automated Management Report",
            styles["ReportTitle"]
        )
    )

    story.append(
        Spacer(
            1,
            8 * mm
        )
    )

    story.append(
        Paragraph(
            "AI-powered analysis of business performance, "
            "data quality, anomalies and strategic opportunities.",
            styles["ReportSubtitle"]
        )
    )

    story.append(
        Spacer(
            1,
            10 * mm
        )
    )

    cover_data = [
        [
            "Report Generated",
            datetime.now().strftime(
                "%d %B %Y, %I:%M %p"
            )
        ],
        [
            "Records Analyzed",
            format_number(
                len(df)
            )
        ],
        [
            "Columns Analyzed",
            format_number(
                len(df.columns)
            )
        ],
        [
            "Report Type",
            "Automated Business Intelligence"
        ]
    ]

    cover_table = Table(
        cover_data,
        colWidths=[
            55 * mm,
            105 * mm
        ]
    )

    cover_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#17365D")
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (0, -1),
                    colors.white
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),
                (
                    "BACKGROUND",
                    (1, 0),
                    (1, -1),
                    colors.HexColor("#F1F5F9")
                ),
                (
                    "TEXTCOLOR",
                    (1, 0),
                    (1, -1),
                    colors.HexColor("#334155")
                ),
                (
                    "FONTNAME",
                    (1, 0),
                    (1, -1),
                    "Helvetica"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1")
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    8
                )
            ]
        )
    )

    story.append(
        cover_table
    )

    story.append(
        Spacer(
            1,
            15 * mm
        )
    )

    story.append(
        Paragraph(
            "Generated by AI-Powered Business Intelligence Analyst",
            styles["SmallText"]
        )
    )

    story.append(
        PageBreak()
    )

    # ========================================================
    # EXECUTIVE SUMMARY
    # ========================================================

    story.append(
        section_title(
            "1. Executive Summary",
            styles
        )
    )

    summary_items = build_executive_summary(
        df,
        analytics,
        anomaly_summary,
        recommendations
    )

    for item in summary_items:

        story.append(
            Paragraph(
                "• " + item,
                styles["BodyTextCustom"]
            )
        )

    # ========================================================
    # DATASET OVERVIEW
    # ========================================================

    story.append(
        section_title(
            "2. Dataset & Data Quality Overview",
            styles
        )
    )

    missing_values = int(
        df.isnull().sum().sum()
    )

    duplicate_rows = int(
        df.duplicated().sum()
    )

    numeric_columns = len(
        df.select_dtypes(
            include="number"
        ).columns
    )

    categorical_columns = len(
        df.select_dtypes(
            include="object"
        ).columns
    )

    dataset_data = [
        [
            "Metric",
            "Value"
        ],
        [
            "Total Records",
            format_number(len(df))
        ],
        [
            "Total Columns",
            format_number(len(df.columns))
        ],
        [
            "Missing Values",
            format_number(missing_values)
        ],
        [
            "Duplicate Rows",
            format_number(duplicate_rows)
        ],
        [
            "Numeric Columns",
            format_number(numeric_columns)
        ],
        [
            "Categorical Columns",
            format_number(categorical_columns)
        ]
    ]

    story.append(
        create_table(
            dataset_data,
            col_widths=[
                80 * mm,
                80 * mm
            ]
        )
    )

    story.append(
        Spacer(
            1,
            8
        )
    )

    if missing_values == 0:

        quality_message = (
            "The dataset contains no missing values."
        )

    else:

        quality_message = (
            f"The dataset contains {format_number(missing_values)} "
            "missing values that should be reviewed."
        )

    if duplicate_rows == 0:

        duplicate_message = (
            "No duplicate records were detected."
        )

    else:

        duplicate_message = (
            f"{format_number(duplicate_rows)} duplicate "
            "records were detected."
        )

    story.append(
        Paragraph(
            f"Data Quality Assessment: {quality_message} "
            f"{duplicate_message}",
            styles["BodyTextCustom"]
        )
    )

    # ========================================================
    # KPI SUMMARY
    # ========================================================

    story.append(
        section_title(
            "3. KPI Summary",
            styles
        )
    )

    story.append(
        create_table(
            build_kpi_table(
                analytics
            ),
            col_widths=[
                80 * mm,
                80 * mm
            ]
        )
    )

    # ========================================================
    # SALES PERFORMANCE
    # ========================================================

    story.append(
        section_title(
            "4. Sales Performance",
            styles
        )
    )

    monthly_data = analytics.get(
        "monthly",
        pd.DataFrame()
    )

    if not monthly_data.empty:

        if "Sales" in monthly_data.columns:

            monthly_sorted = monthly_data.sort_values(
                "Sales",
                ascending=False
            )

            best_month = monthly_sorted.iloc[0]

            worst_month = monthly_sorted.iloc[-1]

            story.append(
                Paragraph(
                    f"Highest revenue period: "
                    f"<b>{safe_text(best_month.get('Month'))}</b> "
                    f"with revenue of "
                    f"<b>{format_currency(best_month.get('Sales'))}</b>.",
                    styles["BodyTextCustom"]
                )
            )

            story.append(
                Paragraph(
                    f"Lowest revenue period: "
                    f"<b>{safe_text(worst_month.get('Month'))}</b> "
                    f"with revenue of "
                    f"<b>{format_currency(worst_month.get('Sales'))}</b>.",
                    styles["BodyTextCustom"]
                )
            )

    else:

        story.append(
            Paragraph(
                "Monthly sales data was not available "
                "for detailed trend analysis.",
                styles["BodyTextCustom"]
            )
        )

    # ========================================================
    # REGIONAL PERFORMANCE
    # ========================================================

    story.append(
        section_title(
            "5. Regional Performance",
            styles
        )
    )

    region_table = build_region_table(
        analytics
    )

    if region_table:

        story.append(
            create_table(
                region_table,
                col_widths=[
                    90 * mm,
                    70 * mm
                ]
            )
        )

    else:

        story.append(
            Paragraph(
                "Regional performance data was not available.",
                styles["BodyTextCustom"]
            )
        )

    # ========================================================
    # PRODUCT PERFORMANCE
    # ========================================================

    story.append(
        section_title(
            "6. Product Performance",
            styles
        )
    )

    product_table = build_product_table(
        analytics
    )

    if product_table:

        story.append(
            create_table(
                product_table,
                col_widths=[
                    90 * mm,
                    70 * mm
                ]
            )
        )

    else:

        story.append(
            Paragraph(
                "Product performance data was not available.",
                styles["BodyTextCustom"]
            )
        )

    # ========================================================
    # PROFIT ANALYSIS
    # ========================================================

    story.append(
        section_title(
            "7. Profit Analysis",
            styles
        )
    )

    profit_table = build_profit_table(
        analytics
    )

    if profit_table:

        story.append(
            create_table(
                profit_table,
                col_widths=[
                    90 * mm,
                    70 * mm
                ]
            )
        )

    else:

        story.append(
            Paragraph(
                "Product-level profit data was not available.",
                styles["BodyTextCustom"]
            )
        )

    # ========================================================
    # CUSTOMER SEGMENT
    # ========================================================

    story.append(
        section_title(
            "8. Customer Segment Analysis",
            styles
        )
    )

    segment_table = build_segment_table(
        analytics
    )

    if segment_table:

        story.append(
            create_table(
                segment_table,
                col_widths=[
                    90 * mm,
                    70 * mm
                ]
            )
        )

    else:

        story.append(
            Paragraph(
                "Customer segment data was not available.",
                styles["BodyTextCustom"]
            )
        )

    # ========================================================
    # ANOMALIES
    # ========================================================

    story.append(
        PageBreak()
    )

    story.append(
        section_title(
            "9. AI-Powered Anomaly Detection",
            styles
        )
    )

    anomaly_summary_data = [
        [
            "Anomaly Metric",
            "Count"
        ],
        [
            "Total Anomalies",
            format_number(
                anomaly_summary.get(
                    "total",
                    0
                )
            )
        ],
        [
            "High Severity",
            format_number(
                anomaly_summary.get(
                    "high",
                    0
                )
            )
        ],
        [
            "Medium Severity",
            format_number(
                anomaly_summary.get(
                    "medium",
                    0
                )
            )
        ],
        [
            "Low Severity",
            format_number(
                anomaly_summary.get(
                    "low",
                    0
                )
            )
        ]
    ]

    story.append(
        create_table(
            anomaly_summary_data,
            col_widths=[
                100 * mm,
                60 * mm
            ]
        )
    )

    story.append(
        Spacer(
            1,
            8
        )
    )

    anomaly_table = build_anomaly_table(
        anomaly_records
    )

    if anomaly_table:

        story.append(
            create_table(
                anomaly_table,
                col_widths=[
                    27 * mm,
                    28 * mm,
                    27 * mm,
                    25 * mm,
                    53 * mm
                ]
            )
        )

    else:

        story.append(
            Paragraph(
                "No significant business anomalies "
                "were detected.",
                styles["BodyTextCustom"]
            )
        )

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    story.append(
        PageBreak()
    )

    story.append(
        section_title(
            "10. AI Business Recommendations",
            styles
        )
    )

    recommendation_table = build_recommendation_table(
        recommendations
    )

    if recommendation_table:

        story.append(
            create_table(
                recommendation_table,
                col_widths=[
                    28 * mm,
                    48 * mm,
                    22 * mm,
                    62 * mm
                ]
            )
        )

    else:

        story.append(
            Paragraph(
                "No business recommendations were generated.",
                styles["BodyTextCustom"]
            )
        )

    # ========================================================
    # EXECUTIVE ACTION PLAN
    # ========================================================

    story.append(
        section_title(
            "11. Executive Action Plan",
            styles
        )
    )

    if isinstance(
        recommendations,
        pd.DataFrame
    ) and not recommendations.empty:

        priority_order = [
            ("High", "Immediate Actions"),
            ("Medium", "Strategic Improvements"),
            ("Low", "Optimization Opportunities")
        ]

        for priority, title in priority_order:

            priority_rows = recommendations[
                recommendations["Priority"]
                .astype(str)
                .str.lower()
                == priority.lower()
            ]

            if priority_rows.empty:

                continue

            story.append(
                Paragraph(
                    f"{priority} Priority — {title}",
                    styles["ActionTitle"]
                )
            )

            for _, row in priority_rows.head(10).iterrows():

                recommendation = safe_text(
                    row.get(
                        "Recommendation"
                    )
                )

                why = safe_text(
                    row.get(
                        "Why"
                    )
                )

                action = safe_text(
                    row.get(
                        "Recommended Action"
                    )
                )

                action_text = (
                    f"<b>{recommendation}</b><br/>"
                    f"<b>Why:</b> {why}<br/>"
                    f"<b>Recommended Action:</b> {action}"
                )

                story.append(
                    Paragraph(
                        "• " + action_text,
                        styles["BodyTextCustom"]
                    )
                )

    else:

        story.append(
            Paragraph(
                "No immediate business actions were identified "
                "by the recommendation engine.",
                styles["BodyTextCustom"]
            )
        )

    # ========================================================
    # FINAL NOTE
    # ========================================================

    story.append(
        Spacer(
            1,
            10
        )
    )

    story.append(
        Paragraph(
            "<b>Management Note:</b> "
            "This report is automatically generated from the "
            "uploaded business dataset. Statistical findings, "
            "anomalies and recommendations should be reviewed "
            "with appropriate business context before major "
            "decisions are implemented.",
            styles["SmallText"]
        )
    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(
        story,
        onFirstPage=add_page_header_footer,
        onLaterPages=add_page_header_footer
    )

    buffer.seek(0)

    return buffer.getvalue()