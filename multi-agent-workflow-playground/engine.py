#!/usr/bin/env python3
"""
Multi-Agent Workflow Playground
Visual builder and executor for multi-agent systems.
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

class AgentRole(Enum):
    RESEARCHER = "researcher"
    WRITER = "writer"
    CRITIC = "critic"
    COORDINATOR = "coordinator"
    EXECUTOR = "executor"
    ANALYST = "analyst"

class MemoryType(Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    SHARED = "shared"
    NONE = "none"

class ToolType(Enum):
    WEB_SEARCH = "web_search"
    CODE_EXECUTOR = "code_executor"
    FILE_READER = "file_reader"
    API_CALLER = "api_caller"
    DATABASE = "database"
    CALCULATOR = "calculator"

@dataclass
class Tool:
    type: ToolType
    name: str
    config: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class Memory:
    type: MemoryType
    capacity: int = 1000
    persistence: bool = False
    
@dataclass
class Agent:
    id: str
    name: str
    role: AgentRole
    system_prompt: str
    tools: List[Tool] = field(default_factory=list)
    memory: Optional[Memory] = None
    model: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.7
    
@dataclass
class Connection:
    from_agent: str
    to_agent: str
    condition: Optional[str] = None
    
@dataclass
class Workflow:
    id: str
    name: str
    description: str
    agents: List[Agent]
    connections: List[Connection]
    entry_point: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
@dataclass
class ExecutionResult:
    workflow_id: str
    agent_id: str
    agent_name: str
    input: str
    output: str
    tools_used: List[str]
    memory_accessed: bool
    execution_time: float
    timestamp: str
    error: Optional[str] = None

class WorkflowEngine:
    """Executes multi-agent workflows with full state tracking."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.execution_history = []
        self.agent_memories = {}
        self.shared_memory = {}
        
    async def execute_workflow(self, workflow: Workflow, initial_input: str) -> List[ExecutionResult]:
        """Execute a workflow starting from entry point."""
        
        if not self.api_key:
            return [ExecutionResult(
                workflow_id=workflow.id,
                agent_id="system",
                agent_name="System",
                input=initial_input,
                output="Set ANTHROPIC_API_KEY to execute workflows",
                tools_used=[],
                memory_accessed=False,
                execution_time=0.0,
                timestamp=datetime.now().isoformat(),
                error="API key not configured"
            )]
        
        results = []
        current_agent_id = workflow.entry_point
        current_input = initial_input
        visited = set()
        
        while current_agent_id and current_agent_id not in visited:
            visited.add(current_agent_id)
            
            agent = self._find_agent(workflow, current_agent_id)
            if not agent:
                break
            
            # Execute agent
            result = await self._execute_agent(workflow, agent, current_input)
            results.append(result)
            
            if result.error:
                break
            
            # Find next agent
            next_agent = self._find_next_agent(workflow, current_agent_id, result)
            current_agent_id = next_agent
            current_input = result.output
        
        return results
    
    async def _execute_agent(self, workflow: Workflow, agent: Agent, input_text: str) -> ExecutionResult:
        """Execute a single agent."""
        
        import anthropic
        import time
        
        start_time = time.time()
        
        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Build context from memory
            context = self._build_context(agent, input_text)
            
            # Execute tools if needed
            tool_results = []
            if agent.tools:
                tool_results = await self._execute_tools(agent, input_text)
            
            # Build full prompt
            full_prompt = self._build_prompt(agent, context, tool_results, input_text)
            
            # Call LLM
            message = client.messages.create(
                model=agent.model,
                max_tokens=2000,
                temperature=agent.temperature,
                system=agent.system_prompt,
                messages=[{"role": "user", "content": full_prompt}]
            )
            
            output = message.content[0].text
            
            # Update memory
            if agent.memory:
                self._update_memory(agent, input_text, output)
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                workflow_id=workflow.id,
                agent_id=agent.id,
                agent_name=agent.name,
                input=input_text,
                output=output,
                tools_used=[t.name for t in agent.tools],
                memory_accessed=agent.memory is not None,
                execution_time=execution_time,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            return ExecutionResult(
                workflow_id=workflow.id,
                agent_id=agent.id,
                agent_name=agent.name,
                input=input_text,
                output="",
                tools_used=[],
                memory_accessed=False,
                execution_time=time.time() - start_time,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    async def _execute_tools(self, agent: Agent, input_text: str) -> List[Dict]:
        """Execute agent tools."""
        results = []
        
        for tool in agent.tools:
            if tool.type == ToolType.WEB_SEARCH:
                result = await self._web_search(input_text, tool.config)
                results.append({"tool": tool.name, "result": result})
            elif tool.type == ToolType.CALCULATOR:
                result = self._calculator(input_text)
                results.append({"tool": tool.name, "result": result})
            elif tool.type == ToolType.FILE_READER:
                result = self._file_reader(tool.config.get("path", ""))
                results.append({"tool": tool.name, "result": result})
        
        return results
    
    async def _web_search(self, query: str, config: Dict) -> str:
        """Simulate web search."""
        return f"Search results for: {query} (Web search tool executed)"
    
    def _calculator(self, expression: str) -> str:
        """Simple calculator."""
        try:
            # Extract numbers and operators
            import re
            numbers = re.findall(r'\d+\.?\d*', expression)
            if len(numbers) >= 2:
                result = float(numbers[0]) + float(numbers[1])
                return f"Calculation result: {result}"
        except:
            pass
        return "Calculator: Unable to parse expression"
    
    def _file_reader(self, path: str) -> str:
        """Read file content."""
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return f.read()[:500]  # First 500 chars
        except:
            pass
        return f"File reader: Unable to read {path}"
    
    def _build_context(self, agent: Agent, input_text: str) -> str:
        """Build context from agent memory."""
        if not agent.memory:
            return ""
        
        if agent.memory.type == MemoryType.SHORT_TERM:
            memory = self.agent_memories.get(agent.id, [])
            return "\n".join(memory[-5:])  # Last 5 interactions
        elif agent.memory.type == MemoryType.SHARED:
            return "\n".join(list(self.shared_memory.values())[-10:])
        
        return ""
    
    def _build_prompt(self, agent: Agent, context: str, tool_results: List[Dict], input_text: str) -> str:
        """Build full prompt for agent."""
        parts = []
        
        if context:
            parts.append(f"Context from memory:\n{context}\n")
        
        if tool_results:
            parts.append("Tool results:")
            for tr in tool_results:
                parts.append(f"- {tr['tool']}: {tr['result']}")
            parts.append("")
        
        parts.append(f"Task: {input_text}")
        
        return "\n".join(parts)
    
    def _update_memory(self, agent: Agent, input_text: str, output: str):
        """Update agent memory."""
        memory_entry = f"Input: {input_text}\nOutput: {output}"
        
        if agent.memory.type == MemoryType.SHORT_TERM:
            if agent.id not in self.agent_memories:
                self.agent_memories[agent.id] = []
            self.agent_memories[agent.id].append(memory_entry)
            
            # Limit capacity
            if len(self.agent_memories[agent.id]) > agent.memory.capacity:
                self.agent_memories[agent.id] = self.agent_memories[agent.id][-agent.memory.capacity:]
        
        elif agent.memory.type == MemoryType.SHARED:
            key = f"{agent.id}_{datetime.now().timestamp()}"
            self.shared_memory[key] = memory_entry
    
    def _find_agent(self, workflow: Workflow, agent_id: str) -> Optional[Agent]:
        """Find agent by ID."""
        for agent in workflow.agents:
            if agent.id == agent_id:
                return agent
        return None
    
    def _find_next_agent(self, workflow: Workflow, current_id: str, result: ExecutionResult) -> Optional[str]:
        """Find next agent based on connections."""
        for conn in workflow.connections:
            if conn.from_agent == current_id:
                # Check condition if exists
                if conn.condition:
                    if self._evaluate_condition(conn.condition, result):
                        return conn.to_agent
                else:
                    return conn.to_agent
        return None
    
    def _evaluate_condition(self, condition: str, result: ExecutionResult) -> bool:
        """Evaluate transition condition."""
        # Simple condition evaluation
        if "success" in condition.lower():
            return result.error is None
        if "error" in condition.lower():
            return result.error is not None
        return True

class WorkflowBuilder:
    """Visual workflow builder with save/load."""
    
    def __init__(self):
        self.workflows = {}
        self.load_workflows()
    
    def create_workflow(self, name: str, description: str) -> Workflow:
        """Create new workflow."""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            agents=[],
            connections=[],
            entry_point=""
        )
        self.workflows[workflow.id] = workflow
        return workflow
    
    def add_agent(self, workflow_id: str, name: str, role: AgentRole, 
                  system_prompt: str, tools: List[Tool] = None, 
                  memory: Memory = None) -> Agent:
        """Add agent to workflow."""
        agent = Agent(
            id=str(uuid.uuid4()),
            name=name,
            role=role,
            system_prompt=system_prompt,
            tools=tools or [],
            memory=memory
        )
        
        workflow = self.workflows[workflow_id]
        workflow.agents.append(agent)
        
        # Set as entry point if first agent
        if not workflow.entry_point:
            workflow.entry_point = agent.id
        
        return agent
    
    def connect_agents(self, workflow_id: str, from_agent_id: str, 
                       to_agent_id: str, condition: str = None):
        """Connect two agents."""
        workflow = self.workflows[workflow_id]
        connection = Connection(
            from_agent=from_agent_id,
            to_agent=to_agent_id,
            condition=condition
        )
        workflow.connections.append(connection)
    
    def save_workflow(self, workflow_id: str, filepath: str = "workflows.json"):
        """Save workflow to file."""
        workflow = self.workflows[workflow_id]
        
        # Load existing workflows
        workflows_data = {}
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                workflows_data = json.load(f)
        
        # Add/update workflow
        workflows_data[workflow_id] = self._serialize_workflow(workflow)
        
        # Save
        with open(filepath, 'w') as f:
            json.dump(workflows_data, f, indent=2)
    
    def load_workflows(self, filepath: str = "workflows.json"):
        """Load workflows from file."""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                workflows_data = json.load(f)
                
            for wf_id, wf_data in workflows_data.items():
                self.workflows[wf_id] = self._deserialize_workflow(wf_data)
    
    def _serialize_workflow(self, workflow: Workflow) -> Dict:
        """Convert workflow to JSON-serializable dict."""
        return {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "entry_point": workflow.entry_point,
            "created_at": workflow.created_at,
            "agents": [
                {
                    "id": a.id,
                    "name": a.name,
                    "role": a.role.value,
                    "system_prompt": a.system_prompt,
                    "model": a.model,
                    "temperature": a.temperature,
                    "tools": [{"type": t.type.value, "name": t.name, "config": t.config} for t in a.tools],
                    "memory": {"type": a.memory.type.value, "capacity": a.memory.capacity} if a.memory else None
                }
                for a in workflow.agents
            ],
            "connections": [
                {"from": c.from_agent, "to": c.to_agent, "condition": c.condition}
                for c in workflow.connections
            ]
        }
    
    def _deserialize_workflow(self, data: Dict) -> Workflow:
        """Convert dict to Workflow object."""
        agents = [
            Agent(
                id=a["id"],
                name=a["name"],
                role=AgentRole(a["role"]),
                system_prompt=a["system_prompt"],
                model=a.get("model", "claude-3-5-sonnet-20241022"),
                temperature=a.get("temperature", 0.7),
                tools=[Tool(ToolType(t["type"]), t["name"], t.get("config", {})) for t in a.get("tools", [])],
                memory=Memory(MemoryType(a["memory"]["type"]), a["memory"]["capacity"]) if a.get("memory") else None
            )
            for a in data["agents"]
        ]
        
        connections = [
            Connection(c["from"], c["to"], c.get("condition"))
            for c in data["connections"]
        ]
        
        return Workflow(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            agents=agents,
            connections=connections,
            entry_point=data["entry_point"],
            created_at=data.get("created_at", datetime.now().isoformat())
        )
    
    def export_visualization(self, workflow_id: str) -> str:
        """Export workflow as Mermaid diagram."""
        workflow = self.workflows[workflow_id]
        
        lines = ["```mermaid", "graph TD"]
        
        # Add agents
        for agent in workflow.agents:
            label = f"{agent.name}\\n[{agent.role.value}]"
            if agent.id == workflow.entry_point:
                lines.append(f"    {agent.id}[{label}]:::entry")
            else:
                lines.append(f"    {agent.id}[{label}]")
        
        # Add connections
        for conn in workflow.connections:
            if conn.condition:
                lines.append(f"    {conn.from_agent} -->|{conn.condition}| {conn.to_agent}")
            else:
                lines.append(f"    {conn.from_agent} --> {conn.to_agent}")
        
        lines.append("    classDef entry fill:#90EE90")
        lines.append("```")
        
        return "\n".join(lines)

