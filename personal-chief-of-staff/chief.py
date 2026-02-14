#!/usr/bin/env python3
"""
Personal Chief of Staff
Agentic AI that proactively manages your life operations using tool-use.
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import anthropic

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"

@dataclass
class Task:
    id: str
    title: str
    description: str
    priority: Priority
    status: TaskStatus
    deadline: Optional[str]
    estimated_hours: float
    dependencies: List[str]
    context: str
    created_at: str
    completed_at: Optional[str] = None

@dataclass
class Goal:
    id: str
    title: str
    description: str
    target_date: str
    progress: float  # 0.0 to 1.0
    milestones: List[str]
    related_tasks: List[str]
    created_at: str

@dataclass
class ContextSwitch:
    from_task: str
    to_task: str
    reason: str
    timestamp: str
    cost_minutes: int

@dataclass
class DailyBriefing:
    date: str
    summary: str
    top_priorities: List[str]
    deadline_warnings: List[Dict[str, Any]]
    suggested_focus: str
    time_allocation: Dict[str, float]
    blockers: List[str]
    wins_yesterday: List[str]
    generated_at: str

class MemorySystem:
    """Long-term memory for context and patterns."""

    def __init__(self):
        self.working_patterns = {}  # When you work best
        self.task_history = []
        self.context_switches = []
        self.preferences = {}
        self.energy_levels = {}  # Time of day -> energy

    def record_task_completion(self, task: Task, actual_hours: float):
        """Learn from completed tasks."""
        self.task_history.append({
            "task_id": task.id,
            "estimated": task.estimated_hours,
            "actual": actual_hours,
            "priority": task.priority.value,
            "completed_at": datetime.now().isoformat()
        })

    def record_context_switch(self, switch: ContextSwitch):
        """Track context switching costs."""
        self.context_switches.append(switch)

    def get_estimation_accuracy(self) -> float:
        """How accurate are time estimates?"""
        if not self.task_history:
            return 1.0

        ratios = [h["actual"] / h["estimated"] for h in self.task_history if h["estimated"] > 0]
        return sum(ratios) / len(ratios) if ratios else 1.0

    def get_best_work_times(self) -> List[str]:
        """When do you complete most tasks?"""
        if not self.task_history:
            return ["09:00-12:00", "14:00-17:00"]

        # Analyze completion times
        hours = [datetime.fromisoformat(h["completed_at"]).hour for h in self.task_history]

        # Find peak hours
        from collections import Counter
        common = Counter(hours).most_common(3)

        return [f"{h:02d}:00-{h+1:02d}:00" for h, _ in common]

    def get_context_switch_cost(self) -> int:
        """Average cost of context switching in minutes."""
        if not self.context_switches:
            return 15  # Default

        return sum(cs.cost_minutes for cs in self.context_switches) // len(self.context_switches)

class DeadlineMonitor:
    """Proactive deadline monitoring and warnings."""

    def __init__(self):
        self.warning_thresholds = {
            Priority.CRITICAL: 24,  # hours
            Priority.HIGH: 48,
            Priority.MEDIUM: 72,
            Priority.LOW: 168
        }

    def check_deadlines(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Check for approaching deadlines."""

        warnings = []
        now = datetime.now()

        for task in tasks:
            if not task.deadline or task.status == TaskStatus.DONE:
                continue

            deadline = datetime.fromisoformat(task.deadline)
            hours_until = (deadline - now).total_seconds() / 3600

            threshold = self.warning_thresholds.get(task.priority, 72)

            if hours_until < threshold:
                urgency = "CRITICAL" if hours_until < 24 else "WARNING"
                warnings.append({
                    "task_id": task.id,
                    "title": task.title,
                    "deadline": task.deadline,
                    "hours_remaining": hours_until,
                    "urgency": urgency,
                    "estimated_hours": task.estimated_hours,
                    "can_complete": hours_until > task.estimated_hours
                })

        return sorted(warnings, key=lambda x: x["hours_remaining"])


