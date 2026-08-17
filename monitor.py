import os
import pandas as pd

from dotenv import load_dotenv
from google import genai
import resend


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")


# ============================================================
# FILE PATHS
# ============================================================

DATA_FILE = "data/business_data.csv"

OUTPUT_FOLDER = "outputs"

ALERT_LOG_FILE = (
    "outputs/alert_history.csv"
)


# ============================================================
# CREATE OUTPUT FOLDER
# ============================================================

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# ============================================================
# CHECK API KEYS
# ============================================================

if not GEMINI_API_KEY:

    print(
        "ERROR: GEMINI_API_KEY not found."
    )

    exit()


if not RESEND_API_KEY:

    print(
        "ERROR: RESEND_API_KEY not found."
    )

    exit()


if not ALERT_EMAIL:

    print(
        "ERROR: ALERT_EMAIL not found."
    )

    exit()


# ============================================================
# INITIALIZE GEMINI
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# INITIALIZE RESEND
# ============================================================

resend.api_key = RESEND_API_KEY


# ============================================================
# LOAD DATA
# ============================================================

print()
print("=" * 60)
print("🤖 AI BUSINESS ANOMALY MONITOR")
print("=" * 60)

print()
print("📂 Loading business data...")


try:

    df = pd.read_csv(
        DATA_FILE
    )

except Exception as e:

    print(
        "ERROR: Could not load business data."
    )

    print(e)

    exit()


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "Date",
    "Revenue",
    "Orders",
    "Traffic",
    "Conversion_Rate",
    "Cost",
    "Refunds"
]


missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    print()
    print(
        "ERROR: Missing columns:"
    )

    print(
        missing_columns
    )

    exit()


# ============================================================
# CLEAN DATA
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
    subset=required_columns
)

df = df.sort_values(
    "Date"
).reset_index(drop=True)


# ============================================================
# CALCULATE BASELINES
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
# CALCULATE CHANGES
# ============================================================

df["Revenue_Change_%"] = (
    (
        df["Revenue"]
        - df["Revenue_Baseline"]
    )
    / df["Revenue_Baseline"]
) * 100


df["Orders_Change_%"] = (
    (
        df["Orders"]
        - df["Orders_Baseline"]
    )
    / df["Orders_Baseline"]
) * 100


df["Traffic_Change_%"] = (
    (
        df["Traffic"]
        - df["Traffic_Baseline"]
    )
    / df["Traffic_Baseline"]
) * 100


df["Conversion_Change_%"] = (
    (
        df["Conversion_Rate"]
        - df["Conversion_Baseline"]
    )
    / df["Conversion_Baseline"]
) * 100


df["Refunds_Change_%"] = (
    (
        df["Refunds"]
        - df["Refunds_Baseline"]
    )
    / df["Refunds_Baseline"]
) * 100


# ============================================================
# DETECT ANOMALIES
# ============================================================

df["Revenue_Anomaly"] = (
    df["Revenue_Change_%"].abs() > 20
)


df["Orders_Anomaly"] = (
    df["Orders_Change_%"].abs() > 20
)


df["Traffic_Anomaly"] = (
    df["Traffic_Change_%"].abs() > 20
)


df["Conversion_Anomaly"] = (
    df["Conversion_Change_%"].abs() > 20
)


df["Refunds_Anomaly"] = (
    df["Refunds_Change_%"].abs() > 20
)


df["Anomaly"] = (
    df["Revenue_Anomaly"]
    |
    df["Orders_Anomaly"]
    |
    df["Traffic_Anomaly"]
    |
    df["Conversion_Anomaly"]
    |
    df["Refunds_Anomaly"]
)


# ============================================================
# SEVERITY FUNCTION
# ============================================================

