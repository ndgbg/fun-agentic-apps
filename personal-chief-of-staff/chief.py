#!/usr/bin/env python3
"""
Personal Chief of Staff
Autonomous AI that proactively manages your life operations.
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

class PriorityEngine:
    """Autonomous priority ranking based on multiple factors."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def rank_tasks(self, tasks: List[Task], goals: List[Goal], 
                        memory: MemorySystem, current_time: datetime) -> List[Task]:
        """Intelligently re-rank tasks based on context."""
        
        # Build context
        context = self._build_context(tasks, goals, memory, current_time)
        
        prompt = f"""You are a Chief of Staff. Analyze these tasks and re-rank them by true priority.

Current Context:
{context}

Tasks:
{self._format_tasks(tasks)}

Goals:
{self._format_goals(goals)}

Consider:
1. Deadlines (urgent vs important)
2. Goal alignment
3. Dependencies
4. Energy levels (current time: {current_time.strftime('%H:%M')})
5. Context switching costs
6. Estimated effort

Return JSON array of task IDs in priority order with reasoning:
{{
  "ranking": [
    {{"task_id": "task_1", "reason": "Critical deadline tomorrow, blocks 3 other tasks"}},
    {{"task_id": "task_2", "reason": "High-impact, aligns with Q1 goal"}}
  ]
}}"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        # Extract JSON
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            ranking_data = json.loads(json_match.group())
        else:
            ranking_data = json.loads(response_text)
        
        # Re-order tasks
        task_map = {t.id: t for t in tasks}
        ranked_tasks = []
        
        for item in ranking_data["ranking"]:
            task_id = item["task_id"]
            if task_id in task_map:
                task = task_map[task_id]
                # Store reasoning
                task.context = item["reason"]
                ranked_tasks.append(task)
        
        return ranked_tasks
    
    def _build_context(self, tasks: List[Task], goals: List[Goal], 
                      memory: MemorySystem, current_time: datetime) -> str:
        """Build context for ranking."""
        
        best_times = memory.get_best_work_times()
        switch_cost = memory.get_context_switch_cost()
        
        return f"""
