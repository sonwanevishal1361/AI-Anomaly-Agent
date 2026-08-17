import pandas as pd

# ==========================================
# 1. LOAD DATA
# ==========================================

file_path = "data/business_data.csv"

df = pd.read_csv(file_path)

df["Date"] = pd.to_datetime(df["Date"])

df = df.sort_values("Date")


# ==========================================
# 2. CALCULATE BASELINE
# ==========================================

df["Revenue_Baseline"] = (
    df["Revenue"]
    .rolling(window=7)
    .mean()
    .shift(1)
)

df["Orders_Baseline"] = (
    df["Orders"]
    .rolling(window=7)
    .mean()
    .shift(1)
)

df["Traffic_Baseline"] = (
    df["Traffic"]
    .rolling(window=7)
    .mean()
    .shift(1)
)

df["Conversion_Baseline"] = (
    df["Conversion_Rate"]
    .rolling(window=7)
    .mean()
    .shift(1)
)

df["Refunds_Baseline"] = (
    df["Refunds"]
    .rolling(window=7)
    .mean()
    .shift(1)
)


# ==========================================
# 3. CALCULATE % CHANGES
# ==========================================

df["Revenue_Change_%"] = (
    (df["Revenue"] - df["Revenue_Baseline"])
    / df["Revenue_Baseline"]
) * 100

df["Orders_Change_%"] = (
    (df["Orders"] - df["Orders_Baseline"])
    / df["Orders_Baseline"]
) * 100

df["Traffic_Change_%"] = (
    (df["Traffic"] - df["Traffic_Baseline"])
    / df["Traffic_Baseline"]
) * 100

df["Conversion_Change_%"] = (
    (df["Conversion_Rate"] - df["Conversion_Baseline"])
    / df["Conversion_Baseline"]
) * 100

df["Refunds_Change_%"] = (
    (df["Refunds"] - df["Refunds_Baseline"])
    / df["Refunds_Baseline"]
) * 100


# ==========================================
# 4. DETECT ANOMALIES
# ==========================================

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


# ==========================================
# 5. FIND ANOMALIES
# ==========================================

anomalies = df[
    (df["Revenue_Anomaly"]) |
    (df["Orders_Anomaly"]) |
    (df["Traffic_Anomaly"]) |
    (df["Conversion_Anomaly"]) |
    (df["Refunds_Anomaly"])
]


# ==========================================
# 6. BUSINESS EXPLANATION
# ==========================================

print("\n========== BUSINESS ANOMALY REPORT ==========\n")

if len(anomalies) == 0:

    print("✅ No major anomalies detected.")

else:

    for _, row in anomalies.iterrows():

        print("⚠️ ANOMALY DETECTED")
        print("--------------------------------")

        print(
            "Date:",
            row["Date"].date()
        )

        print(
            "Revenue:",
            f"₹{row['Revenue']:,.0f}"
        )

        print(
            "Revenue Change:",
            f"{row['Revenue_Change_%']:.2f}%"
        )

        print(
            "Orders:",
            row["Orders"]
        )

        print(
            "Orders Change:",
            f"{row['Orders_Change_%']:.2f}%"
        )

        print(
            "Traffic Change:",
            f"{row['Traffic_Change_%']:.2f}%"
        )

        print(
            "Conversion Rate:",
            f"{row['Conversion_Rate']:.2f}%"
        )

        print(
            "Conversion Change:",
            f"{row['Conversion_Change_%']:.2f}%"
        )

        print(
            "Refunds:",
            row["Refunds"]
        )

        print(
            "Refund Change:",
            f"{row['Refunds_Change_%']:.2f}%"
        )


        # --------------------------------------
        # Generate business explanation
        # --------------------------------------

        explanation = []

        # Revenue
        if row["Revenue_Change_%"] < -20:

            explanation.append(
                f"Revenue decreased sharply by "
                f"{abs(row['Revenue_Change_%']):.1f}%."
            )

        elif row["Revenue_Change_%"] > 20:

            explanation.append(
                f"Revenue increased sharply by "
                f"{row['Revenue_Change_%']:.1f}%."
            )


        # Orders
        if row["Orders_Change_%"] < -20:

            explanation.append(
                f"Orders decreased by "
                f"{abs(row['Orders_Change_%']):.1f}%."
            )

        elif row["Orders_Change_%"] > 20:

            explanation.append(
                f"Orders increased by "
                f"{row['Orders_Change_%']:.1f}%."
            )


        # Traffic
        if abs(row["Traffic_Change_%"]) <= 20:

            explanation.append(
                "Traffic remained relatively stable."
            )

        elif row["Traffic_Change_%"] < -20:

            explanation.append(
                f"Traffic also decreased by "
                f"{abs(row['Traffic_Change_%']):.1f}%."
            )

        else:

            explanation.append(
                f"Traffic increased by "
                f"{row['Traffic_Change_%']:.1f}%."
            )


        # Conversion
        if row["Conversion_Change_%"] < -20:

            explanation.append(
                f"Conversion rate dropped significantly "
                f"by {abs(row['Conversion_Change_%']):.1f}%."
            )


        # Refunds
        if row["Refunds_Change_%"] > 20:

            explanation.append(
                f"Refunds increased by "
                f"{row['Refunds_Change_%']:.1f}%."
            )


        # --------------------------------------
        # Print final explanation
        # --------------------------------------

        print("\n🧠 BUSINESS EXPLANATION:")

        for sentence in explanation:

            print("•", sentence)


        # --------------------------------------
        # Business impact
        # --------------------------------------

        print("\n💼 POSSIBLE BUSINESS IMPACT:")

        if (
            row["Revenue_Change_%"] < -20
            and row["Conversion_Change_%"] < -20
        ):

            print(
                "The decline may indicate a conversion "
                "or customer purchasing issue."
            )

        elif row["Traffic_Change_%"] < -20:

            print(
                "The decline may be related to reduced "
                "customer traffic."
            )

        elif row["Refunds_Change_%"] > 20:

            print(
                "Higher refunds may be negatively affecting "
                "revenue and customer satisfaction."
            )

        else:

            print(
                "The anomaly should be investigated to "
                "identify the underlying business cause."
            )

        print("\n============================================\n")


# ==========================================
# 7. SAVE RESULTS
# ==========================================

output_file = "outputs/anomaly_results.csv"

df.to_csv(output_file, index=False)

print("Results saved to:")
print(output_file)