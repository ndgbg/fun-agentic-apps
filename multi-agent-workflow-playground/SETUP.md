# Setup Guide

## Prerequisites

- Python 3.8+
- Anthropic API key
- Modern web browser (for visual builder)

## Installation

```bash
# Clone the repository
git clone https://github.com/ndgbg/fun-agentic-apps.git
cd fun-agentic-apps/multi-agent-workflow-playground

# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=your_key_here
```

## Quick Start

### 1. Run Example Workflow

```bash
python engine.py
```

This creates and executes a 3-agent workflow:
- Researcher (with web search tool)
- Writer
- Critic (with shared memory)

### 2. Run Demos

```bash
python demo.py
```

Shows three workflow patterns:
- Content creation (4 agents)
- Parallel analysis (conceptual)
- Conditional routing

### 3. Visual Builder

```bash
# Open in browser
open index.html
# or
python -m http.server 8000
# then visit http://localhost:8000
```

## Using the Visual Builder

### Building a Workflow

1. **Drag agents** from the palette to the canvas
2. **Click agents** to connect them (click first agent, then second)
3. **Double-click agents** to configure:
   - Name and system prompt
   - Tools (web search, calculator, file reader, code executor)
   - Memory type (none, short-term, long-term, shared)

### Running a Workflow

1. Click **"▶️ Run Workflow"**
2. Enter initial input
3. View execution results in the bottom panel

### Saving/Loading

- **Save Workflow**: Downloads JSON file
- **Load Workflow**: Upload previously saved JSON
- **Export JSON**: Copy workflow definition
- **Export Mermaid**: Copy diagram for documentation

## Programmatic Usage

### Basic Workflow

```python
from engine import WorkflowBuilder, WorkflowEngine, AgentRole

# Create workflow
builder = WorkflowBuilder()
workflow = builder.create_workflow("My Workflow", "Description")

# Add agents
agent1 = builder.add_agent(
    workflow.id,
    "Agent 1",
    AgentRole.RESEARCHER,
    "You are a researcher."
)

agent2 = builder.add_agent(
    workflow.id,
    "Agent 2",
    AgentRole.WRITER,
    "You are a writer."
)

# Connect agents
builder.connect_agents(workflow.id, agent1.id, agent2.id)

# Execute
engine = WorkflowEngine()
results = await engine.execute_workflow(workflow, "Your input here")
```

### Adding Tools

```python
from engine import Tool, ToolType

agent = builder.add_agent(
    workflow.id,
    "Researcher",
    AgentRole.RESEARCHER,
    "You gather information.",
    tools=[
        Tool(ToolType.WEB_SEARCH, "search"),
        Tool(ToolType.CALCULATOR, "calc")
    ]
)
```

### Adding Memory

```python
from engine import Memory, MemoryType

agent = builder.add_agent(
    workflow.id,
    "Writer",
    AgentRole.WRITER,
    "You write content.",
    memory=Memory(MemoryType.SHORT_TERM, capacity=10)
)
```

### Conditional Routing

```python
builder.connect_agents(
    workflow.id,
    agent1.id,
    agent2.id,
    condition="success"  # Only route if no error
)
```

## Agent Roles

| Role | Purpose | Typical Tools |
|------|---------|---------------|
| RESEARCHER | Information gathering | Web search, file reader |
| WRITER | Content creation | None (uses LLM) |
| CRITIC | Review and feedback | None (uses LLM) |
| COORDINATOR | Orchestration | None (uses LLM) |
| ANALYST | Data analysis | Calculator, file reader |
| EXECUTOR | Action taking | Code executor, API caller |

## Memory Types

| Type | Scope | Use Case |
|------|-------|----------|
| NONE | Stateless | Simple transformations |
| SHORT_TERM | Agent-specific | Recent context |
| LONG_TERM | Agent-specific | Persistent knowledge |
| SHARED | Cross-agent | Collaboration |

## Tool Types

| Tool | Purpose | Configuration |
|------|---------|---------------|
| WEB_SEARCH | Search the web | `{"max_results": 5}` |
| CALCULATOR | Math operations | None |
| FILE_READER | Read files | `{"path": "/path/to/file"}` |
| CODE_EXECUTOR | Run code | `{"language": "python"}` |
| API_CALLER | Call APIs | `{"endpoint": "url"}` |
| DATABASE | Query DB | `{"connection": "string"}` |

## Execution Results

Each agent execution returns:

```python
ExecutionResult(
    workflow_id="...",
    agent_id="...",
    agent_name="Researcher",
    input="Research topic X",
    output="Found 5 key insights...",
    tools_used=["web_search"],
    memory_accessed=True,
    execution_time=2.3,
    timestamp="2025-01-20T10:30:00",
    error=None  # or error message
)
```

## Workflow Persistence

Workflows are saved as JSON:

```json
{
  "id": "workflow_123",
  "name": "My Workflow",
  "description": "...",
  "entry_point": "agent_456",
  "agents": [...],
  "connections": [...]
}
```

Load with:

```python
builder = WorkflowBuilder()
builder.load_workflows("workflows.json")
workflow = builder.workflows["workflow_123"]
```

## Troubleshooting

### API Key Not Set

```
Error: API key not configured
```

Solution:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

### Import Errors

```
ModuleNotFoundError: No module named 'anthropic'
```

Solution:
```bash
pip install -r requirements.txt
```

### Visual Builder Not Loading

Solution:
```bash
# Use a local server
python -m http.server 8000
# Visit http://localhost:8000
```

## Advanced Usage

### Custom Tool Implementation

```python
class CustomTool:
    async def execute(self, input_text: str) -> str:
        # Your tool logic
        return result

# Add to engine
engine._custom_tools["my_tool"] = CustomTool()
```

### Parallel Execution

Current implementation is sequential. For parallel execution:

```python
# Future enhancement
import asyncio

tasks = [
    engine._execute_agent(workflow, agent1, input),
    engine._execute_agent(workflow, agent2, input)
]
results = await asyncio.gather(*tasks)
```

### Custom Memory Backend

```python
class CustomMemory:
    def store(self, key: str, value: str):
        # Your storage logic
        pass
    
    def retrieve(self, key: str) -> str:
        # Your retrieval logic
        pass

# Use in engine
engine.memory_backend = CustomMemory()
```

## Examples

See `demo.py` for complete examples:
- Content creation workflow
- Multi-perspective analysis
- Quality-gated content

## Support

- GitHub Issues: [Report bugs](https://github.com/ndgbg/fun-agentic-apps/issues)
- Documentation: [README.md](README.md)
- Examples: [demo.py](demo.py)

## Next Steps

1. Build your first workflow with the visual builder
2. Try the example workflows in `demo.py`
3. Create custom agents for your use case
4. Share your workflows with the community!