def create_example_workflow():
    """Create example research workflow."""
    builder = WorkflowBuilder()
    
    # Create workflow
    workflow = builder.create_workflow(
        "Research & Write",
        "Multi-agent workflow for research and content creation"
    )
    
    # Add researcher agent
    researcher = builder.add_agent(
        workflow.id,
        "Researcher",
        AgentRole.RESEARCHER,
        "You are a research agent. Gather information and provide comprehensive findings.",
        tools=[Tool(ToolType.WEB_SEARCH, "web_search")],
        memory=Memory(MemoryType.SHORT_TERM, capacity=10)
    )
    
    # Add writer agent
    writer = builder.add_agent(
        workflow.id,
        "Writer",
        AgentRole.WRITER,
        "You are a writer. Create engaging content based on research findings.",
        memory=Memory(MemoryType.SHORT_TERM, capacity=5)
    )
    
    # Add critic agent
    critic = builder.add_agent(
        workflow.id,
        "Critic",
        AgentRole.CRITIC,
        "You are a critic. Review content and provide constructive feedback.",
        memory=Memory(MemoryType.SHARED)
    )
    
    # Connect agents
    builder.connect_agents(workflow.id, researcher.id, writer.id)
    builder.connect_agents(workflow.id, writer.id, critic.id)
    
    # Save
    builder.save_workflow(workflow.id)
    
    return workflow, builder

