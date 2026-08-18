import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

from ai_report import generate_ai_report
from metric_detector import detect_business_metrics, explain_metric
from anomaly_detector import detect_anomalies
from risk_engine import calculate_risk_score
from anomaly_trends import create_anomaly_trend_chart


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

st.set_page_config(
    page_title="AI Business Anomaly Agent",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🤖 AI Business Anomaly Agent")

st.caption(
    "Dynamic business anomaly detection with "
    "statistical analysis, AI insights and risk assessment."
)


# ============================================================
# FILE UPLOAD
# ============================================================

st.sidebar.header("📂 Upload Business Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx", "xls"]
)


if uploaded_file is None:

    st.info(
        "👈 Upload a CSV or Excel file from the sidebar."
    )

    st.markdown(
        """
        ## 🚀 AI Business Anomaly Agent

        Upload any business CSV or Excel dataset and the
        system automatically:

        - 🔍 Understands the uploaded data
        - 📅 Detects date columns
        - 📊 Detects business metrics
        - 🚨 Detects anomalies
        - 📈 Analyzes anomaly trends
        - 🎯 Calculates business risk
        - 🤖 Uses Gemini AI for explanations
        - 💡 Generates recommendations
        - 📥 Creates downloadable reports

        ### Detection Engine

        **Percentage Change + Z-Score**

        ### AI Layer

        **Gemini Business Intelligence Analysis**

        ### Risk Layer

        **Critical / High / Medium / Low**
        """
    )

    st.stop()


# ============================================================
# READ FILE
# ============================================================

try:

    if uploaded_file.name.lower().endswith(".csv"):

        df = pd.read_csv(
            uploaded_file
        )

    else:

        df = pd.read_excel(
            uploaded_file
        )

except Exception as e:

    st.error(
        f"❌ Could not read the uploaded file: {e}"
    )

    st.stop()


# ============================================================
# BASIC CLEANING
# ============================================================

df = df.dropna(
    how="all"
).copy()

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
)

df = df.dropna(
    axis=1,
    how="all"
)


# ============================================================
# AUTOMATIC NUMERIC CONVERSION
# ============================================================

for column in df.columns:

    if df[column].dtype == "object":

        cleaned = (
            df[column]
            .astype(str)
            .str.replace(
                ",",
                "",
                regex=False
            )
            .str.replace(
                "₹",
                "",
                regex=False
            )
            .str.replace(
                "$",
                "",
                regex=False
            )
            .str.replace(
                "€",
                "",
                regex=False
            )
            .str.replace(
                "£",
                "",
                regex=False
            )
            .str.strip()
        )

        converted = pd.to_numeric(
            cleaned,
            errors="coerce"
        )

        if converted.notna().mean() >= 0.85:

            df[column] = converted


# ============================================================
# FILE INFORMATION
# ============================================================

st.sidebar.success(
    f"Loaded: {uploaded_file.name}"
)

st.sidebar.write(
    f"Rows: **{len(df):,}**"
)

st.sidebar.write(
    f"Columns: **{len(df.columns):,}**"
)


# ============================================================
# DATE DETECTION
# ============================================================

date_candidates = []

date_keywords = [
    "date",
    "time",
    "timestamp",
    "day",
    "month"
]


for column in df.columns:

    column_name = str(
        column
    ).lower()

    if any(
        keyword in column_name
        for keyword in date_keywords
    ):

        try:

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            if converted.notna().mean() >= 0.60:

                date_candidates.append(
                    column
                )

        except Exception:

            pass


# ============================================================
# DATE SELECTION
# ============================================================

st.sidebar.header("📅 Date Column")

if date_candidates:

    date_column = st.sidebar.selectbox(
        "Select date column",
        date_candidates
    )

    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce"
    )

    df = df.dropna(
        subset=[date_column]
    )

    df = df.sort_values(
        date_column
    )

else:

    date_column = None

    st.sidebar.info(
        "No date column automatically detected."
    )