- Current time: {current_time.strftime('%A %H:%M')}
- Your best work times: {', '.join(best_times)}
- Context switch cost: {switch_cost} minutes
- Active goals: {len(goals)}
- Pending tasks: {len([t for t in tasks if t.status == TaskStatus.TODO])}
"""
    
    def _format_tasks(self, tasks: List[Task]) -> str:
        """Format tasks for prompt."""
        lines = []
        for t in tasks:
            deadline_str = f"Deadline: {t.deadline}" if t.deadline else "No deadline"
            lines.append(f"- {t.id}: {t.title} | {t.priority.value} | {deadline_str} | {t.estimated_hours}h")
        return "\n".join(lines)
    
    def _format_goals(self, goals: List[Goal]) -> str:
        """Format goals for prompt."""
        lines = []
        for g in goals:
            lines.append(f"- {g.title} (Target: {g.target_date}, Progress: {g.progress*100:.0f}%)")
        return "\n".join(lines)

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

class BriefingGenerator:
    """Generates proactive daily briefings."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def generate_briefing(self, tasks: List[Task], goals: List[Goal],
                               memory: MemorySystem, warnings: List[Dict]) -> DailyBriefing:
        """Generate comprehensive daily briefing."""
        
        # Get yesterday's completions
        yesterday = datetime.now() - timedelta(days=1)
        wins = [t for t in tasks if t.completed_at and 
                datetime.fromisoformat(t.completed_at) > yesterday]
        
        # Identify blockers
        blockers = [t for t in tasks if t.status == TaskStatus.BLOCKED]
        
        # Build context
        context = f"""
Tasks: {len(tasks)} total, {len([t for t in tasks if t.status == TaskStatus.TODO])} pending
Goals: {len(goals)} active
Wins yesterday: {len(wins)}
Blockers: {len(blockers)}
Deadline warnings: {len(warnings)}
Best work times: {', '.join(memory.get_best_work_times())}
"""

        prompt = f"""You are a Chief of Staff preparing a daily briefing.

Context:
{context}

Top Priority Tasks:
{self._format_tasks(tasks[:5])}

Deadline Warnings:
{self._format_warnings(warnings)}

Goals:
{self._format_goals(goals)}

Create a concise daily briefing with:
1. Executive summary (2-3 sentences)
2. Top 3 priorities for today
3. Suggested focus area
4. Time allocation recommendation
5. Key blockers to address

Return JSON:
{{
  "summary": "Brief overview",
  "top_priorities": ["Priority 1", "Priority 2", "Priority 3"],
  "suggested_focus": "What to focus on and why",
  "time_allocation": {{"deep_work": 4.0, "meetings": 2.0, "admin": 1.0}},
  "blockers": ["Blocker 1", "Blocker 2"]
}}"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        # Extract JSON
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            briefing_data = json.loads(json_match.group())
        else:
            briefing_data = json.loads(response_text)
        
        return DailyBriefing(
            date=datetime.now().strftime("%Y-%m-%d"),
            summary=briefing_data["summary"],
            top_priorities=briefing_data["top_priorities"],
            deadline_warnings=warnings,
            suggested_focus=briefing_data["suggested_focus"],
            time_allocation=briefing_data["time_allocation"],
            blockers=briefing_data["blockers"],
            wins_yesterday=[t.title for t in wins],
            generated_at=datetime.now().isoformat()
        )
    
    def _format_tasks(self, tasks: List[Task]) -> str:
        lines = []
        for t in tasks:
            lines.append(f"- {t.title} ({t.priority.value}, {t.estimated_hours}h)")
        return "\n".join(lines)
    
    def _format_warnings(self, warnings: List[Dict]) -> str:
        if not warnings:
            return "None"
        lines = []
        for w in warnings[:3]:
            lines.append(f"- {w['title']}: {w['hours_remaining']:.1f}h remaining ({w['urgency']})")
        return "\n".join(lines)
    
    def _format_goals(self, goals: List[Goal]) -> str:
        lines = []
        for g in goals:
            lines.append(f"- {g.title}: {g.progress*100:.0f}% complete")
        return "\n".join(lines)

class FocusAdvisor:
    """Answers 'What should I focus on today?'"""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def get_focus_recommendation(self, tasks: List[Task], goals: List[Goal],
                                      memory: MemorySystem, current_context: str = "") -> str:
        """Provide intelligent focus recommendation."""
        
        now = datetime.now()
        current_hour = now.hour
        
        # Determine energy level
        if 9 <= current_hour < 12:
            energy = "high"
        elif 14 <= current_hour < 17:
            energy = "medium-high"
        elif 17 <= current_hour < 20:
            energy = "medium"
        else:
            energy = "low"
        
        prompt = f"""You are a Chief of Staff. Someone just asked: "What should I focus on today?"

Current Context:
- Time: {now.strftime('%A %H:%M')}
- Energy level: {energy}
- {current_context}

Top Tasks:
{self._format_tasks(tasks[:10])}

Active Goals:
{self._format_goals(goals)}

Provide a clear, actionable recommendation:
1. What to focus on RIGHT NOW
2. Why this is the best use of time
3. How long to spend on it
4. What to do next

Be specific and decisive."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    def _format_tasks(self, tasks: List[Task]) -> str:
        lines = []
        for t in tasks:
            status = "✓" if t.status == TaskStatus.DONE else "○"
            deadline = f"Due: {t.deadline}" if t.deadline else ""
            lines.append(f"{status} {t.title} ({t.priority.value}, {t.estimated_hours}h) {deadline}")
        return "\n".join(lines)
    
    def _format_goals(self, goals: List[Goal]) -> str:
        lines = []
        for g in goals:
            lines.append(f"- {g.title} ({g.progress*100:.0f}% complete, target: {g.target_date})")
        return "\n".join(lines)

