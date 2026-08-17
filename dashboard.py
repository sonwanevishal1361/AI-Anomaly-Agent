import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv
from google import genai


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Business Anomaly Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DATA_FILE = "data/business_data.csv"
ALERT_FILE = "outputs/alert_history.csv"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .dashboard-title {
        font-size: 38px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .dashboard-subtitle {
        font-size: 16px;
        color: #777777;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .status-normal {
        padding: 18px;
        border-radius: 12px;
        background-color: #e9f7ef;
        text-align: center;
        font-size: 20px;
        font-weight: 700;
    }

    .status-danger {
        padding: 18px;
        border-radius: 12px;
        background-color: #fdecea;
        text-align: center;
        font-size: 20px;
        font-weight: 700;
    }

    .ai-box {
        padding: 22px;
        border-radius: 12px;
        background-color: #f5f5f5;
        border: 1px solid #dddddd;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">'
    '🤖 AI Business Anomaly Agent'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Automated business monitoring • anomaly detection • AI-powered insights'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

try:

    df = pd.read_csv(DATA_FILE)

except Exception as e:

    st.error(
        f"Unable to load business data: {e}"
    )

    st.stop()


# ============================================================
# DATA CLEANING
# ============================================================

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

numeric_columns = [
    "Revenue",
    "Orders",
    "Traffic",
    "Conversion_Rate",
    "Cost",
    "Refunds"
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


df = df.dropna(
    subset=[
        "Date",
        "Revenue",
        "Orders",
        "Traffic",
        "Conversion_Rate",
        "Cost",
        "Refunds"
    ]
)

df = df.sort_values(
    "Date"
).reset_index(drop=True)


# ============================================================
# BASELINES
# ============================================================

df["Revenue_Baseline"] = (
    df["Revenue"]
    .rolling(7)
    .mean()
    .shift(1)
)

df["Orders_Baseline"] = (
    df["Orders"]
    .rolling(7)
    .mean()
    .shift(1)
)

df["Traffic_Baseline"] = (
    df["Traffic"]
    .rolling(7)
    .mean()
    .shift(1)
)

df["Conversion_Baseline"] = (
    df["Conversion_Rate"]
    .rolling(7)
    .mean()
    .shift(1)
)

df["Refunds_Baseline"] = (
    df["Refunds"]
    .rolling(7)
    .mean()
    .shift(1)
)


# ============================================================
# PERCENTAGE CHANGES
# ============================================================

def calculate_change(current, baseline):

    if pd.isna(baseline) or baseline == 0:

        return 0

    return (
        (current - baseline)
        / baseline
    ) * 100


df["Revenue_Change"] = df.apply(
    lambda row: calculate_change(
        row["Revenue"],
        row["Revenue_Baseline"]
    ),
    axis=1
)

df["Orders_Change"] = df.apply(
    lambda row: calculate_change(
        row["Orders"],
        row["Orders_Baseline"]
    ),
    axis=1
)

df["Traffic_Change"] = df.apply(
    lambda row: calculate_change(
        row["Traffic"],
        row["Traffic_Baseline"]
    ),
    axis=1
)

df["Conversion_Change"] = df.apply(
    lambda row: calculate_change(
        row["Conversion_Rate"],
        row["Conversion_Baseline"]
    ),
    axis=1
)

df["Refunds_Change"] = df.apply(
    lambda row: calculate_change(
        row["Refunds"],
        row["Refunds_Baseline"]
    ),
    axis=1
)


# ============================================================
# ANOMALY DETECTION
# ============================================================

df["Anomaly"] = (
    df["Revenue_Change"].abs() > 20
) | (
    df["Orders_Change"].abs() > 20
) | (
    df["Traffic_Change"].abs() > 20
) | (
    df["Conversion_Change"].abs() > 20
) | (
    df["Refunds_Change"].abs() > 20
)


# ============================================================
# SEVERITY
# ============================================================

def get_severity(row):

    changes = [
        abs(row["Revenue_Change"]),
        abs(row["Orders_Change"]),
        abs(row["Traffic_Change"]),
        abs(row["Conversion_Change"]),
        abs(row["Refunds_Change"])
    ]

    maximum_change = max(changes)

    number_of_anomalies = sum(
        change > 20
        for change in changes
    )

    if (
        maximum_change >= 40
        or number_of_anomalies >= 3
    ):

        return "CRITICAL"

    elif (
        maximum_change >= 20
        or number_of_anomalies >= 2
    ):

        return "MEDIUM"

    elif maximum_change >= 10:

        return "LOW"

    return "NORMAL"


df["Severity"] = df.apply(
    get_severity,
    axis=1
)


# ============================================================
# LATEST DATA
# ============================================================

latest = df.iloc[-1]

latest_date = latest["Date"]


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "⚙️ Dashboard Controls"
)

st.sidebar.markdown(
    "---"
)

show_anomalies = st.sidebar.checkbox(
    "Show anomaly records only",
    value=False
)

st.sidebar.markdown(
    "---"
)

st.sidebar.write(
    f"📅 Data from: "
    f"{df['Date'].min().strftime('%d %b %Y')}"
)

st.sidebar.write(
    f"📅 Data to: "
    f"{df['Date'].max().strftime('%d %b %Y')}"
)

st.sidebar.write(
    f"📊 Total records: {len(df)}"
)

st.sidebar.write(
    f"🚨 Total anomalies: "
    f"{int(df['Anomaly'].sum())}"
)


# ============================================================
# KPI SECTION
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📊 Latest Business Performance'
    '</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "Revenue",
        f"₹{latest['Revenue']:,.0f}",
        f"{latest['Revenue_Change']:.1f}%"
    )


with col2:

    st.metric(
        "Orders",
        f"{latest['Orders']:,.0f}",
        f"{latest['Orders_Change']:.1f}%"
    )


with col3:

    st.metric(
        "Traffic",
        f"{latest['Traffic']:,.0f}",
        f"{latest['Traffic_Change']:.1f}%"
    )


with col4:

    st.metric(
        "Conversion",
        f"{latest['Conversion_Rate']:.2f}%",
        f"{latest['Conversion_Change']:.1f}%"
    )


with col5:

    st.metric(
        "Refunds",
        f"{latest['Refunds']:,.0f}",
        f"{latest['Refunds_Change']:.1f}%"
    )


# ============================================================
# SYSTEM STATUS
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🚨 Monitoring Status'
    '</div>',
    unsafe_allow_html=True
)