def calculate_severity(row):

    changes = [

        abs(
            row["Revenue_Change_%"]
        ),

        abs(
            row["Orders_Change_%"]
        ),

        abs(
            row["Traffic_Change_%"]
        ),

        abs(
            row["Conversion_Change_%"]
        ),

        abs(
            row["Refunds_Change_%"]
        )

    ]


    maximum_change = max(
        changes
    )


    anomaly_metrics = sum(
        change > 20
        for change in changes
    )


    if (
        maximum_change >= 40
        or anomaly_metrics >= 3
    ):

        return "CRITICAL"


    elif (
        maximum_change >= 20
        or anomaly_metrics >= 2
    ):

        return "MEDIUM"


    else:

        return "LOW"


# ============================================================
# APPLY SEVERITY
# ============================================================

df["Severity"] = df.apply(
    calculate_severity,
    axis=1
)


# ============================================================
# GET LATEST RECORD
# ============================================================

latest = df.iloc[-1]


latest_date = (
    latest["Date"].strftime(
        "%Y-%m-%d"
    )
)


latest_anomaly = bool(
    latest["Anomaly"]
)


print()
print(
    f"📅 Latest Date: {latest_date}"
)


# ============================================================
# SHOW CURRENT DATA
# ============================================================

print()
print("📊 Latest Business Metrics")
print("-" * 40)

print(
    f"Revenue: ₹{latest['Revenue']:,.0f}"
)

print(
    f"Orders: {latest['Orders']:,.0f}"
)

print(
    f"Traffic: {latest['Traffic']:,.0f}"
)

print(
    f"Conversion Rate: "
    f"{latest['Conversion_Rate']:.2f}%"
)

print(
    f"Refunds: {latest['Refunds']:,.0f}"
)


# ============================================================
# NO ANOMALY
# ============================================================

if not latest_anomaly:

    print()
    print("=" * 60)
    print("🟢 SYSTEM NORMAL")
    print("=" * 60)
    print(
        "No anomaly detected."
    )

    exit()


# ============================================================
# ANOMALY DETECTED
# ============================================================

severity = latest["Severity"]


print()
print("=" * 60)
print(
    f"🚨 {severity} ANOMALY DETECTED"
)
print("=" * 60)


print()
print(
    f"Revenue Change: "
    f"{latest['Revenue_Change_%']:.2f}%"
)


print(
    f"Orders Change: "
    f"{latest['Orders_Change_%']:.2f}%"
)


print(
    f"Traffic Change: "
    f"{latest['Traffic_Change_%']:.2f}%"
)


print(
    f"Conversion Change: "
    f"{latest['Conversion_Change_%']:.2f}%"
)


print(
    f"Refund Change: "
    f"{latest['Refunds_Change_%']:.2f}%"
)


# ============================================================
# LOAD ALERT HISTORY
# ============================================================

if os.path.exists(
    ALERT_LOG_FILE
):

    try:

        alert_history = pd.read_csv(
            ALERT_LOG_FILE
        )

    except Exception:

        alert_history = pd.DataFrame()

else:

    alert_history = pd.DataFrame()


# ============================================================
# CHECK DUPLICATE ALERT
# ============================================================

already_sent = False


if not alert_history.empty:

    matching_alert = alert_history[
        (
            alert_history["Date"]
            == latest_date
        )
        &
        (
            alert_history["Severity"]
            == severity
        )
    ]


    if len(
        matching_alert
    ) > 0:

        already_sent = True


# ============================================================
# DUPLICATE ALERT
# ============================================================

if already_sent:

    print()
    print(
        "ℹ️ Alert already sent."
    )

    print(
        "No duplicate email will be sent."
    )

    exit()


# ============================================================
# GEMINI ANALYSIS
# ============================================================

print()
print(
    "🧠 Asking Gemini for business analysis..."
)


prompt = f"""
You are a senior business data analyst.

Analyze this business anomaly.

Date:
{latest_date}

Severity:
{severity}

Revenue:
₹{latest['Revenue']:,.0f}

Revenue change:
{latest['Revenue_Change_%']:.2f}%

Orders:
{latest['Orders']:,.0f}

Orders change:
{latest['Orders_Change_%']:.2f}%

Traffic:
{latest['Traffic']:,.0f}

Traffic change:
{latest['Traffic_Change_%']:.2f}%

Conversion rate:
{latest['Conversion_Rate']:.2f}%

Conversion change:
{latest['Conversion_Change_%']:.2f}%

Cost:
₹{latest['Cost']:,.0f}

Refunds:
{latest['Refunds']:,.0f}

Refund change:
{latest['Refunds_Change_%']:.2f}%

Provide:

1. What happened
2. Possible causes
3. Business impact
4. Recommended actions
5. Priority

Do not invent facts.
Possible causes should be presented as hypotheses.
Use simple professional business language.
"""


