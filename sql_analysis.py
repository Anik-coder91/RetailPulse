

import os
from pathlib import Path

import mysql.connector
import pandas as pd
from dotenv import load_dotenv


# Project folders
BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

# Load .env from the same folder as this script
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=True)


def get_database_connection():
    """Load and validate database settings before connecting."""

    required_settings = [
        "DB_HOST",
        "DB_USER",
        "DB_PASSWORD",
        "DB_NAME",
    ]

    missing = [
        key for key in required_settings
        if os.getenv(key) is None or not os.getenv(key).strip()
    ]

    if missing:
        raise ValueError(
            "Missing database settings in .env: "
            + ", ".join(missing)
            + f"\nExpected .env location: {ENV_FILE}"
        )

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=3306,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        use_pure=True,
        connection_timeout=10,
    )


def save_report(dataframe, filename):
    """Save a report as a CSV file."""
    output_path = REPORT_DIR / filename
    dataframe.to_csv(output_path, index=False)
    print(f"Saved: {output_path.name}")
    return dataframe


def main():
    connection = None

    try:
        print("=" * 55)
        print("       RETAILPULSE SQL ANALYSIS")
        print("=" * 55)

        print("Checking .env configuration...")
        print("Environment file found:", ENV_FILE.is_file())

        connection = get_database_connection()
        print("Database connection successful!\n")

        # 1. Product performance
        product_query = """
            SELECT
                p.product_id,
                p.product_name,
                p.category,
                COALESCE(SUM(si.quantity), 0) AS units_sold,
                COALESCE(
                    SUM(si.quantity * si.unit_price), 0
                ) AS revenue
            FROM products p
            LEFT JOIN sale_items si
                ON p.product_id = si.product_id
            GROUP BY
                p.product_id, p.product_name, p.category
            ORDER BY revenue DESC
        """

        product_df = pd.read_sql(
            product_query, connection
        )
        save_report(product_df, "product_performance.csv")

        # 2. Daily sales trends
        daily_query = """
            SELECT
                s.sale_date,
                SUM(si.quantity * si.unit_price) AS revenue,
                SUM(si.quantity) AS units_sold,
                COUNT(DISTINCT s.sale_id) AS orders
            FROM sales s
            JOIN sale_items si
                ON s.sale_id = si.sale_id
            GROUP BY s.sale_date
            ORDER BY s.sale_date
        """

        daily_df = pd.read_sql(
            daily_query, connection
        )
        save_report(daily_df, "daily_sales_trends.csv")

        # 3. Payment method analysis
        payment_query = """
            SELECT
                s.payment_method,
                SUM(si.quantity * si.unit_price) AS revenue,
                COUNT(DISTINCT s.sale_id) AS orders
            FROM sales s
            JOIN sale_items si
                ON s.sale_id = si.sale_id
            GROUP BY s.payment_method
            ORDER BY revenue DESC
        """

        payment_df = pd.read_sql(
            payment_query, connection
        )
        save_report(payment_df, "payment_analysis.csv")

        # 4. Overall sales summary
        summary_query = """
            SELECT
                COALESCE(
                    SUM(si.quantity * si.unit_price), 0
                ) AS total_revenue,
                COALESCE(SUM(si.quantity), 0) AS units_sold,
                COUNT(DISTINCT s.sale_id) AS total_orders
            FROM sales s
            LEFT JOIN sale_items si
                ON s.sale_id = si.sale_id
        """

        summary_df = pd.read_sql(
            summary_query, connection
        )

        total_revenue = float(
            summary_df.loc[0, "total_revenue"]
        )
        total_units = int(summary_df.loc[0, "units_sold"])
        total_orders = int(summary_df.loc[0, "total_orders"])

        average_order_value = (
            total_revenue / total_orders
            if total_orders else 0
        )

        summary_df["average_order_value"] = round(
            average_order_value, 2
        )

        save_report(
            summary_df, "overall_sales_summary.csv"
        )

        # 5. Inventory and reorder analysis
        inventory_query = """
            SELECT
                product_id,
                product_name,
                category,
                stock_quantity,
                reorder_level,
                CASE
                    WHEN stock_quantity <= reorder_level
                    THEN 'REORDER'
                    ELSE 'OK'
                END AS stock_status
            FROM products
            ORDER BY stock_quantity ASC
        """

        inventory_df = pd.read_sql(
            inventory_query, connection
        )
        save_report(
            inventory_df, "inventory_reorder_analysis.csv"
        )

        # Display the reports
        print("\n--- PRODUCT PERFORMANCE ---")
        print(product_df.to_string(index=False))

        print("\n--- DAILY SALES TRENDS ---")
        print(daily_df.to_string(index=False))

        print("\n--- PAYMENT ANALYSIS ---")
        print(payment_df.to_string(index=False))

        print("\n--- OVERALL SALES SUMMARY ---")
        print(summary_df.to_string(index=False))

        print("\n--- INVENTORY REORDER ANALYSIS ---")
        print(inventory_df.to_string(index=False))

        # Audit and validation
        audit_lines = [
            "RETAILPULSE DATA VALIDATION AUDIT",
            "=" * 40,
            "",
        ]

        failures = []

        def check(description, condition):
            status = "PASS" if condition else "FAIL"
            audit_lines.append(f"{description}: {status}")
            print(f"{description}: {status}")

            if not condition:
                failures.append(description)

        print("\n--- VALIDATION CHECKS ---")

        check(
            "Product report has 3 products",
            len(product_df) == 3,
        )
        check(
            "Daily report has 3 dates",
            len(daily_df) == 3,
        )
        check(
            "Payment report has 3 methods",
            len(payment_df) == 3,
        )
        check(
            "Total revenue equals 630",
            abs(total_revenue - 630) < 0.01,
        )
        check(
            "Total units sold equals 7",
            total_units == 7,
        )
        check(
            "Total orders equals 3",
            total_orders == 3,
        )
        check(
            "Average order value equals 210",
            abs(average_order_value - 210) < 0.01,
        )

        usb_revenue = product_df.loc[
            product_df["product_name"] == "USB Drive",
            "revenue",
        ]

        check(
            "USB Drive revenue equals 450",
            len(usb_revenue) == 1
            and abs(float(usb_revenue.iloc[0]) - 450) < 0.01,
        )

        check(
            "Daily revenue totals match overall revenue",
            abs(
                float(daily_df["revenue"].sum())
                - total_revenue
            ) < 0.01,
        )

        check(
            "Inventory quantities are non-negative",
            (inventory_df["stock_quantity"] >= 0).all(),
        )

        check(
            "Inventory report includes stock status",
            "stock_status" in inventory_df.columns,
        )

        audit_lines.extend([
            "",
            "=" * 40,
            "FINAL STATUS: "
            + ("PASS" if not failures else "FAIL"),
        ])

        audit_path = REPORT_DIR / "retailpulse_audit.txt"
        audit_path.write_text(
            "\n".join(audit_lines) + "\n",
            encoding="utf-8",
        )

        print("\nAudit saved: retailpulse_audit.txt")
        print("\nFINAL STATUS:", "PASS" if not failures else "FAIL")

        if failures:
            print("\nChecks requiring attention:")
            for failure in failures:
                print("-", failure)

    except ValueError as error:
        print("\nCONFIGURATION ERROR:", error)

    except mysql.connector.Error as error:
        print("\nDATABASE ERROR:", error)
        print(
            "Check the local MySQL service, .env settings, "
            "username and password."
        )

    except Exception as error:
        print("\nUNEXPECTED ERROR:", error)
        print("Check the error details before continuing.")

    finally:
        if connection is not None and connection.is_connected():
            connection.close()
            print("\nDatabase connection closed.")


if __name__ == "__main__":
    main()