async def main():
    """Demo the workflow playground."""
    
    print("🎭 MULTI-AGENT WORKFLOW PLAYGROUND")
    print("=" * 70)
    print()
    
    # Create example workflow
    workflow, builder = create_example_workflow()
    
    print(f"📋 Created Workflow: {workflow.name}")
    print(f"   Description: {workflow.description}")
    print(f"   Agents: {len(workflow.agents)}")
    print(f"   Connections: {len(workflow.connections)}")
    print()
    
    # Show visualization
    print("📊 Workflow Visualization:")
    print(builder.export_visualization(workflow.id))
    print()
    
    # Execute workflow
    print("🚀 Executing workflow...")
    print()
    
    engine = WorkflowEngine()
    results = await engine.execute_workflow(
        workflow,
        "Research the benefits of multi-agent systems and write a brief summary"
    )
    
    # Display results
    print("📈 EXECUTION RESULTS:")
    print("=" * 70)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.agent_name} ({result.agent_id[:8]}...)")
        print(f"   Input: {result.input[:100]}...")
        print(f"   Output: {result.output[:200]}...")
        print(f"   Tools: {', '.join(result.tools_used) if result.tools_used else 'None'}")
        print(f"   Memory: {'Yes' if result.memory_accessed else 'No'}")
        print(f"   Time: {result.execution_time:.2f}s")
        if result.error:
            print(f"   ❌ Error: {result.error}")
    
    print("\n" + "=" * 70)
    print(f"✅ Workflow completed: {len(results)} agents executed")
    print(f"💾 Workflow saved to: workflows.json")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