if latest["Anomaly"]:

    st.markdown(
        f"""
        <div class="status-danger">
        🚨 {latest["Severity"]} ANOMALY DETECTED
        <br>
        <small>
        {latest_date.strftime("%d %B %Y")}
        </small>
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        f"""
        <div class="status-normal">
        🟢 SYSTEM NORMAL
        <br>
        <small>
        {latest_date.strftime("%d %B %Y")}
        </small>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# REVENUE CHART
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📈 Revenue Monitoring'
    '</div>',
    unsafe_allow_html=True
)


fig_revenue = go.Figure()


fig_revenue.add_trace(
    go.Scatter(
        x=df["Date"],
        y=df["Revenue"],
        mode="lines+markers",
        name="Revenue"
    )
)


anomaly_rows = df[
    df["Anomaly"]
]


fig_revenue.add_trace(
    go.Scatter(
        x=anomaly_rows["Date"],
        y=anomaly_rows["Revenue"],
        mode="markers",
        name="Anomaly",
        marker={
            "size": 12,
            "symbol": "x"
        }
    )
)


fig_revenue.update_layout(
    height=420,
    hovermode="x unified",
    xaxis_title="Date",
    yaxis_title="Revenue",
    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20
    )
)


st.plotly_chart(
    fig_revenue,
    use_container_width=True
)


# ============================================================
# TWO-COLUMN SECTION
# ============================================================

left, right = st.columns(2)


# ============================================================
# METRIC CHANGE CHART
# ============================================================

with left:

    st.markdown(
        '<div class="section-title">'
        '📉 Latest Metric Changes'
        '</div>',
        unsafe_allow_html=True
    )

    metric_names = [
        "Revenue",
        "Orders",
        "Traffic",
        "Conversion",
        "Refunds"
    ]

    metric_changes = [
        latest["Revenue_Change"],
        latest["Orders_Change"],
        latest["Traffic_Change"],
        latest["Conversion_Change"],
        latest["Refunds_Change"]
    ]

    fig_change = go.Figure(
        go.Bar(
            x=metric_names,
            y=metric_changes,
            text=[
                f"{value:.1f}%"
                for value in metric_changes
            ],
            textposition="outside"
        )
    )

    fig_change.update_layout(
        height=400,
        yaxis_title="Change (%)",
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        )
    )

    st.plotly_chart(
        fig_change,
        use_container_width=True
    )


