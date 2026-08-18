import pandas as pd
import plotly.express as px


# ============================================================
# CREATE ANOMALY TREND DATA
# ============================================================

def prepare_anomaly_trends(
    anomaly_df,
    date_column="Date"
):

    if anomaly_df is None or anomaly_df.empty:

        return pd.DataFrame()


    data = anomaly_df.copy()


    if date_column not in data.columns:

        return pd.DataFrame()


    data[date_column] = pd.to_datetime(
        data[date_column],
        errors="coerce"
    )


    data = data.dropna(
        subset=[date_column]
    )


    if data.empty:

        return pd.DataFrame()


    # --------------------------------------------------------
    # Create daily anomaly counts
    # --------------------------------------------------------

    data["Period"] = (
        data[date_column]
        .dt.to_period("D")
        .astype(str)
    )


    trend = (
        data
        .groupby(
            "Period"
        )
        .size()
        .reset_index(
            name="Anomalies"
        )
    )


    trend["Period"] = pd.to_datetime(
        trend["Period"]
    )


    return trend


# ============================================================
# CREATE TREND CHART
# ============================================================

def create_anomaly_trend_chart(
    anomaly_df
):

    trend = prepare_anomaly_trends(
        anomaly_df
    )


    if trend.empty:

        return None


    fig = px.line(
        trend,
        x="Period",
        y="Anomalies",
        markers=True,
        title="Anomaly Frequency Over Time"
    )


    fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Number of Anomalies"
    )


    return fig


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("📈 ANOMALY TREND TEST")
    print("=" * 60)


    test_data = pd.DataFrame(
        {
            "Date": [
                "2026-01-01",
                "2026-01-01",
                "2026-01-02",
                "2026-01-03",
                "2026-01-03",
                "2026-01-03"
            ],

            "Metric": [
                "Sales",
                "Profit",
                "Sales",
                "Sales",
                "Profit",
                "Revenue"
            ],

            "Severity": [
                "HIGH",
                "CRITICAL",
                "MEDIUM",
                "HIGH",
                "CRITICAL",
                "MEDIUM"
            ]
        }
    )


    trend = prepare_anomaly_trends(
        test_data
    )


    print()

    print(
        trend.to_string(
            index=False
        )
    )


    print()
    print(
        "✅ Anomaly trend test completed."
    )