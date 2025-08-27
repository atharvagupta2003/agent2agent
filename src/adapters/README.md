# A2A Agent Adapters

This directory contains adapters that make existing agents compatible with the A2A protocol.

## Overview

The adapters wrap existing agents with a FastAPI server that implements the A2A protocol endpoints:

- `GET /` - Returns the agent card
- `POST /messages` - Handles incoming messages and delegates them to the underlying agent
- `GET /tasks/{task_id}` - Returns the status of a task

## Available Adapters

### LangGraph Research Agent

Located in `langgraph/adapter.py`, this adapter wraps the LangGraph-based research agent.

**Features:**
- Web search capability using Tavily
- Detailed responses to research queries

**Port:** 8001

### Agno YouTube Agent

Located in `agno/adapter.py`, this adapter wraps the Agno YouTube analysis agent.

**Features:**
- YouTube video analysis
- Timestamps and summaries
- Content categorization

**Port:** 8002

## Running the Adapters

To run each adapter:

```bash
# LangGraph Research Agent
cd src/adapters/langgraph
python run.py

# Agno YouTube Agent
cd src/adapters/agno
python run.py
```

## Using with the Orchestrator

The adapters are designed to work with the A2A orchestrator located at `src/orchestrator.py`.

To use the orchestrator with these adapters:

1. Start both adapters as described above
2. Run the orchestrator: `python src/orchestrator.py`
3. Use the CLI client to interact with the orchestrator: `python src/cli.py`

## Extending

To add a new adapter:

1. Create a new directory for your agent: `src/adapters/your_agent_name/`
2. Create an adapter file based on the existing examples
3. Define an appropriate agent card
4. Implement the message handling logic to interface with your agent
5. Add your agent's URL to the orchestrator's initialization in `src/orchestrator.py`