# ============================================================
# BUSINESS METRIC DETECTION
# ============================================================

detected_metrics = detect_business_metrics(
    df
)


if not detected_metrics:

    st.error(
        """
        ❌ No suitable business metrics detected.

        Your dataset should contain numeric business
        measurements such as:

        Sales, Revenue, Profit, Cost, Quantity,
        Orders, Customers, Amount, etc.
        """
    )

    st.stop()


# ============================================================
# METRIC SELECTION
# ============================================================

st.sidebar.header("📊 Business Metrics")

selected_metrics = st.sidebar.multiselect(
    "Select metrics to monitor",
    detected_metrics,
    default=detected_metrics[
        :min(5, len(detected_metrics))
    ]
)


if not selected_metrics:

    st.warning(
        "Please select at least one metric."
    )

    st.stop()


# ============================================================
# METRIC INFORMATION
# ============================================================

with st.sidebar.expander(
    "ℹ️ Detected Metric Information"
):

    for metric in detected_metrics:

        st.write(
            f"**{metric}** — "
            f"{explain_metric(metric)}"
        )


# ============================================================
# DETECTION SETTINGS
# ============================================================

st.sidebar.header("⚙️ Detection Settings")

lookback_period = st.sidebar.slider(
    "Historical baseline periods",
    min_value=3,
    max_value=30,
    value=7
)

threshold = st.sidebar.slider(
    "Percentage threshold (%)",
    min_value=5,
    max_value=100,
    value=20,
    step=5
)

z_threshold = st.sidebar.slider(
    "Z-score threshold",
    min_value=1.5,
    max_value=5.0,
    value=2.5,
    step=0.5
)


# ============================================================
# DATASET OVERVIEW
# ============================================================

st.subheader(
    "📋 Dataset Overview"
)

c1, c2, c3, c4 = st.columns(4)


with c1:

    st.metric(
        "Rows",
        f"{len(df):,}"
    )


with c2:

    st.metric(
        "Columns",
        f"{len(df.columns):,}"
    )


with c3:

    st.metric(
        "Metrics",
        f"{len(selected_metrics):,}"
    )


with c4:

    if date_column:

        latest_date = df[
            date_column
        ].max()

        st.metric(
            "Latest Date",
            latest_date.strftime(
                "%Y-%m-%d"
            )
        )

    else:

        st.metric(
            "Date",
            "Not detected"
        )


# ============================================================
# DATA PREVIEW
# ============================================================

with st.expander(
    "🔍 View Uploaded Data"
):

    st.dataframe(
        df,
        use_container_width=True
    )


# ============================================================
# ANOMALY DETECTION
# ============================================================

analysis_df, anomaly_df = detect_anomalies(
    df=df,
    selected_metrics=selected_metrics,
    date_column=date_column,
    lookback_period=lookback_period,
    threshold=threshold,
    z_threshold=z_threshold
)


# ============================================================
# ANOMALY SUMMARY
# ============================================================

st.subheader(
    "🚨 Anomaly Detection"
)


if anomaly_df.empty:

    st.success(
        "✅ No significant anomalies detected."
    )

else:

    critical_count = (
        anomaly_df[
            "Severity"
        ]
        .eq("CRITICAL")
        .sum()
    )

    high_count = (
        anomaly_df[
            "Severity"
        ]
        .eq("HIGH")
        .sum()
    )

    medium_count = (
        anomaly_df[
            "Severity"
        ]
        .eq("MEDIUM")
        .sum()
    )


    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "Total Anomalies",
            len(anomaly_df)
        )


    with c2:

        st.metric(
            "Critical",
            critical_count
        )


    with c3:

        st.metric(
            "High",
            high_count
        )


    with c4:

        st.metric(
            "Medium",
            medium_count
        )


    display_df = (
        anomaly_df
        .drop(
            columns=["Index"],
            errors="ignore"
        )
    )


    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# ANOMALY TREND
# ============================================================

