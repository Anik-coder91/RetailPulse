import os
from dotenv import load_dotenv
import streamlit as st
import mysql.connector
import pandas as pd


# ==========================================
# 1. DASHBOARD SETTINGS
# ==========================================

st.set_page_config(
    page_title="RetailPulse | Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 RetailPulse")
st.subheader("Sales & Inventory Intelligence")
st.write("Explore sales and inventory data from MySQL.")
st.divider()


# ==========================================
# 2. DATABASE CONNECTION
# ==========================================
# Load database settings from the private .env file
load_dotenv()
connection = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"))


connection = None

try:
    connection = get_connection()

    # ==========================================
    # 3. DATE SELECTOR
    # ==========================================

    st.header("📅 Filter Sales by Date")

    date_query = """
        SELECT
            MIN(sale_date) AS first_date,
            MAX(sale_date) AS last_date
        FROM sales
    """

    date_df = pd.read_sql(date_query, connection)

    if (
        date_df.empty
        or pd.isna(date_df.loc[0, "first_date"])
        or pd.isna(date_df.loc[0, "last_date"])
    ):
        st.warning("No sales dates are available yet.")
        st.stop()

    first_date = pd.to_datetime(
        date_df.loc[0, "first_date"]
    ).date()

    last_date = pd.to_datetime(
        date_df.loc[0, "last_date"]
    ).date()

    selected_dates = st.date_input(
        "Choose a date range:",
        value=(first_date, last_date),
        min_value=first_date,
        max_value=last_date
    )

    # Handle a date selection that is not yet a complete range
    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
    elif len(selected_dates) == 1:
        start_date = selected_dates[0]
        end_date = selected_dates[0]
    else:
        start_date = first_date
        end_date = last_date

    # ==========================================
    # 4. LOAD SALES DATA FOR THE SELECTED DATES
    # ==========================================

    product_query = """
        SELECT
            p.product_id,
            p.product_name,
            p.category,
            SUM(si.quantity) AS units_sold,
            SUM(si.quantity * si.unit_price) AS revenue
        FROM sale_items AS si
        JOIN products AS p
            ON si.product_id = p.product_id
        JOIN sales AS s
            ON si.sale_id = s.sale_id
        WHERE s.sale_date BETWEEN %s AND %s
        GROUP BY
            p.product_id,
            p.product_name,
            p.category
        ORDER BY revenue DESC
    """

    # df is defined before any code uses it
    df = pd.read_sql(
        product_query,
        connection,
        params=(start_date, end_date)
    )

    # ==========================================
    # 5. CATEGORY FILTER
    # ==========================================

    st.header("🔎 Filter Sales by Category")

    category_query = """
        SELECT DISTINCT category
        FROM products
        ORDER BY category
    """

    category_df = pd.read_sql(
        category_query,
        connection
    )

    categories = ["All Categories"] + (
        category_df["category"].dropna().tolist()
    )

    selected_category = st.selectbox(
        "Choose a product category:",
        categories
    )
       
    if selected_category == "All Categories":
        filtered_df = df.copy()
    else:
        filtered_df = df[
            df["category"] == selected_category
        ].copy()

    # ==========================================
    # 6. CALCULATE KPI VALUES
    # ==========================================

    total_revenue = float(
        filtered_df["revenue"].sum()
    )

    units_sold = int(
        filtered_df["units_sold"].sum()
    )

    if selected_category == "All Categories":
        order_query = """
            SELECT COUNT(*) AS total_orders
            FROM sales
            WHERE sale_date BETWEEN %s AND %s
        """

        order_params = (start_date, end_date)

    else:
        order_query = """
            SELECT COUNT(DISTINCT s.sale_id) AS total_orders
            FROM sales AS s
            JOIN sale_items AS si
                ON s.sale_id = si.sale_id
            JOIN products AS p
                ON si.product_id = p.product_id
            WHERE s.sale_date BETWEEN %s AND %s
              AND p.category = %s
        """

        order_params = (
            start_date,
            end_date,
            selected_category
        )

    order_df = pd.read_sql(
        order_query,
        connection,
        params=order_params
    )

    total_orders = int(
        order_df.loc[0, "total_orders"]
    )

    if total_orders > 0:
        average_order_value = (
            total_revenue / total_orders
        )
    else:
        average_order_value = 0.0

    # ==========================================
    # 7. DISPLAY KPI CARDS
    # ==========================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Revenue",
        f"₹{total_revenue:,.2f}"
    )

    col2.metric(
        "Units Sold",
        f"{units_sold:,}"
    )

    col3.metric(
        "Total Orders",
        f"{total_orders:,}"
    )

    col4.metric(
        "Average Order Value",
        f"₹{average_order_value:,.2f}"
    )

    st.divider()

    # ==========================================
    # 8. REVENUE CHART
    # ==========================================

    st.header("📈 Revenue by Product")

    if not filtered_df.empty:
        revenue_chart = filtered_df.set_index(
            "product_name"
        )[["revenue"]]

        st.bar_chart(revenue_chart)
    else:
        st.info(
            "No sales data exists for this date range "
            "and category."
        )

    # ==========================================
    # 9. UNITS SOLD CHART
    # ==========================================

    st.header("📦 Units Sold by Product")

    if not filtered_df.empty:
        units_chart = filtered_df.set_index(
            "product_name"
        )[["units_sold"]]

        st.bar_chart(units_chart)
    else:
        st.info("No product quantities are available.")

    st.divider()

        # ==========================================
    # PAYMENT METHOD ANALYSIS
    # ==========================================

    st.header("💳 Revenue by Payment Method")

    payment_query = """
        SELECT
            s.payment_method,
            SUM(si.quantity * si.unit_price) AS revenue
        FROM sales AS s
        JOIN sale_items AS si
            ON s.sale_id = si.sale_id
        WHERE s.sale_date BETWEEN %s AND %s
    """

    payment_params = [start_date, end_date]

    if selected_category != "All Categories":
        payment_query += """
            AND EXISTS (
                SELECT 1
                FROM sale_items AS si2
                JOIN products AS p
                    ON si2.product_id = p.product_id
                WHERE si2.sale_id = s.sale_id
                  AND p.category = %s
            )
        """
        payment_params.append(selected_category)

    payment_query += """
        GROUP BY s.payment_method
        ORDER BY revenue DESC
    """

    payment_df = pd.read_sql(
        payment_query,
        connection,
        params=tuple(payment_params)
    )

    if not payment_df.empty:
        payment_chart = payment_df.set_index(
            "payment_method"
        )[["revenue"]]

        st.bar_chart(payment_chart)

        st.dataframe(
            payment_df,
            use_container_width=True
        )
    else:
        st.info("No payment data exists for these filters.")

    # ==========================================
    # 10. INVENTORY ALERTS
    # ==========================================

    st.header("⚠️ Inventory Alerts")

    stock_query = """
        SELECT
            product_name,
            stock_quantity,
            reorder_level
        FROM products
        WHERE stock_quantity <= reorder_level
        ORDER BY stock_quantity ASC
    """

    stock_df = pd.read_sql(
        stock_query,
        connection
    )

    if stock_df.empty:
        st.success("All products have sufficient stock.")
    else:
        st.warning("Some products need restocking.")

        st.dataframe(
            stock_df,
            use_container_width=True
        )
        
        stock_csv = stock_df.to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            label="📥 Download Low-Stock Report",
            data=stock_csv,
            file_name="retailpulse_low_stock_report.csv",
            mime="text/csv"
        )


    # ==========================================
    # 11. PRODUCT SALES DETAILS
    # ==========================================

    st.header("📋 Product Sales Details")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )
    st.subheader("📥 Export Your Sales Data")

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="Download Filtered Sales as CSV",
        data=csv_data,
        file_name="retailpulse_sales_report.csv",
        mime="text/csv"
    )


# ==========================================
# 12. ERROR HANDLING
# ==========================================

except mysql.connector.Error as error:
    st.error("Could not connect to the RetailPulse database.")
    st.code(str(error))
    st.info(
        "Check that MySQL is running and your database "
        "credentials are correct."
    )

except Exception as error:
    st.error("Something went wrong while loading the dashboard.")
    st.code(str(error))

finally:
    if connection is not None and connection.is_connected():
        connection.close()