class ChiefOfStaff:
    """Main agent orchestrating all life operations."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.memory = MemorySystem()
        self.priority_engine = PriorityEngine(self.api_key)
        self.deadline_monitor = DeadlineMonitor()
        self.briefing_generator = BriefingGenerator(self.api_key)
        self.focus_advisor = FocusAdvisor(self.api_key)
        
        self.tasks = []
        self.goals = []
        self.last_briefing = None
    
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
    
    async def generate_daily_briefing(self) -> DailyBriefing:
        """Generate proactive daily briefing."""
        
        print("📋 Generating daily briefing...")
        
        # Re-rank tasks
        ranked_tasks = await self.priority_engine.rank_tasks(
            self.tasks, self.goals, self.memory, datetime.now()
        )
        self.tasks = ranked_tasks
        
        # Check deadlines
        warnings = self.deadline_monitor.check_deadlines(self.tasks)
        
        # Generate briefing
        briefing = await self.briefing_generator.generate_briefing(
            self.tasks, self.goals, self.memory, warnings
        )
        
        self.last_briefing = briefing
        
        # Display
        self._display_briefing(briefing)
        
        return briefing
    
    async def what_should_i_focus_on(self, context: str = "") -> str:
        """Answer the key question."""
        
        print("\n🎯 Analyzing current situation...")
        
        recommendation = await self.focus_advisor.get_focus_recommendation(
            self.tasks, self.goals, self.memory, context
        )
        
        print("\n" + "="*70)
        print("FOCUS RECOMMENDATION")
        print("="*70)
        print(recommendation)
        print("="*70)
        
        return recommendation
    
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
                completed = len([t for t in goal.related_tasks 
                               if next((x for x in self.tasks if x.id == t), None).status == TaskStatus.DONE])
                goal.progress = completed / len(goal.related_tasks)
    
    def _display_briefing(self, briefing: DailyBriefing):
        """Display briefing in terminal."""
        
        print("\n" + "="*70)
        print(f"DAILY BRIEFING - {briefing.date}")
        print("="*70)
        
        print(f"\n📊 SUMMARY")
        print(f"{briefing.summary}")
        
        print(f"\n🎯 TOP PRIORITIES")
        for i, priority in enumerate(briefing.top_priorities, 1):
            print(f"{i}. {priority}")
        
        if briefing.deadline_warnings:
            print(f"\n⚠️  DEADLINE WARNINGS ({len(briefing.deadline_warnings)})")
            for warning in briefing.deadline_warnings[:3]:
                urgency_icon = "🔴" if warning["urgency"] == "CRITICAL" else "🟡"
                print(f"{urgency_icon} {warning['title']}: {warning['hours_remaining']:.1f}h remaining")
        
        print(f"\n💡 SUGGESTED FOCUS")
        print(f"{briefing.suggested_focus}")
        
        print(f"\n⏰ TIME ALLOCATION")
        for activity, hours in briefing.time_allocation.items():
            print(f"  {activity}: {hours:.1f}h")
        
        if briefing.blockers:
            print(f"\n🚧 BLOCKERS TO ADDRESS")
            for blocker in briefing.blockers:
                print(f"  - {blocker}")
        
        if briefing.wins_yesterday:
            print(f"\n✅ WINS YESTERDAY")
            for win in briefing.wins_yesterday:
                print(f"  - {win}")
        
        print("\n" + "="*70)
    
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
        
        print(f"\n💾 State saved to {filepath}")

async def main():
    """Demo the Chief of Staff."""
    
    print("👔 PERSONAL CHIEF OF STAFF")
    print("="*70)
    print("Autonomous AI managing your life operations")
    print("="*70)
    
    chief = ChiefOfStaff()
    
    # Add some goals
    print("\n📌 Setting up goals...")
    
    goal1 = chief.add_goal(
        "Launch new product",
        "Complete MVP and launch to first customers",
        "2026-03-15",
        ["Complete design", "Build MVP", "Get 10 beta users"]
    )
    
    goal2 = chief.add_goal(
        "Improve health",
        "Exercise 3x/week and improve diet",
        "2026-06-01",
        ["Join gym", "Meal prep routine", "Track progress"]
    )
    
    print(f"  ✓ Added {len(chief.goals)} goals")
    
    # Add tasks
    print("\n📝 Adding tasks...")
    
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
    
    print(f"  ✓ Added {len(chief.tasks)} tasks")
    
    # Generate daily briefing
    print("\n" + "="*70)
    briefing = await chief.generate_daily_briefing()
    
    # Ask for focus recommendation
    await asyncio.sleep(1)
    await chief.what_should_i_focus_on("Just finished a meeting, have 2 hours before lunch")
    
    # Save state
    chief.save_state()
    
    print("\n" + "="*70)
    print("✅ Chief of Staff ready!")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