if (
    not anomaly_df.empty
    and date_column is not None
):

    st.subheader(
        "📈 Anomaly Trend"
    )

    trend_chart = (
        create_anomaly_trend_chart(
            anomaly_df
        )
    )

    if trend_chart is not None:

        st.plotly_chart(
            trend_chart,
            use_container_width=True
        )

    else:

        st.info(
            "Not enough date information "
            "to create the anomaly trend."
        )


# ============================================================
# BUSINESS RISK SCORE
# ============================================================

st.subheader(
    "🎯 Overall Business Risk"
)


risk_result = calculate_risk_score(
    anomaly_df
)


risk_score = risk_result[
    "score"
]

risk_level = risk_result[
    "level"
]


# ============================================================
# RISK GAUGE
# ============================================================

gauge_color = "green"

if risk_score >= 70:

    gauge_color = "red"

elif risk_score >= 40:

    gauge_color = "orange"

elif risk_score >= 15:

    gauge_color = "yellow"


fig_gauge = go.Figure(
    go.Indicator(
        mode="gauge+number",
        value=risk_score,
        title={
            "text": f"Business Risk: {risk_level}"
        },
        gauge={
            "axis": {
                "range": [0, 100]
            },
            "bar": {
                "color": gauge_color
            },
            "steps": [
                {
                    "range": [0, 15],
                    "color": "lightgray"
                },
                {
                    "range": [15, 40],
                    "color": "lightyellow"
                },
                {
                    "range": [40, 70],
                    "color": "moccasin"
                },
                {
                    "range": [70, 100],
                    "color": "mistyrose"
                }
            ]
        }
    )
)


fig_gauge.update_layout(
    height=350
)


st.plotly_chart(
    fig_gauge,
    use_container_width=True
)


# ============================================================
# RISK STATUS
# ============================================================

if risk_level == "CRITICAL":

    st.error(
        f"🔴 CRITICAL BUSINESS RISK — "
        f"{risk_score}/100"
    )

elif risk_level == "HIGH":

    st.warning(
        f"🟠 HIGH BUSINESS RISK — "
        f"{risk_score}/100"
    )

elif risk_level == "MEDIUM":

    st.info(
        f"🟡 MEDIUM BUSINESS RISK — "
        f"{risk_score}/100"
    )

else:

    st.success(
        f"🟢 LOW BUSINESS RISK — "
        f"{risk_score}/100"
    )


r1, r2, r3, r4, r5 = st.columns(5)


with r1:

    st.metric(
        "Risk Score",
        f"{risk_score}/100"
    )


with r2:

    st.metric(
        "Risk Level",
        risk_level
    )


with r3:

    st.metric(
        "Critical",
        risk_result[
            "critical"
        ]
    )


with r4:

    st.metric(
        "High",
        risk_result[
            "high"
        ]
    )


with r5:

    st.metric(
        "Medium",
        risk_result[
            "medium"
        ]
    )


# ============================================================
# DETECTION METHOD
# ============================================================

if not anomaly_df.empty:

    st.subheader(
        "🔬 Detection Method"
    )

    method_counts = (
        anomaly_df[
            "Detection Method"
        ]
        .value_counts()
        .reset_index()
    )

    method_counts.columns = [
        "Detection Method",
        "Anomalies"
    ]

    fig_method = px.bar(
        method_counts,
        x="Detection Method",
        y="Anomalies",
        title="How Anomalies Were Detected"
    )

    st.plotly_chart(
        fig_method,
        use_container_width=True
    )


# ============================================================
# MOST IMPORTANT ANOMALY
# ============================================================

st.subheader(
    "🚨 Most Important Anomaly"
)


