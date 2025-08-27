#!/usr/bin/env python3
"""
A2A Orchestrator CLI Client

This script provides a command-line interface to interact with the A2A orchestrator.
"""

import argparse
import asyncio
import json
import sys

import httpx

async def send_request(query, agent_name=None):
    """Send a request to the orchestrator."""
    url = "http://localhost:8000/delegate"
    payload = {"query": query}
    
    if agent_name:
        payload["agent_name"] = agent_name
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Error: {str(e)}")
            print("Make sure the orchestrator is running at http://localhost:8000")
            return None

async def get_available_agents():
    """Get the list of available agents."""
    url = "http://localhost:8000/"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            print(f"Error: {str(e)}")
            print("Make sure the orchestrator is running at http://localhost:8000")
            return None

def display_result(result):
    """Display the result in a readable format."""
    if not result:
        return
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"✅ Task delegated to: {result['agent']}")
    print(f"📝 Task ID: {result['task_id']}")
    print(f"🔄 Status: {result['status']}")
    
    if result.get("response"):
        print("\n" + "=" * 80)
        print("📄 Response:")
        print("=" * 80)
        print(result["response"])
        print("=" * 80)
    else:
        print("\n❓ No response content available")

async def interactive_mode():
    """Run the client in interactive mode."""
    print("🤖 A2A Orchestrator CLI Client")
    print("=" * 80)
    
    # Get available agents
    agents_info = await get_available_agents()
    if agents_info:
        print(f"Connected to orchestrator: {agents_info['name']}")
        print(f"Available agents: {', '.join(agents_info['agents'])}")
    
    print("\nType 'exit' or 'quit' to exit")
    print("=" * 80)
    
    while True:
        try:
            query = input("\n🔍 Enter your query: ").strip()
            
            if query.lower() in ("exit", "quit"):
                break
            
            if not query:
                continue
            
            # Ask for specific agent (optional)
            agent_choice = input("🤖 Specify agent (leave empty for auto-selection): ").strip()
            agent_name = agent_choice if agent_choice else None
            
            print("\n⏳ Processing request...")
            result = await send_request(query, agent_name)
            display_result(result)
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="A2A Orchestrator CLI Client")
    parser.add_argument("--query", "-q", help="Query to send to the orchestrator")
    parser.add_argument("--agent", "-a", help="Specific agent to use")
    
    args = parser.parse_args()
    
    if args.query:
        # Single query mode
        result = asyncio.run(send_request(args.query, args.agent))
        display_result(result)
    else:
        # Interactive mode
        try:
            asyncio.run(interactive_mode())
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)

if __name__ == "__main__":
    main()
