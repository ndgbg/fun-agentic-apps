#!/usr/bin/env python3
"""
Multi-Agent Workflow Playground
Visual builder and executor for multi-agent systems.

Each agent uses Anthropic's tool_use API to autonomously decide which tools
to call, react to results, and iterate until it has a final answer.
"""

import os
import io
import ast
import json
import uuid
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

# ---------------------------------------------------------------------------
# Data models (unchanged)
# ---------------------------------------------------------------------------

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
    model: str = "claude-sonnet-4-5-20250929"
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

# ---------------------------------------------------------------------------
# Anthropic tool schemas -- one per ToolType
# ---------------------------------------------------------------------------

TOOL_SCHEMAS: Dict[ToolType, dict] = {
    ToolType.WEB_SEARCH: {
        "name": "web_search",
        "description": (
            "Search the web for information. Returns a list of results with "
            "titles, URLs, and snippets. Use this when you need up-to-date "
            "information or facts you are not sure about."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to look up."
                }
            },
            "required": ["query"]
        }
    },
    ToolType.CALCULATOR: {
        "name": "calculator",
        "description": (
            "Evaluate a mathematical expression and return the numeric result. "
            "Supports standard Python math syntax: +, -, *, /, **, %, //, "
            "parentheses, and numeric literals (int and float)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate, e.g. '(3 + 4) * 2'."
                }
            },
            "required": ["expression"]
        }
    },
    ToolType.FILE_READER: {
        "name": "file_reader",
        "description": (
            "Read the contents of a file on the local filesystem. Returns up "
            "to the first 5000 characters of the file."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to read."
                }
            },
            "required": ["path"]
        }
    },
    ToolType.CODE_EXECUTOR: {
        "name": "code_executor",
        "description": (
            "Execute a snippet of Python code in a restricted namespace and "
            "return whatever the code prints to stdout. The namespace includes "
            "builtins for math, json, datetime, and re. If the code raises an "
            "exception the traceback is returned instead."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python source code to execute."
                }
            },
            "required": ["code"]
        }
    },
    ToolType.API_CALLER: {
        "name": "api_caller",
        "description": (
            "Make an HTTP request to an API endpoint and return the response. "
            "Supports GET and POST methods. Returns response body (up to 5000 "
            "characters), status code, and headers."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL to call."
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST"],
                    "description": "HTTP method. Defaults to GET."
                },
                "headers": {
                    "type": "object",
                    "description": "Optional HTTP headers as key/value pairs.",
                    "additionalProperties": {"type": "string"}
                },
                "body": {
                    "type": "string",
                    "description": "Optional request body (for POST requests)."
                }
            },
            "required": ["url"]
        }
    },
}

# ---------------------------------------------------------------------------
# WorkflowEngine -- now truly agentic
# ---------------------------------------------------------------------------

