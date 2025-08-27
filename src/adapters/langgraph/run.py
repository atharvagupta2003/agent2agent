#!/usr/bin/env python3
"""
LangGraph A2A Adapter Runner

This script starts the LangGraph A2A adapter server.
"""

import uvicorn
from adapter import app

if __name__ == "__main__":
    print("🚀 Starting LangGraph A2A Adapter Server")
    print("📝 Agent Card available at: http://localhost:8001/")
    print("📡 A2A Endpoints:")
    print("   - POST /messages")
    print("   - GET /tasks/{task_id}")
    uvicorn.run(app, host="0.0.0.0", port=8001)
