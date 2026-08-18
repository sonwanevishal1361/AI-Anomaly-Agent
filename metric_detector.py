import pandas as pd


# ============================================================
# METRIC DETECTOR
# ============================================================

def detect_business_metrics(df):
    """
    Automatically identifies numeric columns that are
    more likely to represent meaningful business metrics.
    """

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()


    # --------------------------------------------------------
    # Columns that usually aren't business metrics
    # --------------------------------------------------------

    excluded_keywords = [
        "id",
        "identifier",
        "code",
        "zip",
        "postal",
        "phone",
        "latitude",
        "longitude",
        "index",
        "row",
        "number"
    ]


    # --------------------------------------------------------
    # Strong business metric keywords
    # --------------------------------------------------------

    priority_keywords = [
        "sales",
        "revenue",
        "profit",
        "income",
        "expense",
        "expenses",
        "cost",
        "amount",
        "price",
        "quantity",
        "units",
        "orders",
        "order_count",
        "customers",
        "customer_count",
        "transactions",
        "transaction_count",
        "visits",
        "traffic",
        "conversion",
        "refund",
        "returns",
        "return",
        "balance",
        "payment",
        "salary",
        "wages",
        "loss",
        "margin",
        "rate"
    ]


    strong_metrics = []
    normal_metrics = []


    # --------------------------------------------------------
    # Analyze every numeric column
    # --------------------------------------------------------

    for column in numeric_columns:

        column_name = str(
            column
        ).lower().strip()


        # Remove obvious ID/code columns

        if any(
            keyword in column_name
            for keyword in excluded_keywords
        ):

            continue


        # Remove year columns

        if column_name == "year":

            continue


        # Check uniqueness

        unique_count = (
            df[column]
            .nunique(
                dropna=True
            )
        )

        row_count = max(
            len(df),
            1
        )

        unique_ratio = (
            unique_count
            / row_count
        )


        # Ignore almost constant columns

        if unique_ratio < 0.01:

            continue


        # Ignore columns with extremely high uniqueness
        # if they look like identifiers

        if unique_ratio > 0.98:

            if any(
                word in column_name
                for word in [
                    "id",
                    "code",
                    "number"
                ]
            ):

                continue


        # Check for strong business keyword

        if any(
            keyword in column_name
            for keyword in priority_keywords
        ):

            strong_metrics.append(
                column
            )

        else:

            normal_metrics.append(
                column
            )


    # --------------------------------------------------------
    # Final list
    # --------------------------------------------------------

    business_metrics = (
        strong_metrics
        + normal_metrics
    )


    return business_metrics


# ============================================================
# METRIC EXPLANATION
# ============================================================

def explain_metric(column_name):
    """
    Provides a simple explanation of why a column
    was selected as a possible business metric.
    """

    name = str(
        column_name
    ).lower()


    if any(
        word in name
        for word in [
            "sales",
            "revenue",
            "income"
        ]
    ):

        return "Financial performance metric"


    if any(
        word in name
        for word in [
            "profit",
            "margin"
        ]
    ):

        return "Profitability metric"


    if any(
        word in name
        for word in [
            "cost",
            "expense"
        ]
    ):

        return "Cost / expense metric"


    if any(
        word in name
        for word in [
            "order",
            "transaction"
        ]
    ):

        return "Transaction volume metric"


    if any(
        word in name
        for word in [
            "customer",
            "users"
        ]
    ):

        return "Customer / user metric"


    if any(
        word in name
        for word in [
            "quantity",
            "units"
        ]
    ):

        return "Volume metric"


    if any(
        word in name
        for word in [
            "refund",
            "return"
        ]
    ):

        return "Returns / refund metric"


    if "discount" in name:

        return "Pricing / discount metric"


    return "Numeric business metric"


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    test_data = pd.DataFrame(
        {
            "Row ID": [1, 2, 3, 4],
            "Customer ID": [101, 102, 103, 104],
            "Sales": [
                500,
                700,
                650,
                900
            ],
            "Profit": [
                100,
                150,
                120,
                200
            ],
            "Quantity": [
                2,
                4,
                3,
                5
            ],
            "Discount": [
                0.1,
                0.2,
                0.0,
                0.3
            ],
            "Postal Code": [
                411001,
                411002,
                411003,
                411004
            ]
        }
    )


    metrics = detect_business_metrics(
        test_data
    )


    print()
    print("=" * 60)
    print("📊 BUSINESS METRIC DETECTOR TEST")
    print("=" * 60)

    for metric in metrics:

        print(
            f"✅ {metric} "
            f"→ {explain_metric(metric)}"
        )