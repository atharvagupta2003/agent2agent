#!/bin/bash

# Script to stop all Agent2Agent components

# Check if logs directory exists
if [ ! -d "logs" ]; then
  echo "❌ Logs directory not found. No components to stop."
  exit 1
fi

# Function to stop a component
stop_component() {
  local name=$1
  local pid_file="logs/$name.pid"
  
  if [ -f "$pid_file" ]; then
    local pid=$(cat "$pid_file")
    echo "Stopping $name (PID: $pid)..."
    
    if kill -0 $pid 2>/dev/null; then
      kill $pid
      echo "✅ $name stopped"
    else
      echo "⚠️  Process for $name is not running"
    fi
    
    rm "$pid_file"
  else
    echo "⚠️  PID file for $name not found"
  fi
}

# Stop all components
stop_component "orchestrator"
stop_component "langgraph-adapter"
stop_component "agno-adapter"

echo ""
echo "🛑 All components stopped"
