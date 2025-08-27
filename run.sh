#!/bin/bash

# Script to run the entire Agent2Agent system

# Exit on error
set -e

# Function to check if a port is in use
port_in_use() {
  lsof -i:$1 &>/dev/null
}

# Function to start a component
start_component() {
  local name=$1
  local command=$2
  local port=$3
  local log_file="logs/$name.log"
  
  echo "Starting $name on port $port..."
  
  if port_in_use $port; then
    echo "⚠️  Port $port is already in use. $name may already be running."
    return 1
  fi
  
  # Run the command in the background and save the PID
  eval "$command" > "$log_file" 2>&1 &
  local pid=$!
  
  # Wait a moment for the process to start
  sleep 2
  
  # Check if the process is still running
  if kill -0 $pid 2>/dev/null; then
    echo "✅ $name started successfully (PID: $pid)"
    echo $pid > "logs/$name.pid"
  else
    echo "❌ Failed to start $name. Check logs/$name.log for details."
    return 1
  fi
}

# Create logs directory
mkdir -p logs

# Start the LangGraph agent adapter
start_component "langgraph-adapter" "cd src/adapters/langgraph && python run.py" 8001

# Start the Agno agent adapter
start_component "agno-adapter" "cd src/adapters/agno && python run.py" 8002

# Start the orchestrator
start_component "orchestrator" "python src/orchestrator.py" 8000

echo ""
echo "🚀 All components started successfully!"
echo "📊 You can now use the CLI client: python src/cli.py"
echo ""
echo "📝 Logs are available in the logs directory"
echo "⚠️  To stop all components, run: ./stop.sh"