class ChiefOfStaff:
    """Main agentic orchestrator using Anthropic tool-use API."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.memory = MemorySystem()
        self.deadline_monitor = DeadlineMonitor()

        self.tasks: List[Task] = []
        self.goals: List[Goal] = []
        self.last_briefing: Optional[DailyBriefing] = None

        self.system_prompt = (
            "You are a Chief of Staff AI. You proactively manage tasks, goals, "
            "deadlines, and focus. You have tools to inspect and modify tasks/goals, "
            "check deadlines, and query the user's work patterns from memory. "
            "When asked for a briefing, gather data using tools and synthesize. "
            "When asked for focus advice, check current tasks, deadlines, energy "
            "patterns, and context switch costs before recommending. "
            "Be decisive and specific."
        )

    # ------------------------------------------------------------------
    # Tool definitions
    # ------------------------------------------------------------------

    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return Anthropic tool schemas for the agent."""
        return [
            {
                "name": "list_tasks",
                "description": (
                    "List all tasks. Optionally filter by status. "
                    "Returns a JSON array of task objects with id, title, description, "
                    "priority, status, deadline, estimated_hours, dependencies, context, "
                    "created_at, and completed_at."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "description": "Filter by status: todo, in_progress, blocked, done. Omit to list all.",
                            "enum": ["todo", "in_progress", "blocked", "done"]
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "add_task",
                "description": (
                    "Add a new task. Returns the created task object."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Short task title."
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed task description."
                        },
                        "priority": {
                            "type": "string",
                            "description": "Task priority level.",
                            "enum": ["critical", "high", "medium", "low"]
                        },
                        "deadline": {
                            "type": "string",
                            "description": "ISO-format deadline string. Optional."
                        },
                        "estimated_hours": {
                            "type": "number",
                            "description": "Estimated hours to complete. Defaults to 1.0."
                        },
                        "dependencies": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of task IDs this task depends on."
                        }
                    },
                    "required": ["title", "description", "priority"]
                }
            },
            {
                "name": "complete_task",
                "description": (
                    "Mark a task as done and record actual hours spent. "
                    "This also updates related goal progress and feeds the memory system."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "ID of the task to complete."
                        },
                        "actual_hours": {
                            "type": "number",
                            "description": "Actual hours spent on the task."
                        }
                    },
                    "required": ["task_id", "actual_hours"]
                }
            },
            {
                "name": "list_goals",
                "description": (
                    "List all goals. Returns a JSON array of goal objects with id, "
                    "title, description, target_date, progress, milestones, "
                    "related_tasks, and created_at."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "add_goal",
                "description": "Add a new goal. Returns the created goal object.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Short goal title."
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed goal description."
                        },
                        "target_date": {
                            "type": "string",
                            "description": "Target completion date (YYYY-MM-DD)."
                        },
                        "milestones": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of milestone descriptions."
                        }
                    },
                    "required": ["title", "description", "target_date"]
                }
            },
            {
                "name": "check_deadlines",
                "description": (
                    "Check for approaching deadlines across all tasks. "
                    "Returns a sorted list of deadline warnings with urgency levels."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "query_memory",
                "description": (
                    "Query the memory system for task completion history. "
                    "Returns estimation accuracy ratio, recent task history entries, "
                    "and stored preferences."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_work_patterns",
                "description": (
                    "Get the user's work patterns including best work times, "
                    "average context switch cost, estimation accuracy, and "
                    "current energy level estimate based on time of day."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "record_context_switch",
                "description": (
                    "Record a context switch between tasks to track productivity costs."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "from_task": {
                            "type": "string",
                            "description": "Task ID or description of the task switched from."
                        },
                        "to_task": {
                            "type": "string",
                            "description": "Task ID or description of the task switched to."
                        },
                        "reason": {
                            "type": "string",
                            "description": "Why the switch happened."
                        },
                        "cost_minutes": {
                            "type": "integer",
                            "description": "Estimated minutes lost to the switch."
                        }
                    },
                    "required": ["from_task", "to_task", "reason", "cost_minutes"]
                }
            }
        ]

    # ------------------------------------------------------------------
    # Tool execution dispatcher
    # ------------------------------------------------------------------

    def _execute_tool(self, name: str, tool_input: Dict[str, Any]) -> Any:
        """Dispatch a tool call to the matching implementation."""

        if name == "list_tasks":
            status_filter = tool_input.get("status")
            tasks = self.tasks
            if status_filter:
                tasks = [t for t in tasks if t.status.value == status_filter]
            return [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority.value,
                    "status": t.status.value,
                    "deadline": t.deadline,
                    "estimated_hours": t.estimated_hours,
                    "dependencies": t.dependencies,
                    "context": t.context,
                    "created_at": t.created_at,
                    "completed_at": t.completed_at
                }
                for t in tasks
            ]

        elif name == "add_task":
            task = self.add_task(
                title=tool_input["title"],
                description=tool_input["description"],
                priority=Priority(tool_input["priority"]),
                deadline=tool_input.get("deadline"),
                estimated_hours=tool_input.get("estimated_hours", 1.0),
                dependencies=tool_input.get("dependencies")
            )
            return {
                "id": task.id,
                "title": task.title,
                "priority": task.priority.value,
                "status": task.status.value,
                "deadline": task.deadline,
                "estimated_hours": task.estimated_hours,
                "created_at": task.created_at
            }

        elif name == "complete_task":
            task_id = tool_input["task_id"]
            actual_hours = tool_input["actual_hours"]
            task = next((t for t in self.tasks if t.id == task_id), None)
            if not task:
                return {"error": f"Task '{task_id}' not found."}
            self.complete_task(task_id, actual_hours)
            return {
                "task_id": task_id,
                "title": task.title,
                "status": task.status.value,
                "completed_at": task.completed_at,
                "actual_hours": actual_hours
            }

        elif name == "list_goals":
            return [
                {
                    "id": g.id,
                    "title": g.title,
                    "description": g.description,
                    "target_date": g.target_date,
                    "progress": g.progress,
                    "milestones": g.milestones,
                    "related_tasks": g.related_tasks,
                    "created_at": g.created_at
                }
                for g in self.goals
            ]

        elif name == "add_goal":
            goal = self.add_goal(
                title=tool_input["title"],
                description=tool_input["description"],
                target_date=tool_input["target_date"],
                milestones=tool_input.get("milestones")
            )
            return {
                "id": goal.id,
                "title": goal.title,
                "target_date": goal.target_date,
                "progress": goal.progress,
                "created_at": goal.created_at
            }

        elif name == "check_deadlines":
            return self.deadline_monitor.check_deadlines(self.tasks)

        elif name == "query_memory":
            return {
                "estimation_accuracy": self.memory.get_estimation_accuracy(),
                "task_history": self.memory.task_history[-20:],  # last 20
                "preferences": self.memory.preferences
            }

        elif name == "get_work_patterns":
            now = datetime.now()
            hour = now.hour
            if 9 <= hour < 12:
                energy = "high"
            elif 14 <= hour < 17:
                energy = "medium-high"
            elif 17 <= hour < 20:
                energy = "medium"
            else:
                energy = "low"
            return {
                "current_time": now.strftime("%A %H:%M"),
                "best_work_times": self.memory.get_best_work_times(),
                "context_switch_cost_minutes": self.memory.get_context_switch_cost(),
                "estimation_accuracy": self.memory.get_estimation_accuracy(),
                "current_energy_estimate": energy
            }

        elif name == "record_context_switch":
            switch = ContextSwitch(
                from_task=tool_input["from_task"],
                to_task=tool_input["to_task"],
                reason=tool_input["reason"],
                timestamp=datetime.now().isoformat(),
                cost_minutes=tool_input["cost_minutes"]
            )
            self.memory.record_context_switch(switch)
            return {
                "recorded": True,
                "from_task": switch.from_task,
                "to_task": switch.to_task,
                "cost_minutes": switch.cost_minutes
            }

        else:
            return {"error": f"Unknown tool: {name}"}

    # ------------------------------------------------------------------
    # Agentic loop
    # ------------------------------------------------------------------

    async def run(self, request: str, max_iterations: int = 15) -> str:
        """Run the agentic loop: the LLM decides which tools to call."""

        messages = [{"role": "user", "content": request}]

        for i in range(max_iterations):
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=self.system_prompt,
                tools=self._get_tool_definitions(),
                messages=messages
            )

            # Append the assistant's reply (may contain text + tool_use blocks)
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                break

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self._execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, default=str)
                        })
                messages.append({"role": "user", "content": tool_results})

        # Extract the final text response
        final_text = ""
        for block in response.content:
            if hasattr(block, "text"):
                final_text += block.text

        return final_text

    # ------------------------------------------------------------------
    # Direct API methods (also used as tool implementations)
    # ------------------------------------------------------------------

    def add_task(self, title: str, description: str, priority: Priority,
                 deadline: str = None, estimated_hours: float = 1.0,
                 dependencies: List[str] = None) -> Task:
        """Add new task."""

        task = Task(
            id=f"task_{len(self.tasks) + 1}",
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.TODO,
            deadline=deadline,
            estimated_hours=estimated_hours,
            dependencies=dependencies or [],
            context="",
            created_at=datetime.now().isoformat()
        )

        self.tasks.append(task)
        return task

    def add_goal(self, title: str, description: str, target_date: str,
                 milestones: List[str] = None) -> Goal:
        """Add new goal."""

        goal = Goal(
            id=f"goal_{len(self.goals) + 1}",
            title=title,
            description=description,
            target_date=target_date,
            progress=0.0,
            milestones=milestones or [],
            related_tasks=[],
            created_at=datetime.now().isoformat()
        )

        self.goals.append(goal)
        return goal

    def complete_task(self, task_id: str, actual_hours: float):
        """Mark task complete and learn."""

        task = next((t for t in self.tasks if t.id == task_id), None)
        if not task:
            return

        task.status = TaskStatus.DONE
        task.completed_at = datetime.now().isoformat()

        # Learn from completion
        self.memory.record_task_completion(task, actual_hours)

        # Update related goals
        for goal in self.goals:
            if task_id in goal.related_tasks:
                done_tasks = [
                    t_id for t_id in goal.related_tasks
                    if any(x.id == t_id and x.status == TaskStatus.DONE for x in self.tasks)
                ]
                goal.progress = len(done_tasks) / len(goal.related_tasks) if goal.related_tasks else 0.0

    # ------------------------------------------------------------------
    # High-level operations now powered by the agentic loop
    # ------------------------------------------------------------------

    async def generate_daily_briefing(self) -> str:
        """Generate proactive daily briefing via the agentic loop."""

        print("Generating daily briefing...\n")

        result = await self.run(
            "Generate my daily briefing. Check all tasks, deadlines, and my "
            "work patterns to create a comprehensive briefing."
        )

        print("=" * 70)
        print("DAILY BRIEFING")
        print("=" * 70)
        print(result)
        print("=" * 70)

        return result

    async def what_should_i_focus_on(self, context: str = "") -> str:
        """Answer the key question via the agentic loop."""

        print("\nAnalyzing current situation...\n")

        result = await self.run(
            f"What should I focus on right now? Context: {context}"
        )

        print("=" * 70)
        print("FOCUS RECOMMENDATION")
        print("=" * 70)
        print(result)
        print("=" * 70)

        return result

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_state(self, filepath: str = "chief_of_staff_state.json"):
        """Save state for persistence."""

        state = {
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority.value,
                    "status": t.status.value,
                    "deadline": t.deadline,
                    "estimated_hours": t.estimated_hours,
                    "dependencies": t.dependencies,
                    "context": t.context,
                    "created_at": t.created_at,
                    "completed_at": t.completed_at
                }
                for t in self.tasks
            ],
            "goals": [
                {
                    "id": g.id,
                    "title": g.title,
                    "description": g.description,
                    "target_date": g.target_date,
                    "progress": g.progress,
                    "milestones": g.milestones,
                    "related_tasks": g.related_tasks,
                    "created_at": g.created_at
                }
                for g in self.goals
            ],
            "memory": {
                "task_history": self.memory.task_history,
                "context_switches": [asdict(cs) for cs in self.memory.context_switches],
                "preferences": self.memory.preferences
            }
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        print(f"\nState saved to {filepath}")


