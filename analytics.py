
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

connection = None

try:
    # 1. CONNECT TO MYSQL DATABASE
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="anik",
        database="retailpulse"
    )

    print("Connected to RetailPulse database!")

    # 2. FETCH SALES DATA
    sales_query = """
        SELECT
            p.product_name,
            SUM(si.quantity) AS units_sold,
            SUM(si.quantity * si.unit_price) AS revenue
        FROM sale_items AS si
        JOIN products AS p
            ON si.product_id = p.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY revenue DESC
    """

    df = pd.read_sql(sales_query, connection)

    print("\n========== SALES ANALYSIS ==========")

    if df.empty:
        print("No sales data is available.")
    else:
        print(df.to_string(index=False))

        # 3. CALCULATE BUSINESS METRICS
        total_revenue = df["revenue"].sum()
        total_units = df["units_sold"].sum()
        total_orders_query = """
            SELECT COUNT(*) FROM sales
        """

        cursor = connection.cursor()
        cursor.execute(total_orders_query)
        total_orders = cursor.fetchone()[0]
        cursor.close()

        average_order_value = (
            total_revenue / total_orders if total_orders > 0 else 0
        )

        print("\n========== BUSINESS INSIGHTS ==========")
        print(f"Total Revenue: Rs. {total_revenue:.2f}")
        print(f"Total Units Sold: {total_units}")
        print(f"Total Orders: {total_orders}")
        print(f"Average Order Value: Rs. {average_order_value:.2f}")

        # Highest revenue product
        top_revenue_product = df.loc[df["revenue"].idxmax()]
        print(
            "Highest Revenue Product: "
            f"{top_revenue_product['product_name']} "
            f"(Rs. {top_revenue_product['revenue']:.2f})"
        )

        # Best-selling product(s), including ties
        highest_units = df["units_sold"].max()
        top_selling_products = df.loc[
            df["units_sold"] == highest_units,
            "product_name"
        ].tolist()

        print(
            "Best-Selling Product(s): "
            + ", ".join(top_selling_products)
            + f" ({highest_units} units each)"
        )

    # 4. CHECK LOW STOCK
    stock_query = """
        SELECT product_name, stock_quantity, reorder_level
        FROM products
        WHERE stock_quantity <= reorder_level
        ORDER BY stock_quantity ASC
    """

    stock_df = pd.read_sql(stock_query, connection)

    print("\n========== LOW-STOCK ALERT ==========")

    if stock_df.empty:
        print("All products have sufficient stock.")
    else:
        print("Products needing restocking:")
        print(stock_df.to_string(index=False))

    # 5. CREATE SCREENSHOTS FOLDER
    chart_folder = Path(__file__).resolve().parent / "screenshots"
    chart_folder.mkdir(exist_ok=True)

    # 6. CREATE AND SAVE BOTH CHARTS
    if not df.empty:
        # Revenue chart
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        ax1.bar(df["product_name"], df["revenue"])
        ax1.set_title("Revenue by Product")
        ax1.set_xlabel("Product")
        ax1.set_ylabel("Revenue (Rs.)")
        fig1.tight_layout()

        revenue_file = chart_folder / "revenue_by_product.png"
        fig1.savefig(revenue_file, dpi=150, bbox_inches="tight")
        print("\nRevenue chart saved:", revenue_file)

        # Units-sold chart
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.bar(df["product_name"], df["units_sold"])
        ax2.set_title("Units Sold by Product")
        ax2.set_xlabel("Product")
        ax2.set_ylabel("Units Sold")
        fig2.tight_layout()

        units_file = chart_folder / "units_sold_by_product.png"
        fig2.savefig(units_file, dpi=150, bbox_inches="tight")
        print("Units-sold chart saved:", units_file)

        # Display both charts
        plt.show()

    # 7. CLOSE DATABASE CONNECTION
    print("\nRetailPulse analytics completed successfully!")

except mysql.connector.Error as error:
    print("Database error:", error)

except Exception as error:
    print("Program error:", error)

finally:
    if connection is not None and connection.is_connected():
        connection.close()
        print("Database connection closed.")


