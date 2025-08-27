"""LangGraph A2A Adapter

This module adapts the LangGraph agent to the A2A protocol, allowing it to be used
with the A2A orchestrator.
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Union

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

# Import the LangGraph agent
import sys
import os
# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.subagents.langgraph.agent import agent_executor, model

# A2A protocol types
class Part(BaseModel):
    type: str = "text"
    text: Optional[str] = None

class Message(BaseModel):
    role: str
    parts: List[Part]
    messageId: str
    taskId: Optional[str] = None
    contextId: Optional[str] = None

class MessageSendParams(BaseModel):
    message: Message

class SendMessageRequest(BaseModel):
    id: str
    params: MessageSendParams

class TaskStatus(BaseModel):
    state: str
    message: Optional[Message] = None

class Task(BaseModel):
    id: str
    context_id: str
    status: TaskStatus
    created_time: str = Field(default_factory=lambda: str(uuid.uuid4()))
    updated_time: str = Field(default_factory=lambda: str(uuid.uuid4()))

class SendMessageSuccessResponse(BaseModel):
    id: str
    result: Task

class SendMessageResponse(BaseModel):
    root: SendMessageSuccessResponse

# Create FastAPI app
app = FastAPI(title="LangGraph A2A Adapter")

# In-memory storage for tasks
tasks = {}

# Agent card definition
AGENT_CARD = {
    "name": "LangGraph Research Agent",
    "description": "A research agent built with LangGraph that can search for information and provide detailed answers",
    "url": "http://localhost:8001/",  # Update with your actual deployment URL
    "version": "1.0.0",
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "stateTransitionHistory": False
    },
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"],
    "skills": [
        {
            "id": "research",
            "name": "Web Research",
            "description": "Searches the web for information and provides detailed answers",
            "tags": ["research", "information", "knowledge"],
            "examples": [
                "What are the latest developments in quantum computing?",
                "Explain the impact of climate change on marine ecosystems"
            ]
        }
    ]
}

@app.get("/")
async def get_agent_card():
    """Return the agent card."""
    return AGENT_CARD

@app.post("/messages")
async def handle_message(request: SendMessageRequest):
    """Handle incoming A2A messages."""
    # Extract message from request
    message = request.params.message
    
    # Generate task ID if not provided
    task_id = message.taskId or str(uuid.uuid4())
    context_id = message.contextId or str(uuid.uuid4())
    
    # Extract query from message
    query = ""
    for part in message.parts:
        if part.type == "text" and part.text:
            query += part.text
    
    if not query:
        raise HTTPException(status_code=400, detail="No text content in message")
    
    # Create a task
    task = Task(
        id=task_id,
        context_id=context_id,
        status=TaskStatus(state="working")
    )
    tasks[task_id] = task
    
    try:
        # Run the LangGraph agent
        config = {"configurable": {"thread_id": context_id}}
        result = agent_executor.invoke({"messages": [("user", query)]}, config)
        
        # Extract response robustly for LangGraph/LC messages
        response = ""
        try:
            if "messages" in result and result["messages"]:
                last_msg = result["messages"][-1]
                # LangChain message objects (AIMessage/HumanMessage)
                content = getattr(last_msg, "content", None)
                if content:
                    response = content if isinstance(content, str) else str(content)
                else:
                    # Tuple fallback: ("ai", text)
                    try:
                        if isinstance(last_msg, (list, tuple)) and len(last_msg) >= 2:
                            response = str(last_msg[1])
                    except Exception:
                        response = str(last_msg)
            else:
                response = json.dumps(result)
        except Exception as _extract_e:
            response = f"Unable to extract response. Raw: {result}"
        
        # Update task status
        task.status = TaskStatus(
            state="completed",
            message=Message(
                role="assistant",
                parts=[Part(type="text", text=response)],
                messageId=str(uuid.uuid4()),
                taskId=task_id,
                contextId=context_id
            )
        )
        
        # Return success response
        return SendMessageResponse(
            root=SendMessageSuccessResponse(
                id=request.id,
                result=task
            )
        )
    except Exception as e:
        # Update task status to error
        task.status = TaskStatus(
            state="error",
            message=Message(
                role="assistant",
                parts=[Part(type="text", text=f"Error: {str(e)}")],
                messageId=str(uuid.uuid4()),
                taskId=task_id,
                contextId=context_id
            )
        )
        
        # Return error response
        return SendMessageResponse(
            root=SendMessageSuccessResponse(
                id=request.id,
                result=task
            )
        )

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task status."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
