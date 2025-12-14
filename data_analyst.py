from dataclasses import dataclass
from dotenv import load_dotenv
import sqlite3
from datetime import datetime, timedelta
import random

from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain.agents.structured_output import ToolStrategy
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase

load_dotenv()


# ---------------- DATABASE SETUP ----------------

def create_sample_business_database():
    """Create a sample business database with customer, subscription, and churn data."""
    conn = sqlite3.connect('business_data.db')
    cursor = conn.cursor()

    # Customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            signup_date TEXT,
            industry TEXT,
            company_size TEXT
        )
    ''')

    # Subscriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            subscription_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            plan_type TEXT,
            mrr REAL,
            start_date TEXT,
            end_date TEXT,
            status TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    ''')

    # Usage metrics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_metrics (
            metric_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            date TEXT,
            logins INTEGER,
            feature_usage INTEGER,
            support_tickets INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    ''')

    # Churn events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS churn_events (
            churn_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            churn_date TEXT,
            churn_reason TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    ''')

    # Insert sample customers
    industries = ['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing']
    company_sizes = ['Small', 'Medium', 'Large', 'Enterprise']

    customers = []
    for i in range(1, 101):
        signup_date = (datetime.now() - timedelta(days=random.randint(180, 730))).strftime('%Y-%m-%d')
        customers.append((
            i,
            f'Company {i}',
            f'contact{i}@company{i}.com',
            signup_date,
            random.choice(industries),
            random.choice(company_sizes)
        ))

    cursor.executemany('''
        INSERT OR REPLACE INTO customers (customer_id, name, email, signup_date, industry, company_size)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', customers)

    # Insert subscriptions
    plan_types = ['Basic', 'Pro', 'Enterprise']
    mrr_map = {'Basic': 99, 'Pro': 299, 'Enterprise': 999}

    subscriptions = []
    for i in range(1, 101):
        plan = random.choice(plan_types)
        customer = customers[i-1]
        signup_date = customer[3]

        # 20% churned in last month
        is_churned = i <= 20
        status = 'Cancelled' if is_churned else 'Active'
        end_date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d') if is_churned else None

        subscriptions.append((
            i, i, plan, mrr_map[plan], signup_date, end_date, status
        ))

    cursor.executemany('''
        INSERT OR REPLACE INTO subscriptions (subscription_id, customer_id, plan_type, mrr, start_date, end_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', subscriptions)

    # Insert usage metrics for last 60 days
    usage_data = []
    for customer_id in range(1, 101):
        is_churned = customer_id <= 20
        for days_ago in range(60):
            date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

            # Churned customers have declining usage
            if is_churned and days_ago < 30:
                logins = random.randint(0, 2)
                feature_usage = random.randint(0, 5)
                support_tickets = random.randint(1, 3)
            else:
                logins = random.randint(5, 20)
                feature_usage = random.randint(20, 100)
                support_tickets = random.randint(0, 1)

            usage_data.append((
                customer_id * 1000 + days_ago,
                customer_id,
                date,
                logins,
                feature_usage,
                support_tickets
            ))

    cursor.executemany('''
        INSERT OR REPLACE INTO usage_metrics (metric_id, customer_id, date, logins, feature_usage, support_tickets)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', usage_data)

    # Insert churn events
    churn_reasons = ['Price too high', 'Missing features', 'Poor support', 'Switching to competitor', 'No longer needed']
    churns = []
    for i in range(1, 21):
        churn_date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
        churns.append((
            i, i, churn_date, random.choice(churn_reasons)
        ))

    cursor.executemany('''
        INSERT OR REPLACE INTO churn_events (churn_id, customer_id, churn_date, churn_reason)
        VALUES (?, ?, ?, ?)
    ''', churns)

    conn.commit()
    conn.close()
    print("✓ Business database created with sample data")

# Create the database
create_sample_business_database()

# Connect to database
db = SQLDatabase.from_uri("sqlite:///business_data.db")


# ---------------- SYSTEM PROMPT ----------------

system_prompt = """YOU ARE A SQL DATA ANALYST who helps business stakeholders understand their data.

Your process:
1. Understand the business question
2. Write SQL to query the database
3. Analyze the results
4. Explain findings in plain English for non-technical audiences

Available tables:
- customers: customer information (customer_id, name, email, signup_date, industry, company_size)
- subscriptions: subscription details (subscription_id, customer_id, plan_type, mrr, start_date, end_date, status)
- usage_metrics: daily usage data (metric_id, customer_id, date, logins, feature_usage, support_tickets)
- churn_events: churn tracking (churn_id, customer_id, churn_date, churn_reason)

IMPORTANT:
- Always validate queries are read-only (SELECT statements only)
- Provide context and insights, not just raw numbers
- Flag any concerning trends or patterns
- Be honest if the data doesn't support a clear conclusion"""


# ---------------- MODEL ----------------

model = init_chat_model(
    "claude-sonnet-4-5-20250929",
    temperature=0
)

# ---------------- DATABASE CHAIN ----------------

chain = SQLDatabaseChain.from_llm(
    llm=model,
    db=db,
    verbose=True,
    return_intermediate_steps=True
)

# ---------------- TOOLS ----------------

@tool
def query_database(question: str) -> str:
    """Query the business database to answer analytical questions.

    Args: question: A natural language question about the business data
    Returns: Analysis results in plain English
    """
    try:
        result = chain.invoke(question)

        # Extract query and result
        query = result.get('intermediate_steps', [{}])[0].get('sql_cmd', 'N/A')
        answer = result.get('result', 'No result returned')

        # Validate it's a SELECT query
        if not query.strip().upper().startswith('SELECT'):
            return "⚠️ SAFETY CHECK FAILED: Only SELECT queries are allowed. Query was rejected."

        return f"Query executed:\n{query}\n\nAnalysis:\n{answer}"
    except Exception as e:
        return f"Error executing query: {str(e)}"


@tool
def explain_query_before_executing(question: str) -> str:
    """Explain what SQL query would be generated without executing it.
    Use this for query validation or when user wants to review first.
    
    Args: question: A natural language question about the business data
    Returns: Explanation of the query that would be executed
    """
    try:
        prompt = f"""Given this database schema:
{db.get_table_info()}

Write the SQL query to answer: {question}

Provide:
1. The SQL query
2. Explanation of what it does
3. What tables/columns it uses
4. Any potential concerns"""

        response = model.invoke(prompt)
        return f"Query Plan:\n{response.content}"
    except Exception as e:
        return f"Error explaining query: {str(e)}"


@tool
def get_database_schema() -> str:
    """Get information about available tables and their structure.
    Use this to understand what data is available."""
    return db.get_table_info()


# ---------------- RESPONSE FORMAT ----------------

@dataclass
class ResponseFormat:
    plain_english_response: str


# ---------------- AGENT ----------------

checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    tools=[query_database, explain_query_before_executing, get_database_schema],
    system_prompt=system_prompt,
    response_format=ToolStrategy(ResponseFormat),
    checkpointer=checkpointer,
)


# ---------------- INVOKE ----------------

config = {"configurable": {"thread_id": "1"}}

# Example queries to test
test_queries = [
    "How many new industries did we get into in the past year?",
]

# Run first query
response = agent.invoke(
    {"messages": [{"role": "user", "content": test_queries[0]}]},
    config=config,
)

