# Agent2Agent: Multi-Framework Agent Orchestration

This project demonstrates how to orchestrate agents built with different frameworks using the A2A (Agent-to-Agent) protocol.

## Overview

Agent2Agent enables seamless communication between agents built with different frameworks:

- **LangGraph Agent**: A research agent built with LangGraph and LangChain
- **Agno Agent**: A YouTube video analysis agent built with Agno
- **A2A Orchestrator**: A central orchestrator that delegates tasks to the appropriate agent

## Architecture

![Architecture](docs/architecture.md)

The system uses the A2A protocol to standardize communication between agents, regardless of their underlying implementation. Each agent exposes an A2A-compatible API through an adapter layer.

## Components

- **Orchestrator**: Central component that receives user queries and delegates tasks to specialized agents
- **Adapters**: Convert existing agents to A2A-compatible endpoints
- **CLI Client**: Simple command-line interface to interact with the orchestrator

## Getting Started

### Prerequisites

- Python 3.10+
- pip or another package manager

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agent2agent.git
   cd agent2agent
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Set up environment variables:
   ```bash
   # For LangGraph agent
   export TAVILY_API_KEY=your_tavily_api_key
   
   # For Agno agent
   export OPENAI_API_KEY=your_openai_api_key
   ```

### Running the System

1. Start the LangGraph agent adapter:
   ```bash
   cd src/adapters/langgraph
   python run.py
   ```

2. Start the Agno agent adapter:
   ```bash
   cd src/adapters/agno
   python run.py
   ```

3. Start the orchestrator:
   ```bash
   python src/orchestrator.py
   ```

4. Use the CLI client to interact with the system:
   ```bash
   python src/cli.py
   ```

## Example Usage

```
🤖 A2A Orchestrator CLI Client
================================================================================
Connected to orchestrator: A2A Orchestrator
Available agents: LangGraph Research Agent, YouTube Analysis Agent

Type 'exit' or 'quit' to exit
================================================================================

🔍 Enter your query: What are the latest developments in quantum computing?
🤖 Specify agent (leave empty for auto-selection): 

⏳ Processing request...
✅ Task delegated to: LangGraph Research Agent
📝 Task ID: 3a7b2c1d-4e5f-6g7h-8i9j-0k1l2m3n4o5p
🔄 Status: completed

================================================================================
📄 Response:
================================================================================
Recent developments in quantum computing include:

1. IBM's 2023 roadmap revealing plans for a 4,158-qubit system by 2025
2. Google's achievement of quantum supremacy with their 53-qubit Sycamore processor
3. Advances in error correction techniques, crucial for practical quantum computing
4. Development of quantum machine learning algorithms that could outperform classical methods
5. Progress in quantum networking and quantum internet infrastructure
6. Increased investment in quantum startups and national quantum initiatives
7. New quantum programming languages and development tools
8. Hybrid quantum-classical computing approaches gaining traction
9. Breakthroughs in topological qubits for more stable quantum systems
10. Early commercial applications in optimization, materials science, and cryptography

These advancements are rapidly moving quantum computing from theoretical research toward practical applications, though significant challenges in qubit stability and error rates remain.
================================================================================

🔍 Enter your query: Analyze this YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ
🤖 Specify agent (leave empty for auto-selection): 

⏳ Processing request...
✅ Task delegated to: YouTube Analysis Agent
📝 Task ID: 6p5o4n3m-2l1k-0j9i-8h7g-6f5e4d3c2b1a
🔄 Status: completed

================================================================================
📄 Response:
================================================================================
# 📋 VIDEO OVERVIEW

**Title:** Rick Astley - Never Gonna Give You Up (Official Music Video)
**Duration:** 3:33
**Channel:** Rick Astley
**Upload Date:** October 25, 2009
**Video Category:** Music Video
**Production Quality:** Professional studio production with high-quality visuals and audio
**Special Features:** Captions available in multiple languages

# 🎯 CONTENT STRUCTURE ANALYSIS

The video follows a classic music video structure with:
- Opening scene establishing the artist and setting
- Alternating performance shots and narrative scenes
- Choreographed dance sequences
- Close-up shots of the artist singing
- Recurring visual motifs and locations

# ⏰ PRECISE TIMESTAMP BREAKDOWN

**[00:00 - 00:18]** Introduction - Opening scene with Rick in a trench coat, bartender setting up, initial drum beats and synthesizer intro
**[00:19 - 00:32]** First Verse - Rick begins singing while standing in an alley, wearing a raincoat
**[00:33 - 00:47]** Pre-Chorus - Transition to indoor scenes with backup dancers
**[00:48 - 01:02]** Chorus - Iconic dance moves begin, featuring Rick's signature side-to-side movements and arm gestures
**[01:03 - 01:17]** Second Verse - Return to narrative elements, Rick singing in various locations
**[01:18 - 01:32]** Pre-Chorus - Similar to first pre-chorus with additional dance elements
**[01:33 - 01:47]** Chorus - Repeated choreography with variations
**[01:48 - 02:02]** Bridge - Instrumental section with extended dance sequence
**[02:03 - 02:32]** Third Verse & Pre-Chorus - Final verse with intensified performance elements
**[02:33 - 03:02]** Final Chorus - Extended chorus with full choreography
**[03:03 - 03:33]** Outro - Fadeout with repeated chorus lyrics and final dance movements

# 📚 KEY INSIGHTS

1. **Cultural Impact:** This video has become one of the internet's most famous memes known as "Rickrolling," where people are tricked into clicking links leading to this video
2. **Distinctive Visual Style:** The 1980s aesthetic features bold colors, characteristic dance moves, and period-appropriate fashion
3. **Choreography:** The dance moves have become iconic and instantly recognizable across generations
4. **Production Techniques:** Showcases typical 1980s music video production with multiple camera angles, quick cuts, and simple but effective visual effects
5. **Longevity:** The video has gained a second life through internet culture, far beyond its original release

# 🎨 CONTENT-SPECIFIC ANALYSIS

**For Music Video Content:**
- **Artist Presentation:** Rick Astley is presented as both a vocalist and performer with emphasis on his distinctive voice and dance moves
- **Visual Storytelling:** Simple narrative elements interspersed with performance shots
- **Cinematography:** Uses standard music video techniques of the era including medium shots, close-ups, and wide dance sequences
- **Color Palette:** Rich, saturated colors typical of 1980s music videos
- **Editing Rhythm:** Cut to match the beat and energy of the song

# 💡 PRACTICAL APPLICATIONS

- **Study of Viral Phenomena:** Perfect case study for how pre-internet content can gain new cultural significance through memes
- **Music Video Production:** Demonstrates effective simplicity in music video creation
- **Pop Culture Reference:** Understanding this video is essential for recognizing a significant internet cultural reference
- **Marketing Lessons:** Shows how unexpected second lives can emerge for content through cultural recontextualization

# 📊 EXECUTIVE SUMMARY

"Never Gonna Give You Up" represents a perfect storm of 1980s pop music video production that gained unprecedented cultural relevance decades later through internet meme culture. The video's simple but effective formula combines catchy music, distinctive visuals, and memorable choreography. Its transformation into the "Rickroll" phenomenon demonstrates how media can transcend its original context to become a shared cultural touchpoint across generations. The video's enduring popularity speaks to both the quality of the original song and the unpredictable nature of internet culture in creating new meanings for existing content.
================================================================================