# ============================================================
# COST VS REVENUE
# ============================================================

with right:

    st.markdown(
        '<div class="section-title">'
        '💰 Revenue vs Cost'
        '</div>',
        unsafe_allow_html=True
    )

    fig_cost = go.Figure()

    fig_cost.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Revenue"],
            mode="lines+markers",
            name="Revenue"
        )
    )

    fig_cost.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["Cost"],
            mode="lines+markers",
            name="Cost"
        )
    )

    fig_cost.update_layout(
        height=400,
        yaxis_title="Amount",
        hovermode="x unified",
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        )
    )

    st.plotly_chart(
        fig_cost,
        use_container_width=True
    )


# ============================================================
# ANOMALY HISTORY
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🔎 Anomaly History'
    '</div>',
    unsafe_allow_html=True
)


if show_anomalies:

    history = df[
        df["Anomaly"]
    ].copy()

else:

    history = df.copy()


history_display = history[
    [
        "Date",
        "Revenue",
        "Revenue_Change",
        "Orders",
        "Orders_Change",
        "Conversion_Rate",
        "Refunds",
        "Severity",
        "Anomaly"
    ]
].copy()


history_display.columns = [
    "Date",
    "Revenue",
    "Revenue Change %",
    "Orders",
    "Orders Change %",
    "Conversion Rate",
    "Refunds",
    "Severity",
    "Anomaly"
]


st.dataframe(
    history_display,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DOWNLOAD REPORT
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📥 Download Report'
    '</div>',
    unsafe_allow_html=True
)


report_csv = history_display.to_csv(
    index=False
)


st.download_button(
    label="⬇️ Download Anomaly Report",
    data=report_csv,
    file_name="ai_anomaly_report.csv",
    mime="text/csv"
)


# ============================================================
# GEMINI AI ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🧠 Gemini AI Business Analysis'
    '</div>',
    unsafe_allow_html=True
)


if not GEMINI_API_KEY:

    st.warning(
        "Gemini API key was not found in the .env file."
    )

else:

    if st.button(
        "🤖 Generate AI Business Insight",
        use_container_width=True
    ):

        with st.spinner(
            "Gemini is analyzing the business data..."
        ):

            try:

                client = genai.Client(
                    api_key=GEMINI_API_KEY
                )


                prompt = f"""
You are a senior business data analyst.

Analyze this latest business performance.

Date:
{latest_date.strftime("%Y-%m-%d")}

Revenue:
₹{latest["Revenue"]:,.0f}

Revenue change:
{latest["Revenue_Change"]:.2f}%

Orders:
{latest["Orders"]:,.0f}

Orders change:
{latest["Orders_Change"]:.2f}%

Traffic:
{latest["Traffic"]:,.0f}

Traffic change:
{latest["Traffic_Change"]:.2f}%

Conversion rate:
{latest["Conversion_Rate"]:.2f}%

Conversion change:
{latest["Conversion_Change"]:.2f}%

Cost:
₹{latest["Cost"]:,.0f}

Refunds:
{latest["Refunds"]:,.0f}

Refund change:
{latest["Refunds_Change"]:.2f}%

Severity:
{latest["Severity"]}

Provide a concise business analysis with these sections:

WHAT HAPPENED
POSSIBLE CAUSES
BUSINESS IMPACT
RECOMMENDED ACTIONS

Do not invent facts.
Treat causes as possible hypotheses.
Use simple professional business language.
"""


                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=prompt
                )


                st.markdown(
                    '<div class="ai-box">',
                    unsafe_allow_html=True
                )

                st.write(
                    response.text
                )

                st.markdown(
                    '</div>',
                    unsafe_allow_html=True
                )


            except Exception as e:

                st.error(
                    f"Gemini error: {e}"
                )


# ============================================================
# EMAIL ALERT HISTORY
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📧 Email Alert Status'
    '</div>',
    unsafe_allow_html=True
)


if os.path.exists(ALERT_FILE):

    try:

        alerts = pd.read_csv(
            ALERT_FILE
        )

        st.success(
            f"Email alerts recorded: {len(alerts)}"
        )

        st.dataframe(
            alerts,
            use_container_width=True,
            hide_index=True
        )

    except Exception:

        st.info(
            "Alert history exists but could not be displayed."
        )

else:

    st.info(
        "No email alerts have been recorded yet."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "🤖 AI Business Anomaly Agent | "
    "Python • Pandas • Plotly • Streamlit • Gemini AI"
)