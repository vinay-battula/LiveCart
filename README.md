# 🛒 LiveCart — Real-Time E-Commerce Analytics

A real-time e-commerce sales and order analytics dashboard built using **Python, MySQL, SQL, and Streamlit**.

LiveCart helps analyze sales performance, order statuses, product sales, inventory levels, and customer lifetime value using sample e-commerce data.

## 📊 Dashboard Features

- Net sales and eligible order metrics
- Average order value (AOV)
- Pending order tracking
- Daily revenue analysis
- Order status distribution
- Top 5 products by sales
- Low-stock alerts
- Latest orders
- Customer lifetime value analysis
- Test order creation using the dashboard

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| MySQL | Relational database |
| SQL | Data analysis and reporting |
| Streamlit | Interactive dashboard |
| Pandas | Data processing |
| Plotly | Data visualization |
| mysql-connector-python | MySQL connectivity |
| python-dotenv | Environment variable management |

## 📁 Project Structure

```text
LiveCart/
├── app.py
├── db.py
├── seed_data.py
├── simulate_orders.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
└── sql/
    ├── schema.sql
    ├── seed.sql
    └── analytics.sql
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd LiveCart
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Update `.env` with your local MySQL connection details.

Never upload your `.env` file or database password to GitHub.

### 5. Start MySQL

Make sure your local MySQL server is running.

### 6. Create the database schema

Run:

```powershell
Get-Content .\sql\schema.sql | mysql -u root -p -h 127.0.0.1 -P 3306
```

Enter your local MySQL password when prompted.

### 7. Load sample SQL data

```powershell
Get-Content .\sql\seed.sql | mysql -u root -p -h 127.0.0.1 -P 3306 livecart
```

### 8. Generate sample orders

```powershell
python seed_data.py
```

### 9. Launch the dashboard

```powershell
streamlit run app.py
```

Open:

http://localhost:8501

## 📈 Analytics

LiveCart provides dashboard views for:

- Revenue trends
- Order status distribution
- Product sales performance
- Inventory alerts
- Customer lifetime value
- Recent order activity

Net sales exclude cancelled and refunded orders, according to the dashboard's displayed definition.

## 🧪 Testing

1. Confirm MySQL is running.
2. Confirm `.env` contains the correct local database credentials.
3. Run the SQL schema and seed scripts.
4. Run `python seed_data.py`.
5. Start the Streamlit dashboard.
6. Verify that sales metrics and charts load.
7. Create a test order and refresh the dashboard.
8. Confirm the latest orders section displays the new order.

## 🔐 Security

- Database credentials are stored in `.env`.
- `.env` is excluded from Git using `.gitignore`.
- `.env.example` provides configuration placeholders.
- Do not commit passwords, API keys, or private customer information.

## 🎯 Project Objective

To demonstrate practical skills in SQL analytics, relational database management, Python data processing, and interactive dashboard development through an e-commerce analytics application.

## 👨‍💻 Author

**Vinay Battula**

GitHub: Add your GitHub profile URL

LinkedIn: Add your LinkedIn profile URL

## 📌 Disclaimer

This project uses sample data for demonstration and educational purposes. It is not connected to a production e-commerce platform.