# Agent2Agent Architecture

```mermaid
flowchart TD
    User[User] --> CLI[CLI Client]
    CLI --> Orchestrator[A2A Orchestrator]
    
    subgraph Adapters
        LangGraphAdapter[LangGraph A2A Adapter]
        AgnoAdapter[Agno A2A Adapter]
    end
    
    Orchestrator --> LangGraphAdapter
    Orchestrator --> AgnoAdapter
    
    subgraph Agents
        LangGraphAgent[LangGraph Research Agent]
        AgnoAgent[Agno YouTube Agent]
    end
    
    LangGraphAdapter --> LangGraphAgent
    AgnoAdapter --> AgnoAgent
    
    LangGraphAgent --> TavilySearch[Tavily Search API]
    AgnoAgent --> YouTubeAPI[YouTube API]
    
    classDef user fill:#f9f,stroke:#333,stroke-width:2px
    classDef orchestrator fill:#bbf,stroke:#33f,stroke-width:2px
    classDef adapter fill:#bfb,stroke:#3f3,stroke-width:2px
    classDef agent fill:#fbb,stroke:#f33,stroke-width:2px
    classDef api fill:#ddd,stroke:#999,stroke-width:1px
    
    class User user
    class CLI,Orchestrator orchestrator
    class LangGraphAdapter,AgnoAdapter adapter
    class LangGraphAgent,AgnoAgent agent
    class TavilySearch,YouTubeAPI api
```

## Component Description

### User Interface
- **CLI Client**: Command-line interface for interacting with the orchestrator

### Orchestration
- **A2A Orchestrator**: Central component that delegates tasks to specialized agents

### Adapters
- **LangGraph A2A Adapter**: Adapts the LangGraph agent to the A2A protocol
- **Agno A2A Adapter**: Adapts the Agno YouTube agent to the A2A protocol

### Agents
- **LangGraph Research Agent**: Research agent built with LangGraph
- **Agno YouTube Agent**: YouTube video analysis agent built with Agno

### External APIs
- **Tavily Search API**: Used by the LangGraph agent for web search
- **YouTube API**: Used by the Agno agent for video analysis
