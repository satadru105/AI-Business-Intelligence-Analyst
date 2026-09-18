# 🤖 AI-Powered Business Intelligence Analyst

An end-to-end **AI-powered Business Intelligence and Data Analytics application** built with **Python and Streamlit**.

The application allows users to upload business data and automatically perform data quality analysis, cleaning, KPI analysis, interactive visualization, anomaly detection, AI-powered insights, business recommendations, executive reporting, email alerts, and natural-language data analysis.

---

## 🚀 Project Overview

Traditional data analysis often requires multiple tools and manual steps to clean data, create dashboards, identify unusual patterns, generate reports, and communicate business insights.

This project brings these workflows together into a single interactive application.

### 🔄 Workflow

```text
Upload CSV / Excel
        ↓
Data Quality Analysis
        ↓
Automatic Data Cleaning
        ↓
Business Analytics
        ↓
Interactive Dashboard
        ↓
AI Business Analyst
        ↓
Anomaly Detection
        ↓
Business Recommendations
        ↓
Executive Management Report
        ↓
Email Alerts
        ↓
AI Analyst Chat Assistant
```

---

## ✨ Key Features

### 1. 📂 Data Upload

Upload business datasets in:

* CSV format
* Excel format

The application automatically loads the dataset for analysis.

---

### 2. 🔍 Data Quality Analysis

Automatically evaluates the uploaded dataset for common data-quality problems.

Includes:

* Missing values
* Duplicate records
* Duplicate IDs
* Text consistency
* Outliers
* Date validation
* Overall data-quality score
* Quality status

---

### 3. 🧹 Automatic Data Cleaning

Automatically processes detected data-quality issues.

The cleaned dataset can be generated and saved as:

```text
cleaned_sales_data.csv
```

This reduces the amount of manual preprocessing required before analysis.

---

### 4. 📊 Interactive Business Dashboard

The dashboard provides interactive business analytics using Plotly.

### KPIs

* Total Revenue
* Total Profit
* Total Orders
* Total Quantity
* Average Order Value
* Profit Margin

### Filters

Users can analyze the data using filters such as:

* Region
* Category
* Customer Segment
* Sales Channel
* Order Date

The dashboard also provides visual analysis of business performance.

---

### 5. 🤖 AI Business Analyst

Users can ask questions about their dataset using natural language.

Example questions:

```text
Which region generated the most revenue?

Why did sales decrease?

Which product is underperforming?
```

The system analyzes the available data and provides data-driven answers.

---

### 6. 🚨 AI-Powered Anomaly Detection

The application automatically identifies unusual business patterns.

It can analyze changes in:

* Sales
* Profit
* Regional performance
* Product performance
* Other business metrics

Detected anomalies are presented for further investigation.

---

### 7. 💡 AI Business Recommendations

After analyzing business performance and anomalies, the application generates actionable recommendations.

Recommendations can help identify areas such as:

* Underperforming products
* Declining regions
* Profitability problems
* Sales opportunities
* Areas requiring management attention

---

### 8. 📄 AI Executive Management Report

The application can generate an automated PDF management report.

The report can contain:

* Executive summary
* Data-quality analysis
* Key performance indicators
* Sales analysis
* Regional analysis
* Product analysis
* Profit analysis
* Customer-segment analysis
* Detected anomalies
* Business recommendations
* Suggested action plan

The generated report can be downloaded directly from the application.

---

### 9. 📧 AI-Powered Email Alert System

The application can send automated email alerts when important anomalies are detected.

The alert system can communicate:

* Detected anomaly
* Relevant business metric
* Change in performance
* Business impact
* Recommended attention/action

Gmail SMTP and Google App Password authentication can be used for email delivery.

> ⚠️ Never upload your email password, App Password, API key, or other credentials to GitHub.

Use environment variables or a secure secrets mechanism instead.

---

### 10. 💬 AI Analyst Chat Assistant

The application includes an interactive analyst-style chat interface.

Users can ask questions about their dataset and receive analytical responses without manually writing SQL or Python code.

Example:

