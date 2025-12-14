# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LangChain practice repository for experimenting with LangChain agents, tools, and SQL database interactions. The project uses LangChain's agent framework with Claude Sonnet 4.5 as the underlying model.

## Architecture

The codebase follows a single-file agent pattern with these key components:

- **System Prompt**: Defines agent behavior as an analytical professional that translates natural language to SQL queries and returns plain English responses
- **Database Chain**: Placeholder for SQLDatabaseChain integration (currently empty)
- **LangChain Agent**: Uses `create_agent` with InMemorySaver checkpointer for conversation state management
- **Model**: Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) via `init_chat_model`
- **Structured Output**: Uses `ToolStrategy` with a `ResponseFormat` dataclass to ensure consistent response formatting

The agent is designed to be conversational with thread-based memory via the checkpointer.

## Development Commands

### Running the Agent

```bash
python3 weather.py
```

### Environment Setup

The project requires Python 3.13+ and uses `python-dotenv` for environment variable management. API credentials are stored in `.env`:

- `ANTHROPIC_API_KEY`: Required for Claude API access

### Dependencies

Key packages (install via pip):
- `langchain-anthropic` - Claude model integration
- `langchain-core` - Core LangChain functionality
- `langchain-experimental` - SQL database features
- `langgraph` - Graph-based agent orchestration with checkpointers
- `python-dotenv` - Environment variable loading

## Current State

The `weather.py` file is a work-in-progress with:
- Empty `SQLDatabaseChain` configuration (line 29-31)
- Empty tools list in agent creation (line 55)
- Example invocation asking "what is the weather outside?" (line 66)

The agent structure is in place but needs:
1. SQL database connection configuration in the chain
2. Tools defined and passed to the agent
3. Integration between the database chain and agent tools