class WorkflowEngine:
    """Executes multi-agent workflows with full state tracking.

    Each agent runs an inner agentic loop: the LLM decides which tools to
    call (if any), results are fed back, and the loop continues until the
    model produces a final text response or the iteration cap is reached.
    """

    MAX_TOOL_ITERATIONS = 10

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

            result = await self._execute_agent(workflow, agent, current_input)
            results.append(result)

            if result.error:
                break

            next_agent = self._find_next_agent(workflow, current_agent_id, result)
            current_agent_id = next_agent
            current_input = result.output

        return results

    # ------------------------------------------------------------------
    # Core agentic execution loop
    # ------------------------------------------------------------------

    async def _execute_agent(self, workflow: Workflow, agent: Agent, input_text: str) -> ExecutionResult:
        """Execute a single agent with an inner agentic tool-use loop."""

        import anthropic
        import time

        start_time = time.time()
        tools_actually_used: List[str] = []

        try:
            client = anthropic.Anthropic(api_key=self.api_key)

            # Build context from memory
            context = self._build_context(agent, input_text)

            # Prepare the initial user message (no pre-executed tool results)
            user_prompt = self._build_prompt(agent, context, [], input_text)
            messages = [{"role": "user", "content": user_prompt}]

            # Convert the agent's Tool list into Anthropic tool schemas
            tools = self._get_agent_tools(agent)

            # Inner agentic loop -- up to MAX_TOOL_ITERATIONS rounds
            final_text = ""
            for _iteration in range(self.MAX_TOOL_ITERATIONS):
                response = client.messages.create(
                    model=agent.model,
                    max_tokens=2000,
                    temperature=agent.temperature,
                    system=agent.system_prompt,
                    tools=tools if tools else [],
                    messages=messages,
                )

                # Append the assistant turn
                messages.append({"role": "assistant", "content": response.content})

                # If the model stopped normally (no tool calls), we are done
                if response.stop_reason == "end_turn" or not tools:
                    # Extract all text blocks from the final response
                    text_parts = [
                        block.text for block in response.content
                        if hasattr(block, "text")
                    ]
                    final_text = "\n".join(text_parts)
                    break

                # If the model wants to use tools, execute them
                if response.stop_reason == "tool_use":
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            tools_actually_used.append(block.name)
                            result_str = await self._run_tool(block.name, block.input, agent)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(result_str),
                            })
                    messages.append({"role": "user", "content": tool_results})
                else:
                    # Unexpected stop reason -- extract text and break
                    text_parts = [
                        block.text for block in response.content
                        if hasattr(block, "text")
                    ]
                    final_text = "\n".join(text_parts)
                    break
            else:
                # If we exhausted iterations, grab whatever text the model last produced
                text_parts = [
                    block.text for block in response.content
                    if hasattr(block, "text")
                ]
                final_text = "\n".join(text_parts) or "[Agent reached maximum tool iterations]"

            # Update memory
            if agent.memory:
                self._update_memory(agent, input_text, final_text)

            execution_time = time.time() - start_time

            return ExecutionResult(
                workflow_id=workflow.id,
                agent_id=agent.id,
                agent_name=agent.name,
                input=input_text,
                output=final_text,
                tools_used=list(dict.fromkeys(tools_actually_used)),  # dedupe, preserve order
                memory_accessed=agent.memory is not None,
                execution_time=execution_time,
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            return ExecutionResult(
                workflow_id=workflow.id,
                agent_id=agent.id,
                agent_name=agent.name,
                input=input_text,
                output="",
                tools_used=list(dict.fromkeys(tools_actually_used)),
                memory_accessed=False,
                execution_time=time.time() - start_time,
                timestamp=datetime.now().isoformat(),
                error=str(e),
            )

    # ------------------------------------------------------------------
    # Tool schema conversion
    # ------------------------------------------------------------------

    def _get_agent_tools(self, agent: Agent) -> List[dict]:
        """Convert an agent's Tool objects into Anthropic API tool schemas."""
        schemas = []
        for tool in agent.tools:
            schema = TOOL_SCHEMAS.get(tool.type)
            if schema:
                schemas.append(schema)
        return schemas

    # ------------------------------------------------------------------
    # Tool dispatcher
    # ------------------------------------------------------------------

    async def _run_tool(self, tool_name: str, tool_input: dict, agent: Agent) -> str:
        """Dispatch a tool call to the appropriate implementation."""
        try:
            if tool_name == "web_search":
                return await self._web_search(tool_input.get("query", ""))
            elif tool_name == "calculator":
                return self._calculator(tool_input.get("expression", ""))
            elif tool_name == "file_reader":
                return self._file_reader(tool_input.get("path", ""))
            elif tool_name == "code_executor":
                return self._code_executor(tool_input.get("code", ""))
            elif tool_name == "api_caller":
                return await self._api_caller(
                    url=tool_input.get("url", ""),
                    method=tool_input.get("method", "GET"),
                    headers=tool_input.get("headers"),
                    body=tool_input.get("body"),
                )
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            return f"Tool error ({tool_name}): {e}"

    # ------------------------------------------------------------------
    # Real tool implementations
    # ------------------------------------------------------------------

    async def _web_search(self, query: str) -> str:
        """Perform a web search using DuckDuckGo HTML and return results.

        Uses DuckDuckGo's HTML endpoint which does not require an API key.
        Falls back to a structured simulated result if the request fails.
        """
        if not query:
            return "Error: empty search query."

        try:
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; AgentWorkflow/1.0)"
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            # Lightweight HTML parsing -- extract result snippets
            results = []
            # DuckDuckGo HTML results live in <a class="result__a"> and
            # <a class="result__snippet"> blocks.  We do a rough parse.
            import re
            # Titles + URLs
            titles = re.findall(r'class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>', html, re.DOTALL)
            snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|span|td)', html, re.DOTALL)

            for i, (href, raw_title) in enumerate(titles[:5]):
                title = re.sub(r'<[^>]+>', '', raw_title).strip()
                snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ""
                results.append(f"{i+1}. {title}\n   URL: {href}\n   {snippet}")

            if results:
                return f"Search results for '{query}':\n\n" + "\n\n".join(results)

            # If parsing yielded nothing, return a note
            return (
                f"Search for '{query}' returned results but parsing failed. "
                "Raw page length: {len(html)} chars."
            )

        except Exception as e:
            # Fallback: return structured simulated results so the agent
            # still has something useful to reason about.
            return (
                f"Web search for '{query}' (simulated -- live search failed: {e}):\n"
                f"1. Wikipedia - {query}\n"
                f"   URL: https://en.wikipedia.org/wiki/{urllib.parse.quote(query)}\n"
                f"   Comprehensive encyclopedia article covering {query}.\n\n"
                f"2. Recent article - {query} explained\n"
                f"   URL: https://example.com/articles/{urllib.parse.quote_plus(query)}\n"
                f"   An in-depth explanation of {query} with examples.\n\n"
                f"3. Research paper - Advances in {query}\n"
                f"   URL: https://arxiv.org/search/?query={urllib.parse.quote_plus(query)}\n"
                f"   Academic research on the latest developments in {query}."
            )

    def _calculator(self, expression: str) -> str:
        """Safely evaluate a mathematical expression.

        Uses ast.parse to validate the expression contains only numeric
        literals and basic math operators before evaluating.
        """
        if not expression:
            return "Error: empty expression."

        try:
            # Parse the expression into an AST and verify safety
            tree = ast.parse(expression, mode="eval")
            # Walk the AST and allow only safe node types
            allowed_nodes = (
                ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
                ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv,
                ast.Mod, ast.Pow, ast.USub, ast.UAdd,
            )
            for node in ast.walk(tree):
                if not isinstance(node, allowed_nodes):
                    return f"Error: disallowed expression element: {type(node).__name__}"

            # Safe to eval
            code = compile(tree, "<calculator>", "eval")
            result = eval(code, {"__builtins__": {}})
            return f"{result}"

        except SyntaxError as e:
            return f"Syntax error in expression: {e}"
        except ZeroDivisionError:
            return "Error: division by zero."
        except Exception as e:
            return f"Calculation error: {e}"

    def _file_reader(self, path: str) -> str:
        """Read file content."""
        if not path:
            return "Error: no file path provided."
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    content = f.read(5000)  # First 5000 chars
                truncated = " [truncated]" if len(content) == 5000 else ""
                return f"Contents of {path}{truncated}:\n{content}"
            else:
                return f"File not found: {path}"
        except Exception as e:
            return f"Error reading {path}: {e}"

    def _code_executor(self, code: str) -> str:
        """Execute Python code in a restricted namespace.

        The code has access to a limited set of safe builtins and modules:
        math, json, datetime, re, collections, itertools.
        Whatever the code prints to stdout is captured and returned.
        """
        if not code:
            return "Error: no code provided."

        import math
        import re as re_module
        import collections
        import itertools

        # Build a restricted namespace
        safe_builtins = {
            "abs": abs, "all": all, "any": any, "bin": bin,
            "bool": bool, "chr": chr, "dict": dict, "divmod": divmod,
            "enumerate": enumerate, "filter": filter, "float": float,
            "format": format, "frozenset": frozenset, "hash": hash,
            "hex": hex, "int": int, "isinstance": isinstance,
            "issubclass": issubclass, "iter": iter, "len": len,
            "list": list, "map": map, "max": max, "min": min,
            "next": next, "oct": oct, "ord": ord, "pow": pow,
            "print": print, "range": range, "repr": repr,
            "reversed": reversed, "round": round, "set": set,
            "slice": slice, "sorted": sorted, "str": str,
            "sum": sum, "tuple": tuple, "type": type, "zip": zip,
        }

        namespace = {
            "__builtins__": safe_builtins,
            "math": math,
            "json": json,
            "datetime": datetime,
            "re": re_module,
            "collections": collections,
            "itertools": itertools,
        }

        # Capture stdout
        captured = io.StringIO()
        import sys
        old_stdout = sys.stdout
        try:
            sys.stdout = captured
            exec(code, namespace)
        except Exception as e:
            return f"Execution error: {type(e).__name__}: {e}"
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        if not output:
            return "(code executed successfully with no output)"
        return output[:5000]

    async def _api_caller(self, url: str, method: str = "GET",
                          headers: Optional[Dict[str, str]] = None,
                          body: Optional[str] = None) -> str:
        """Make an HTTP request and return the response."""
        if not url:
            return "Error: no URL provided."

        try:
            data = body.encode("utf-8") if body else None
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header("User-Agent", "AgentWorkflow/1.0")
            if headers:
                for k, v in headers.items():
                    req.add_header(k, v)

            with urllib.request.urlopen(req, timeout=15) as resp:
                resp_body = resp.read().decode("utf-8", errors="replace")[:5000]
                status = resp.status
                resp_headers = dict(resp.getheaders())

            return json.dumps({
                "status": status,
                "headers": resp_headers,
                "body": resp_body,
            }, indent=2)

        except urllib.error.HTTPError as e:
            body_text = ""
            try:
                body_text = e.read().decode("utf-8", errors="replace")[:2000]
            except Exception:
                pass
            return json.dumps({
                "error": f"HTTP {e.code}: {e.reason}",
                "body": body_text,
            }, indent=2)
        except Exception as e:
            return f"API call error: {e}"

    # ------------------------------------------------------------------
    # Prompt & context helpers
    # ------------------------------------------------------------------

    def _build_context(self, agent: Agent, input_text: str) -> str:
        """Build context from agent memory."""
        if not agent.memory:
            return ""

        if agent.memory.type == MemoryType.SHORT_TERM:
            memory = self.agent_memories.get(agent.id, [])
            return "\n".join(memory[-5:])
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

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------

    def _update_memory(self, agent: Agent, input_text: str, output: str):
        """Update agent memory."""
        memory_entry = f"Input: {input_text}\nOutput: {output}"

        if agent.memory.type == MemoryType.SHORT_TERM:
            if agent.id not in self.agent_memories:
                self.agent_memories[agent.id] = []
            self.agent_memories[agent.id].append(memory_entry)

            if len(self.agent_memories[agent.id]) > agent.memory.capacity:
                self.agent_memories[agent.id] = self.agent_memories[agent.id][-agent.memory.capacity:]

        elif agent.memory.type == MemoryType.SHARED:
            key = f"{agent.id}_{datetime.now().timestamp()}"
            self.shared_memory[key] = memory_entry

    # ------------------------------------------------------------------
    # Workflow navigation
    # ------------------------------------------------------------------

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
                if conn.condition:
                    if self._evaluate_condition(conn.condition, result):
                        return conn.to_agent
                else:
                    return conn.to_agent
        return None

    def _evaluate_condition(self, condition: str, result: ExecutionResult) -> bool:
        """Evaluate transition condition."""
        if "success" in condition.lower():
            return result.error is None
        if "error" in condition.lower():
            return result.error is not None
        return True