```text
Which category has the highest revenue?

What is the most profitable region?

Which products are performing poorly?

What business areas require attention?
```

---

## 🛠️ Tech Stack

| Technology | Purpose                      |
| ---------- | ---------------------------- |
| Python     | Core programming language    |
| Streamlit  | Interactive web application  |
| Pandas     | Data processing and analysis |
| NumPy      | Numerical operations         |
| Plotly     | Interactive visualizations   |
| OpenPyXL   | Excel file processing        |
| ReportLab  | PDF report generation        |
| SMTP       | Email alert delivery         |

---

## 📁 Project Structure

```text
AI-Business-Intelligence-Analyst/
│
├── app.py
├── requirements.txt
├── README.md
│
├── modules/
│   ├── data_loader.py
│   ├── data_quality.py
│   ├── analytics.py
│   ├── ai_analyst.py
│   ├── anomaly_detection.py
│   ├── recommendations.py
│   ├── report_generator.py
│   ├── email_alert.py
│   └── chat_assistant.py
│
├── data/
│   └── sample_sales_data.csv
│
└── screenshots/
    ├── dashboard.png
    ├── data_quality.png
    ├── anomaly_detection.png
    ├── recommendations.png
    └── management_report.png
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/satadru105/AI-Business-Intelligence-Analyst.git
```

### 2. Open the project

```bash
cd AI-Business-Intelligence-Analyst
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 📦 Requirements

The project uses the following Python packages:

```text
streamlit
pandas
numpy
openpyxl
plotly
reportlab
```

---

## 🧪 How to Use

### Step 1

Start the Streamlit application.

### Step 2

Upload a CSV or Excel dataset.

### Step 3

Review the automatic data-quality analysis.

### Step 4

Clean the dataset if required.

### Step 5

Explore the interactive dashboard.

### Step 6

Ask questions using the AI Business Analyst.

### Step 7

Review detected anomalies.

### Step 8

Review generated business recommendations.

### Step 9

Generate and download the executive management report.

### Step 10

Use the email alert and AI chat features for ongoing analysis.

---

## 📈 Example Business Questions

The application can be used to investigate questions such as:

```text
Which region generated the most revenue?

Which product has the lowest performance?

Which category is most profitable?

Why has sales performance decreased?

Which customer segment generates the highest revenue?

Where are unusual changes occurring?

What areas should management investigate?
```

---

## 🎯 Business Value

This project demonstrates how data analytics can be combined with automation and AI-style analytical workflows to create a complete business intelligence solution.

It helps reduce repetitive manual work involved in:

* Data preparation
* KPI calculation
* Dashboard creation
* Anomaly investigation
* Business insight generation
* Recommendation generation
* Management reporting
* Alert communication

---

## 👨‍💻 Skills Demonstrated

This project demonstrates practical experience with:

* Python
* Pandas
* NumPy
* Streamlit
* Data Cleaning
* Exploratory Data Analysis
* KPI Analysis
* Business Intelligence
* Data Visualization
* Plotly
* Anomaly Detection
* Automated Reporting
* PDF Generation
* Email Automation
* Natural-Language Data Analysis
* Business Recommendations

---

## 🔮 Future Improvements

Potential future enhancements include:

* Support for more dataset types
* Automatic dataset schema detection
* More advanced AI/LLM integration
* SQL database connectivity
* Power BI integration
* Scheduled automated reports
* Cloud deployment
* User authentication
* Advanced forecasting
* More advanced predictive analytics

---

## 📌 Project Highlights

```text
✅ End-to-end Business Intelligence workflow
✅ Automated data-quality analysis
✅ Automatic data cleaning
✅ Interactive KPI dashboard
✅ Natural-language data analysis
✅ Automated anomaly detection
✅ Business recommendations
✅ PDF executive reporting
✅ Email anomaly alerts
✅ AI analyst chat interface
```

---

## 📄 License

This project is intended for educational, portfolio, and demonstration purposes.

---

## ⭐ If you find this project useful

Consider giving the repository a ⭐ on GitHub.
