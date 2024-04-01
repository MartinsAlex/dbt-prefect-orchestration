import psycopg2
from faker import Faker
import random

# Configuration
DATABASE = 'yourdatabase'
USER = 'username'
PASSWORD = 'password'
HOST = 'localhost'  # Adjust if necessary
PORT = '5432'

# Establish connection
conn = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST, port=PORT)
conn.autocommit = True
cursor = conn.cursor()

# Create tables (if they do not exist)
cursor.execute('''
CREATE TABLE IF NOT EXISTS Customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Accounts (
    account_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES Customers(customer_id),
    account_number VARCHAR(255),
    balance DECIMAL(10, 2)
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Orders (
    order_id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES Accounts(account_id),
    order_amount DECIMAL(10, 2),
    order_date TIMESTAMP
);
''')

# New Tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS Contracts (
    contract_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES Customers(customer_id),
    contract_type VARCHAR(255),
    contract_value DECIMAL(10, 2),
    start_date TIMESTAMP,
    end_date TIMESTAMP
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS PurchaseOrders (
    po_id SERIAL PRIMARY KEY,
    vendor_name VARCHAR(255),
    po_amount DECIMAL(10, 2),
    po_date TIMESTAMP
);
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Employees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    position VARCHAR(255),
    department VARCHAR(255),
    email VARCHAR(255),
    hire_date TIMESTAMP
);
''')

# Generate and insert fake data
fake = Faker()
Faker.seed(0)

# Existing Data Generation for Customers and Accounts
for _ in range(1000):  # Adjust the range for the desired number of customers
    name = fake.name()
    email = fake.email()
    cursor.execute('INSERT INTO Customers (name, email) VALUES (%s, %s) RETURNING customer_id;', (name, email))
    customer_id = cursor.fetchone()[0]

    # Assume each customer gets one account
    account_number = fake.iban()
    balance = random.uniform(1000, 50000)
    cursor.execute('INSERT INTO Accounts (customer_id, account_number, balance) VALUES (%s, %s, %s) RETURNING account_id;', (customer_id, account_number, balance))
    account_id = cursor.fetchone()[0]

    # Generate orders for the account
    for _ in range(random.randint(1, 10)):  # Random number of orders per account
        order_amount = random.uniform(20, 1000)
        order_date = fake.date_time_this_year()
        cursor.execute('INSERT INTO Orders (account_id, order_amount, order_date) VALUES (%s, %s, %s);', (account_id, order_amount, order_date))

# Contracts
for _ in range(500):
    customer_id = random.randint(1, 1000)
    contract_type = fake.random_element(elements=("Loan Agreement", "Mortgage", "Deposit Agreement"))
    contract_value = random.uniform(10000, 500000)
    start_date = fake.date_between(start_date="-5y", end_date="today")
    end_date = fake.date_between(start_date=start_date, end_date="+5y")
    cursor.execute('INSERT INTO Contracts (customer_id, contract_type, contract_value, start_date, end_date) VALUES (%s, %s, %s, %s, %s);', (customer_id, contract_type, contract_value, start_date, end_date))

# Purchase Orders
for _ in range(200):
    vendor_name = fake.company()
    po_amount = random.uniform(500, 20000)
    po_date = fake.date_time_this_year()
    cursor.execute('INSERT INTO PurchaseOrders (vendor_name, po_amount, po_date) VALUES (%s, %s, %s);', (vendor_name, po_amount, po_date))

# Employees
for _ in range(200):
    name = fake.name()
    position = fake.random_element(elements=("Manager", "Analyst", "Clerk", "Executive"))
    department = fake.random_element(elements=("HR", "IT", "Finance", "Customer Service"))
    email = fake.email()
    hire_date = fake.date_between(start_date="-10y", end_date="today")
    cursor.execute('INSERT INTO Employees (name, position, department, email, hire_date) VALUES (%s, %s, %s, %s, %s);', (name, position, department, email, hire_date))

# Close connection
cursor.close()
conn.close()

print("Fake banking data generated and inserted into the database.")
