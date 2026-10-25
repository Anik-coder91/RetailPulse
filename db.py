
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

connection = None
cursor = None

try:
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    print("Connected to RetailPulse database!")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT product_id, product_name, category,
               unit_price, stock_quantity
        FROM products
        ORDER BY product_id
    """)

    products = cursor.fetchall()

    print("\nPRODUCT INVENTORY")
    print("-" * 65)

    for product in products:
        print(
            f"ID: {product[0]} | "
            f"Name: {product[1]} | "
            f"Category: {product[2]} | "
            f"Price: Rs.{product[3]} | "
            f"Stock: {product[4]}"
        )

    print("-" * 65)
    print("Total products:", len(products))

except mysql.connector.Error as error:
    print("Database error:", error)

finally:
    if cursor is not None:
        cursor.close()

    if connection is not None and connection.is_connected():
        connection.close()
        print("Database connection closed.")
