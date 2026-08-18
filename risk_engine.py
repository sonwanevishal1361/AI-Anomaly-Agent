import pandas as pd


# ============================================================
# CALCULATE BUSINESS RISK SCORE
# ============================================================

def calculate_risk_score(anomaly_df):

    if anomaly_df is None or anomaly_df.empty:

        return {
            "score": 0,
            "level": "LOW",
            "critical": 0,
            "high": 0,
            "medium": 0,
            "total": 0
        }


    critical = (
        anomaly_df["Severity"]
        .eq("CRITICAL")
        .sum()
    )

    high = (
        anomaly_df["Severity"]
        .eq("HIGH")
        .sum()
    )

    medium = (
        anomaly_df["Severity"]
        .eq("MEDIUM")
        .sum()
    )


    total = (
        critical
        + high
        + medium
    )


    # ========================================================
    # WEIGHTED RISK
    # ========================================================

    weighted_risk = (
        critical * 10
        + high * 5
        + medium * 2
    )


    # Normalize score

    score = min(
        100,
        weighted_risk
    )


    # ========================================================
    # RISK LEVEL
    # ========================================================

    if score >= 70:

        level = "CRITICAL"

    elif score >= 40:

        level = "HIGH"

    elif score >= 15:

        level = "MEDIUM"

    else:

        level = "LOW"


    return {
        "score": int(score),
        "level": level,
        "critical": int(critical),
        "high": int(high),
        "medium": int(medium),
        "total": int(total)
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("🎯 BUSINESS RISK ENGINE TEST")
    print("=" * 60)


    test_data = pd.DataFrame(
        {
            "Severity": [
                "CRITICAL",
                "CRITICAL",
                "HIGH",
                "HIGH",
                "MEDIUM"
            ]
        }
    )


    result = calculate_risk_score(
        test_data
    )


    print()

    print(
        f"Risk Score : {result['score']}/100"
    )

    print(
        f"Risk Level : {result['level']}"
    )

    print(
        f"Critical   : {result['critical']}"
    )

    print(
        f"High       : {result['high']}"
    )

    print(
        f"Medium     : {result['medium']}"
    )

    print(
        f"Total      : {result['total']}"
    )

    print()
    print(
        "✅ Risk engine test completed."
    )