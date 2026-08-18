import os
import pandas as pd
from google import genai
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


# ============================================================
# GEMINI CLIENT
# ============================================================

if GEMINI_API_KEY:

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

else:

    client = None


# ============================================================
# PREPARE ANOMALY DATA
# ============================================================

def prepare_anomaly_summary(
    anomaly_df
):

    if anomaly_df is None or anomaly_df.empty:

        return "No anomalies detected."


    data = anomaly_df.copy()


    # Keep the most important columns
    preferred_columns = [
        "Date",
        "Metric",
        "Current Value",
        "Historical Baseline",
        "Deviation (%)",
        "Z-Score",
        "Severity",
        "Detection Method"
    ]


    available_columns = [
        column
        for column in preferred_columns
        if column in data.columns
    ]


    if available_columns:

        data = data[
            available_columns
        ]


    # Limit rows sent to AI
    data = data.head(100)


    return data.to_string(
        index=False
    )


# ============================================================
# GENERATE AI REPORT
# ============================================================

def generate_ai_report(
    anomaly_df,
    selected_metrics=None
):

    if client is None:

        return {
            "success": False,
            "report": (
                "❌ Gemini API key was not found.\n\n"
                "Please make sure GEMINI_API_KEY "
                "is configured in the .env file."
            )
        }


    try:

        anomaly_summary = (
            prepare_anomaly_summary(
                anomaly_df
            )
        )


        metrics_text = ", ".join(
            selected_metrics
            if selected_metrics
            else []
        )


        prompt = f"""
You are a senior Business Intelligence analyst.

Analyze the following automatically detected
business anomalies.

MONITORED METRICS:
{metrics_text}

ANOMALY DATA:
{anomaly_summary}


Create a concise but professional business
intelligence report.

Use exactly these sections:


# Executive Summary

Give a short overview of the overall situation.


# Key Findings

Identify the most important anomalies.

Mention:

- affected metric
- current value
- historical baseline
- percentage deviation
- severity


# Business Impact

Explain what these anomalies could mean
for the business.

Discuss possible impact on:

- revenue
- profitability
- customers
- operations
- pricing
- inventory

Only discuss areas that are relevant to
the detected metrics.


# Possible Causes

Give realistic possible explanations.

Clearly state that these are hypotheses
and not confirmed causes.


# Recommended Actions

Give 4 to 6 practical actions.

Prioritize the most important action first.


# Monitoring Priorities

Explain which metrics or business areas
should be monitored next.


# Risk Assessment

Give an overall risk assessment using:

LOW
MEDIUM
HIGH
CRITICAL

Explain why.


IMPORTANT RULES:

- Do not invent data.
- Do not invent business facts.
- Use only information present in the dataset.
- Clearly distinguish facts from hypotheses.
- Keep the report professional.
- Use bullet points where appropriate.
- Focus on actionable business insights.
"""


        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )


        report = response.text


        if not report:

            return {
                "success": False,
                "report": (
                    "❌ Gemini returned an empty response."
                )
            }


        return {
            "success": True,
            "report": report
        }


    except Exception as e:

        return {
            "success": False,
            "report": (
                "❌ AI report generation failed.\n\n"
                f"Error: {str(e)}"
            )
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("🤖 AI REPORT GENERATOR TEST")
    print("=" * 60)


    if client is None:

        print()
        print(
            "❌ GEMINI_API_KEY not found."
        )

    else:

        test_data = pd.DataFrame(
            {
                "Date": [
                    "2026-01-01",
                    "2026-01-02"
                ],

                "Metric": [
                    "Sales",
                    "Profit"
                ],

                "Current Value": [
                    50000,
                    8000
                ],

                "Historical Baseline": [
                    70000,
                    12000
                ],

                "Deviation (%)": [
                    -28.57,
                    -33.33
                ],

                "Z-Score": [
                    -3.2,
                    -3.8
                ],

                "Severity": [
                    "HIGH",
                    "CRITICAL"
                ],

                "Detection Method": [
                    "Percentage Change",
                    "Z-Score"
                ]
            }
        )


        result = generate_ai_report(
            test_data,
            ["Sales", "Profit"]
        )


        if result["success"]:

            print()
            print(
                result["report"]
            )

            print()
            print(
                "✅ AI report test completed."
            )

        else:

            print()
            print(
                result["report"]
            )