if not anomaly_df.empty:

    severity_order = {
        "CRITICAL": 1,
        "HIGH": 2,
        "MEDIUM": 3
    }


    important_anomalies = (
        anomaly_df.copy()
    )


    important_anomalies[
        "Severity Rank"
    ] = (
        important_anomalies[
            "Severity"
        ]
        .map(severity_order)
    )


    important_anomalies = (
        important_anomalies
        .sort_values(
            [
                "Severity Rank",
                "Deviation (%)"
            ],
            ascending=[
                True,
                False
            ]
        )
    )


    top_anomaly = (
        important_anomalies
        .iloc[0]
    )


    if top_anomaly[
        "Severity"
    ] == "CRITICAL":

        st.error(
            "🔴 CRITICAL ANOMALY DETECTED"
        )

    elif top_anomaly[
        "Severity"
    ] == "HIGH":

        st.warning(
            "🟠 HIGH-SEVERITY ANOMALY DETECTED"
        )

    else:

        st.info(
            "🟡 MEDIUM-SEVERITY ANOMALY DETECTED"
        )


    c1, c2, c3, c4, c5 = st.columns(5)


    with c1:

        st.metric(
            "Metric",
            top_anomaly[
                "Metric"
            ]
        )


    with c2:

        st.metric(
            "Current",
            f"{top_anomaly['Current Value']:,.2f}"
        )


    with c3:

        st.metric(
            "Baseline",
            f"{top_anomaly['Historical Baseline']:,.2f}"
        )


    with c4:

        st.metric(
            "Deviation",
            f"{top_anomaly['Deviation (%)']:.2f}%"
        )


    with c5:

        st.metric(
            "Z-Score",
            str(
                top_anomaly[
                    "Z-Score"
                ]
            )
        )


# ============================================================
# METRIC ANALYSIS
# ============================================================

st.subheader(
    "📊 Metric Analysis"
)


for metric in selected_metrics:

    if date_column:

        fig = px.line(
            analysis_df,
            x=date_column,
            y=metric,
            markers=True,
            title=f"{metric} Trend"
        )

    else:

        chart_df = (
            analysis_df
            .reset_index()
        )

        fig = px.line(
            chart_df,
            x="index",
            y=metric,
            markers=True,
            title=f"{metric} Trend"
        )


    fig.update_layout(
        height=400
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# AI BUSINESS ANALYSIS
# ============================================================

st.subheader(
    "🤖 AI Business Analysis"
)


if anomaly_df.empty:

    st.info(
        "No anomalies are available for AI analysis."
    )

else:

    st.write(
        "Gemini will analyze the detected anomalies "
        "and provide business recommendations."
    )


    if st.button(
        "🧠 Generate AI Business Report",
        type="primary"
    ):

        with st.spinner(
            "🤖 Gemini is analyzing your anomalies..."
        ):

            result = generate_ai_report(
                anomaly_df
                .drop(
                    columns=["Index"],
                    errors="ignore"
                ),
                selected_metrics
            )


        if result["success"]:

            st.success(
                "✅ AI business report generated."
            )


            st.markdown(
                result["report"]
            )


            st.session_state[
                "ai_report"
            ] = result[
                "report"
            ]

        else:

            st.error(
                result["report"]
            )


# ============================================================
# DOWNLOAD AI REPORT
# ============================================================

if "ai_report" in st.session_state:

    st.subheader(
        "📥 Download AI Report"
    )


    st.download_button(
        label="⬇️ Download AI Business Report",
        data=st.session_state[
            "ai_report"
        ],
        file_name=(
            "AI_Business_Anomaly_Report.txt"
        ),
        mime="text/plain"
    )


# ============================================================
# DOWNLOAD ANOMALY REPORT
# ============================================================

if not anomaly_df.empty:

    st.subheader(
        "📥 Download Anomaly Report"
    )


    anomaly_csv = (
        anomaly_df
        .drop(
            columns=["Index"],
            errors="ignore"
        )
        .to_csv(
            index=False
        )
    )


    st.download_button(
        label="⬇️ Download Anomaly CSV",
        data=anomaly_csv,
        file_name=(
            "dynamic_anomaly_report.csv"
        ),
        mime="text/csv"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🤖 AI Business Anomaly Agent | "
    "Dynamic CSV/Excel Analytics + "
    "Statistical Anomaly Detection + "
    "Gemini AI + Business Risk Assessment"
)