async def main():
    """Demo the agentic Chief of Staff."""

    print("PERSONAL CHIEF OF STAFF")
    print("=" * 70)
    print("Agentic AI managing your life operations via tool-use")
    print("=" * 70)

    chief = ChiefOfStaff()

    # Add some goals
    print("\nSetting up goals...")

    chief.add_goal(
        "Launch new product",
        "Complete MVP and launch to first customers",
        "2026-03-15",
        ["Complete design", "Build MVP", "Get 10 beta users"]
    )

    chief.add_goal(
        "Improve health",
        "Exercise 3x/week and improve diet",
        "2026-06-01",
        ["Join gym", "Meal prep routine", "Track progress"]
    )

    print(f"  Added {len(chief.goals)} goals")

    # Add tasks
    print("\nAdding tasks...")

    chief.add_task(
        "Finish product spec",
        "Complete technical specification for MVP",
        Priority.HIGH,
        deadline=(datetime.now() + timedelta(days=2)).isoformat(),
        estimated_hours=4.0
    )

    chief.add_task(
        "Review design mockups",
        "Provide feedback on UI designs",
        Priority.MEDIUM,
        deadline=(datetime.now() + timedelta(days=1)).isoformat(),
        estimated_hours=2.0
    )

    chief.add_task(
        "Schedule team meeting",
        "Coordinate calendars for sprint planning",
        Priority.HIGH,
        deadline=(datetime.now() + timedelta(hours=6)).isoformat(),
        estimated_hours=0.5
    )

    chief.add_task(
        "Research competitors",
        "Analyze top 3 competitors' features",
        Priority.MEDIUM,
        estimated_hours=3.0
    )

    chief.add_task(
        "Update investors",
        "Send monthly progress update",
        Priority.LOW,
        deadline=(datetime.now() + timedelta(days=5)).isoformat(),
        estimated_hours=1.0
    )

    print(f"  Added {len(chief.tasks)} tasks")

    # Generate daily briefing via agentic loop
    print("\n" + "=" * 70)
    await chief.generate_daily_briefing()

    # Ask for focus recommendation via agentic loop
    await chief.what_should_i_focus_on(
        "Just finished a meeting, have 2 hours before lunch"
    )

    # Interactive conversation loop
    print("\n" + "=" * 70)
    print("INTERACTIVE MODE")
    print("Type your requests (or 'quit' to exit):")
    print("=" * 70)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input or user_input.lower() in ("quit", "exit", "q"):
            break

        result = await chief.run(user_input)
        print(f"\nChief of Staff:\n{result}")

    # Save state
    chief.save_state()

    print("\n" + "=" * 70)
    print("Chief of Staff session complete.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
