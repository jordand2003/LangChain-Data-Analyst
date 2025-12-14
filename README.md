# LangChain Data Analyst

A SQL data analyst agent built with LangChain and Claude that helps business stakeholders understand their data through natural language queries.

## Overview

This project demonstrates an AI-powered data analyst that can:

- Answer business questions in natural language
- Generate and execute SQL queries automatically
- Analyze subscription, customer, and churn data
- Provide insights in plain English for non-technical audiences

## Features

- **Natural Language Queries**: Ask questions about your business data in plain English
- **Automated SQL Generation**: Claude generates appropriate SQL queries based on your questions
- **Business Intelligence**: Analyzes customer behavior, subscription metrics, and churn patterns
- **Safety Checks**: Validates queries are read-only (SELECT statements only)
- **Sample Database**: Includes a pre-populated SQLite database with business data

## Database Schema

The project includes four tables:

- **customers**: Customer information (name, email, signup date, industry, company size)
- **subscriptions**: Subscription details (plan type, MRR, status, dates)
- **usage_metrics**: Daily usage data (logins, feature usage, support tickets)
- **churn_events**: Churn tracking (dates and reasons)

## Setup

1. Clone the repository:

```bash
git clone https://github.com/jordand2003/LangChain-Data-Analyst.git
cd LangChain-Data-Analyst
```

2. Install dependencies:

```bash
pip install python-dotenv langchain-anthropic langchain-core langchain-experimental langgraph langchain-community
```

3. Create a `.env` file with your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

4. Run the analyst:

```bash
python data_analyst.py
```

## Usage Example

The script includes a sample query:

```python
"Why did churn increase last month?"
```

The agent will:

1. Analyze the question
2. Query the database tables
3. Generate SQL to find patterns
4. Provide a detailed analysis in plain English

## Dependencies

Key packages (install via pip):

- `langchain-anthropic` - Claude model integration
- `langchain-core` - Core LangChain functionality
- `langchain-experimental` - SQL database features
- `langgraph` - Graph-based agent orchestration with checkpointers
- `python-dotenv` - Environment variable loading

## Project Structure

```
.
├── data_analyst.py      # Main agent script
├── business_data.db     # SQLite database with sample data
├── .env                 # API keys (not tracked in git)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Security

The `.env` file containing your API key is excluded from version control via `.gitignore` to keep your credentials secure.

Agent can only execute read only queries (SELECT statements) to prevent from SQL injection attacks.

---

_README created by Claude Code_
