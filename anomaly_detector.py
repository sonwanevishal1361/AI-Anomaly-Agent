import pandas as pd
import numpy as np


# ============================================================
# CALCULATE Z-SCORE
# ============================================================

def calculate_z_score(series, window=7):

    rolling_mean = (
        series
        .shift(1)
        .rolling(
            window=window,
            min_periods=3
        )
        .mean()
    )

    rolling_std = (
        series
        .shift(1)
        .rolling(
            window=window,
            min_periods=3
        )
        .std()
    )

    safe_std = rolling_std.replace(
        0,
        np.nan
    )

    z_score = (
        (series - rolling_mean)
        / safe_std
    )

    return z_score


# ============================================================
# DETECT ANOMALIES
# ============================================================

def detect_anomalies(
    df,
    selected_metrics,
    date_column=None,
    lookback_period=7,
    threshold=20,
    z_threshold=2.5
):

    analysis_df = df.copy()

    anomaly_records = []


    # ========================================================
    # ANALYZE EACH METRIC
    # ========================================================

    for metric in selected_metrics:

        series = pd.to_numeric(
            analysis_df[metric],
            errors="coerce"
        )

        analysis_df[metric] = series


        # ----------------------------------------------------
        # Historical baseline
        # ----------------------------------------------------

        baseline = (
            series
            .shift(1)
            .rolling(
                window=lookback_period,
                min_periods=3
            )
            .mean()
        )


        # ----------------------------------------------------
        # Percentage deviation
        # ----------------------------------------------------

        safe_baseline = (
            baseline
            .abs()
            .replace(
                0,
                np.nan
            )
        )


        deviation = (
            (series - baseline)
            / safe_baseline
        ) * 100


        # ----------------------------------------------------
        # Z-score
        # ----------------------------------------------------

        z_score = calculate_z_score(
            series,
            window=lookback_period
        )


        # ----------------------------------------------------
        # Analyze every row
        # ----------------------------------------------------

        for index in analysis_df.index:

            current_value = series.loc[
                index
            ]

            baseline_value = baseline.loc[
                index
            ]

            deviation_value = deviation.loc[
                index
            ]

            z_value = z_score.loc[
                index
            ]


            # Skip incomplete records

            if pd.isna(
                current_value
            ):

                continue


            if pd.isna(
                baseline_value
            ):

                continue


            if pd.isna(
                deviation_value
            ):

                continue


            absolute_deviation = abs(
                float(
                    deviation_value
                )
            )


            absolute_z_score = 0

            if not pd.isna(
                z_value
            ):

                absolute_z_score = abs(
                    float(
                        z_value
                    )
                )


            # ------------------------------------------------
            # ANOMALY CONDITIONS
            # ------------------------------------------------

            percentage_anomaly = (
                absolute_deviation >= threshold
            )

            statistical_anomaly = (
                absolute_z_score >= z_threshold
            )


            # Anomaly if either method detects it

            if not (
                percentage_anomaly
                or
                statistical_anomaly
            ):

                continue


            # ------------------------------------------------
            # SEVERITY
            # ------------------------------------------------

            if (
                absolute_deviation >= threshold * 3
                or
                absolute_z_score >= z_threshold * 1.5
            ):

                severity = "CRITICAL"

            elif (
                absolute_deviation >= threshold * 2
                or
                absolute_z_score >= z_threshold
            ):

                severity = "HIGH"

            else:

                severity = "MEDIUM"


            # ------------------------------------------------
            # DETECTION METHOD
            # ------------------------------------------------

            detection_methods = []


            if percentage_anomaly:

                detection_methods.append(
                    "Percentage Change"
                )


            if statistical_anomaly:

                detection_methods.append(
                    "Z-Score"
                )


            detection_method = (
                " + ".join(
                    detection_methods
                )
            )


            # ------------------------------------------------
            # DATE
            # ------------------------------------------------

            if date_column:

                record_date = (
                    analysis_df
                    .loc[
                        index,
                        date_column
                    ]
                )

            else:

                record_date = index


            # ------------------------------------------------
            # STORE RESULT
            # ------------------------------------------------

            anomaly_records.append(
                {
                    "Index": index,

                    "Date": record_date,

                    "Metric": metric,

                    "Current Value": round(
                        float(
                            current_value
                        ),
                        2
                    ),

                    "Historical Baseline": round(
                        float(
                            baseline_value
                        ),
                        2
                    ),

                    "Deviation (%)": round(
                        float(
                            deviation_value
                        ),
                        2
                    ),

                    "Z-Score": round(
                        float(
                            z_value
                        ),
                        2
                    ) if not pd.isna(
                        z_value
                    ) else None,

                    "Detection Method":
                    detection_method,

                    "Severity":
                    severity
                }
            )


    # ========================================================
    # CREATE RESULT DATAFRAME
    # ========================================================

    anomaly_df = pd.DataFrame(
        anomaly_records
    )


    return (
        analysis_df,
        anomaly_df
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("🚨 ANOMALY DETECTOR TEST")
    print("=" * 60)


    test_df = pd.DataFrame(
        {
            "Date": pd.date_range(
                "2026-01-01",
                periods=15
            ),

            "Revenue": [
                100,
                102,
                101,
                103,
                99,
                102,
                101,
                104,
                100,
                103,
                102,
                101,
                105,
                500,
                102
            ]
        }
    )


    analysis_df, anomalies = (
        detect_anomalies(
            test_df,
            ["Revenue"],
            date_column="Date",
            lookback_period=7,
            threshold=20,
            z_threshold=2.5
        )
    )


    print()

    if anomalies.empty:

        print(
            "✅ No anomalies detected."
        )

    else:

        print(
            anomalies.to_string(
                index=False
            )
        )


    print()
    print(
        "✅ Anomaly detector test completed."
    )