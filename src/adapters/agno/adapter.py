"""Agno YouTube Agent A2A Adapter

This module adapts the Agno YouTube Agent to the A2A protocol, allowing it to be used
with the A2A orchestrator.
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Union

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

# Import the Agno YouTube agent
import sys
import os
# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.subagents.agno.youtube_agent import YouTubeAgentPro

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
app = FastAPI(title="Agno YouTube Agent A2A Adapter")

# In-memory storage for tasks and agent instance
tasks = {}
youtube_agent = YouTubeAgentPro()

# Agent card definition
AGENT_CARD = {
    "name": "YouTube Analysis Agent",
    "description": "An advanced YouTube content analyzer that provides comprehensive video analysis, timestamps, summaries, and more",
    "url": "http://localhost:8002/",  # Update with your actual deployment URL
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
            "id": "analyze_video",
            "name": "YouTube Video Analysis",
            "description": "Analyzes YouTube videos and provides detailed breakdowns, timestamps, summaries, and more",
            "tags": ["youtube", "video", "analysis", "summary"],
            "examples": [
                "Analyze this YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "Provide a detailed analysis of https://youtu.be/abc123"
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
        # Extract YouTube URL from query
        import re
        youtube_regex = re.compile(
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        
        match = youtube_regex.search(query)
        if not match:
            raise ValueError("No valid YouTube URL found in the message")
        
        youtube_url = match.group(0)
        
        # Determine analysis mode based on query
        mode = "detailed"  # Default to detailed
        if "quick" in query.lower() or "brief" in query.lower():
            mode = "quick"
        elif "custom" in query.lower() or "specialized" in query.lower():
            mode = "custom"
        
        # Run the YouTube agent
        analysis = youtube_agent.analyze_video(youtube_url, mode)
        
        if not analysis:
            raise ValueError("Failed to analyze the YouTube video")
        
        # Update task status
        task.status = TaskStatus(
            state="completed",
            message=Message(
                role="assistant",
                parts=[Part(type="text", text=analysis)],
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
                parts=[Part(type="text", text=f"Error analyzing YouTube video: {str(e)}")],
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
    uvicorn.run(app, host="0.0.0.0", port=8002)
