# RetailPulse — Sales & Inventory Intelligence

## Project Overview

RetailPulse is a retail sales and inventory analysis project developed using Python, MySQL, Pandas, Matplotlib, and Streamlit. It helps analyze sales performance, monitor inventory, and present important business metrics through reports and an interactive dashboard.

## Objectives

- Analyze total sales revenue and units sold.
- Compare product performance.
- Track daily sales trends.
- Analyze revenue by payment method.
- Monitor stock levels and reorder requirements.
- Export analytical reports as CSV files.

## Technologies Used

- **Python:** Application logic and analysis.
- **MySQL:** Relational database and SQL queries.
- **Pandas:** Data processing and CSV reports.
- **Matplotlib:** Data visualization.
- **Streamlit:** Interactive dashboard.

## Database Structure

The project uses three main tables:

1. `products` — product names, categories, prices, and stock.
2. `sales` — transaction dates and payment methods.
3. `sale_items` — products, quantities, and transaction prices.

## Key Features

- Interactive sales dashboard with filters.
- Revenue and units-sold charts.
- Payment method analysis.
- Inventory and reorder monitoring.
- Five automated CSV reports.
- Automated data validation and an audit report.

## Sample Results

The current synthetic dataset produces the following results:

| Metric | Result |
|---|---:|
| Total Revenue | ₹630 |
| Units Sold | 7 |
| Total Orders | 3 |
| Average Order Value | ₹210 |

These figures describe the project's sample data, not real-world business performance.

## Generated Reports

The `reports` folder contains:

- `product_performance.csv`
- `daily_sales_trends.csv`
- `payment_analysis.csv`
- `overall_sales_summary.csv`
- `inventory_reorder_analysis.csv`
- `retailpulse_audit.txt`

## How to Run

1. Install Python and MySQL.
2. Create and populate the `retailpulse` database.
3. Install the required Python libraries.
4. Configure the local database connection in the Python scripts.
5. Run the SQL analysis script:

   `python sql_analysis.py`

6. Launch the dashboard:

   `streamlit run app.py`

## Learning Outcomes

This project demonstrates SQL joins and aggregation, Python database connectivity, data cleaning and analysis, visualization, CSV export, dashboard development, and automated validation.

## Data and Security

This project uses synthetic sample data. Database passwords should be kept private and excluded from public repositories.

## Conclusion

RetailPulse demonstrates how Python, SQL, and data visualization can be combined to build a small retail analytics solution. It provides a foundation for further development in data analysis and business intelligence.
