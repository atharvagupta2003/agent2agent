"""A2A Orchestrator

This module implements an orchestrator that delegates tasks to specialized agents
using the A2A protocol.
"""

import asyncio
import json
import os
import uuid
from typing import Dict, List, Optional, Any, Union

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
import httpx

# A2A protocol types
class AgentCard(BaseModel):
    name: str
    description: str
    url: str
    version: str
    capabilities: Dict[str, bool]
    defaultInputModes: List[str]
    defaultOutputModes: List[str]
    skills: List[Dict[str, Any]]

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

class RemoteAgentConnection:
    """Handles connection to a remote A2A agent."""
    
    def __init__(self, agent_card: AgentCard, agent_url: str):
        self.agent_card = agent_card
        self.agent_url = agent_url
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def send_message(self, message_request: SendMessageRequest) -> SendMessageResponse:
        """Send a message to the remote agent."""
        response = await self.client.post(
            f"{self.agent_url}/messages",
            json=message_request.dict(),
            timeout=30.0
        )
        response.raise_for_status()
        return SendMessageResponse.parse_obj(response.json())

class Orchestrator:
    """Orchestrator that delegates tasks to specialized agents."""
    
    def __init__(self):
        self.remote_agents: Dict[str, RemoteAgentConnection] = {}
        self.agent_cards: Dict[str, AgentCard] = {}
        
    async def initialize(self, agent_urls: List[str]):
        """Initialize connections to remote agents."""
        for url in agent_urls:
            try:
                # Fetch agent card
                async with httpx.AsyncClient() as client:
                    response = await client.get(url)
                    response.raise_for_status()
                    agent_card = AgentCard.parse_obj(response.json())
                    
                # Create connection
                connection = RemoteAgentConnection(agent_card, url)
                self.remote_agents[agent_card.name] = connection
                self.agent_cards[agent_card.name] = agent_card
                print(f"✅ Connected to agent: {agent_card.name} at {url}")
            except Exception as e:
                print(f"❌ Failed to connect to agent at {url}: {e}")
    
    def get_agent_descriptions(self) -> str:
        """Get descriptions of all available agents."""
        descriptions = []
        for name, card in self.agent_cards.items():
            skills = ", ".join([skill["name"] for skill in card.skills])
            descriptions.append(f"- {name}: {card.description}. Skills: {skills}")
        return "\n".join(descriptions)
    
    def find_best_agent(self, query: str) -> Optional[str]:
        """Find the best agent to handle a query."""
        # Simple keyword matching for now
        if "youtube" in query.lower() or "video" in query.lower():
            return "YouTube Analysis Agent"
        elif "research" in query.lower() or "search" in query.lower() or "information" in query.lower():
            return "LangGraph Research Agent"
        return None
    
    async def delegate_task(self, agent_name: str, query: str, task_id: str = None, context_id: str = None) -> Dict[str, Any]:
        """Delegate a task to a specialized agent."""
        if agent_name not in self.remote_agents:
            return {
                "error": f"Agent '{agent_name}' not found. Available agents: {', '.join(self.remote_agents.keys())}"
            }
        
        # Generate IDs if not provided
        task_id = task_id or str(uuid.uuid4())
        context_id = context_id or str(uuid.uuid4())
        
        # Create message payload
        message_id = str(uuid.uuid4())
        request = SendMessageRequest(
            id=message_id,
            params=MessageSendParams(
                message=Message(
                    role="user",
                    parts=[Part(type="text", text=query)],
                    messageId=message_id,
                    taskId=task_id,
                    contextId=context_id
                )
            )
        )
        
        try:
            # Send message to remote agent
            agent_connection = self.remote_agents[agent_name]
            response = await agent_connection.send_message(request)
            
            # Process response
            task = response.root.result
            
            return {
                "agent": agent_name,
                "task_id": task.id,
                "context_id": task.context_id,
                "status": task.status.state,
                "response": task.status.message.parts[0].text if task.status.message and task.status.message.parts else None
            }
        except Exception as e:
            return {
                "error": f"Error delegating task to {agent_name}: {str(e)}"
            }

# Create FastAPI app for the orchestrator
app = FastAPI(title="A2A Orchestrator")

# Create and initialize the orchestrator
orchestrator = Orchestrator()

@app.on_event("startup")
async def startup_event():
    """Initialize the orchestrator on startup."""
    await orchestrator.initialize([
        "http://localhost:8001",  # LangGraph Research Agent
        "http://localhost:8002",  # YouTube Analysis Agent
    ])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "A2A Orchestrator",
        "description": "Orchestrator that delegates tasks to specialized agents",
        "agents": list(orchestrator.agent_cards.keys())
    }

@app.post("/delegate")
async def delegate_task(request: dict):
    """Delegate a task to the appropriate agent."""
    query = request.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    # Find the best agent for this query
    agent_name = request.get("agent_name") or orchestrator.find_best_agent(query)
    if not agent_name:
        raise HTTPException(status_code=400, detail="Could not determine appropriate agent for this query")
    
    # Delegate the task
    result = await orchestrator.delegate_task(
        agent_name=agent_name,
        query=query,
        task_id=request.get("task_id"),
        context_id=request.get("context_id")
    )
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