# ---------------------------------------------------------------------------
# WorkflowBuilder (unchanged)
# ---------------------------------------------------------------------------

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

        workflows_data = {}
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                workflows_data = json.load(f)

        workflows_data[workflow_id] = self._serialize_workflow(workflow)

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
                model=a.get("model", "claude-sonnet-4-5-20250929"),
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

        for agent in workflow.agents:
            label = f"{agent.name}\\n[{agent.role.value}]"
            if agent.id == workflow.entry_point:
                lines.append(f"    {agent.id}[{label}]:::entry")
            else:
                lines.append(f"    {agent.id}[{label}]")

        for conn in workflow.connections:
            if conn.condition:
                lines.append(f"    {conn.from_agent} -->|{conn.condition}| {conn.to_agent}")
            else:
                lines.append(f"    {conn.from_agent} --> {conn.to_agent}")

        lines.append("    classDef entry fill:#90EE90")
        lines.append("```")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Example workflow
# ---------------------------------------------------------------------------

def create_example_workflow():
    """Create example research workflow with real tools."""
    builder = WorkflowBuilder()

    workflow = builder.create_workflow(
        "Research & Analyze",
        "Multi-agent workflow: research a topic, run calculations, and produce a written analysis"
    )

    # Researcher agent -- has web_search and api_caller
    researcher = builder.add_agent(
        workflow.id,
        "Researcher",
        AgentRole.RESEARCHER,
        (
            "You are a research agent. Your job is to gather information about "
            "the given topic using the tools at your disposal. Use web_search to "
            "find relevant information. Synthesize your findings into a clear, "
            "factual research brief that the next agent can build upon."
        ),
        tools=[
            Tool(ToolType.WEB_SEARCH, "web_search"),
            Tool(ToolType.CALCULATOR, "calculator"),
        ],
        memory=Memory(MemoryType.SHORT_TERM, capacity=10),
    )

    # Writer agent -- has calculator and code_executor for any data work
    writer = builder.add_agent(
        workflow.id,
        "Writer",
        AgentRole.WRITER,
        (
            "You are an expert writer and analyst. You receive research findings "
            "from a researcher agent. Your job is to transform those findings "
            "into a well-structured, engaging written analysis. If you need to "
            "compute statistics or process data, use the calculator or "
            "code_executor tools. Produce a polished final piece."
        ),
        tools=[
            Tool(ToolType.CALCULATOR, "calculator"),
            Tool(ToolType.CODE_EXECUTOR, "code_executor"),
        ],
        memory=Memory(MemoryType.SHORT_TERM, capacity=5),
    )

    # Critic agent -- no tools, just reviews
    critic = builder.add_agent(
        workflow.id,
        "Critic",
        AgentRole.CRITIC,
        (
            "You are a constructive critic. You receive a written analysis and "
            "provide detailed feedback: factual accuracy, logical coherence, "
            "writing quality, and suggestions for improvement. Be specific and "
            "actionable in your critique."
        ),
        memory=Memory(MemoryType.SHARED),
    )

    # Connect: Researcher -> Writer -> Critic
    builder.connect_agents(workflow.id, researcher.id, writer.id)
    builder.connect_agents(workflow.id, writer.id, critic.id)

    builder.save_workflow(workflow.id)

    return workflow, builder


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    """Demo the agentic workflow playground."""

    print("MULTI-AGENT WORKFLOW PLAYGROUND (Agentic)")
    print("=" * 70)
    print()

    workflow, builder = create_example_workflow()

    print(f"Workflow: {workflow.name}")
    print(f"  Description: {workflow.description}")
    print(f"  Agents: {len(workflow.agents)}")
    print(f"  Connections: {len(workflow.connections)}")
    print()

    # Show visualization
    print("Workflow Visualization:")
    print(builder.export_visualization(workflow.id))
    print()

    # Execute workflow
    print("Executing workflow...")
    print("-" * 70)
    print()

    engine = WorkflowEngine()
    results = await engine.execute_workflow(
        workflow,
        "Research the current state of multi-agent AI systems: key architectures, "
        "benefits, and challenges. Then write a concise but informative summary."
    )

    # Display results
    print()
    print("EXECUTION RESULTS:")
    print("=" * 70)

    for i, result in enumerate(results, 1):
        status = "OK" if not result.error else "ERROR"
        print(f"\n--- Agent {i}: {result.agent_name} [{status}] ---")
        print(f"  Time: {result.execution_time:.2f}s")
        print(f"  Tools used: {', '.join(result.tools_used) if result.tools_used else 'None'}")
        print(f"  Memory accessed: {'Yes' if result.memory_accessed else 'No'}")
        if result.error:
            print(f"  Error: {result.error}")
        else:
            # Print output, truncating if very long
            output = result.output
            if len(output) > 1000:
                output = output[:1000] + f"\n  ... [truncated, {len(result.output)} chars total]"
            print(f"  Output:\n{output}")

    print("\n" + "=" * 70)
    print(f"Workflow completed: {len(results)} agents executed")
    total_time = sum(r.execution_time for r in results)
    print(f"Total execution time: {total_time:.2f}s")
    all_tools = []
    for r in results:
        all_tools.extend(r.tools_used)
    if all_tools:
        print(f"All tools invoked: {', '.join(dict.fromkeys(all_tools))}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