try:

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    ai_analysis = response.text

except Exception as e:

    print()
    print(
        "❌ Gemini analysis failed."
    )

    print(e)

    exit()


# ============================================================
# DISPLAY AI ANALYSIS
# ============================================================

print()
print("=" * 60)
print("🧠 GEMINI BUSINESS ANALYSIS")
print("=" * 60)

print()

print(
    ai_analysis
)


# ============================================================
# CREATE EMAIL
# ============================================================

email_body = f"""
<html>

<body>

<h2>
🚨 AI Business Anomaly Alert
</h2>

<h3>
Business Anomaly Detected
</h3>

<p>
<strong>Date:</strong>
{latest_date}
</p>

<p>
<strong>Severity:</strong>
{severity}
</p>

<hr>

<h3>
📊 Business Metrics
</h3>

<ul>

<li>
Revenue:
₹{latest['Revenue']:,.0f}
({latest['Revenue_Change_%']:.2f}%)
</li>

<li>
Orders:
{latest['Orders']:,.0f}
({latest['Orders_Change_%']:.2f}%)
</li>

<li>
Traffic:
{latest['Traffic']:,.0f}
({latest['Traffic_Change_%']:.2f}%)
</li>

<li>
Conversion Rate:
{latest['Conversion_Rate']:.2f}%
({latest['Conversion_Change_%']:.2f}%)
</li>

<li>
Refunds:
{latest['Refunds']:,.0f}
({latest['Refunds_Change_%']:.2f}%)
</li>

</ul>

<hr>

<h3>
🧠 AI Analysis
</h3>

<p>
{
    ai_analysis.replace(
        chr(10),
        "<br>"
    )
}
</p>

<hr>

<p>
🤖 AI Business Anomaly Agent
</p>

</body>

</html>
"""


# ============================================================
# SEND EMAIL
# ============================================================

print()
print(
    "📧 Sending email alert..."
)


try:

    response = resend.Emails.send(
        {
            "from":
                "onboarding@resend.dev",

            "to":
                [ALERT_EMAIL],

            "subject":
                f"🚨 {severity} "
                f"Business Anomaly Alert",

            "html":
                email_body
        }
    )


    print()
    print(
        "✅ EMAIL SENT SUCCESSFULLY!"
    )


except Exception as e:

    print()
    print(
        "❌ EMAIL SENDING FAILED."
    )

    print(e)

    exit()


# ============================================================
# SAVE ALERT HISTORY
# ============================================================

new_alert = pd.DataFrame(
    [
        {
            "Date":
                latest_date,

            "Severity":
                severity,

            "Revenue":
                latest["Revenue"],

            "Revenue_Change_%":
                latest[
                    "Revenue_Change_%"
                ],

            "Orders":
                latest["Orders"],

            "Orders_Change_%":
                latest[
                    "Orders_Change_%"
                ],

            "Email":
                ALERT_EMAIL,

            "Status":
                "Sent"
        }
    ]
)


if os.path.exists(
    ALERT_LOG_FILE
):

    existing_history = pd.read_csv(
        ALERT_LOG_FILE
    )

    updated_history = pd.concat(
        [
            existing_history,
            new_alert
        ],
        ignore_index=True
    )

else:

    updated_history = new_alert


updated_history.to_csv(
    ALERT_LOG_FILE,
    index=False
)


# ============================================================
# FINAL MESSAGE
# ============================================================

print()
print("=" * 60)
print("✅ MONITORING COMPLETED")
print("=" * 60)

print()
print(
    f"Alert saved to: {ALERT_LOG_FILE}"
)

print()