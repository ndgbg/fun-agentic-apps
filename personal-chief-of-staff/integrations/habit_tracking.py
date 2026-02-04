#!/usr/bin/env python3
"""
Habit Tracking - Exercise, sleep, and wellness tracking
"""

import os
import json
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class HabitType(Enum):
    EXERCISE = "exercise"
    SLEEP = "sleep"
    MEDITATION = "meditation"
    READING = "reading"
    WATER = "water"
    NUTRITION = "nutrition"

@dataclass
class HabitEntry:
    habit_type: HabitType
    date: str
    value: float  # hours, count, etc.
    notes: Optional[str] = None
    mood: Optional[int] = None  # 1-5

@dataclass
class HabitGoal:
    habit_type: HabitType
    target_value: float
    frequency: str  # daily, weekly
    unit: str  # hours, times, glasses

class HabitTracker:
    """Track habits and provide insights."""
    
    def __init__(self):
        self.entries = []
        self.goals = {}
        self.load_state()
    
    def log_habit(self, habit_type: HabitType, value: float, notes: str = None, mood: int = None):
        """Log a habit entry."""
        
        entry = HabitEntry(
            habit_type=habit_type,
            date=date.today().isoformat(),
            value=value,
            notes=notes,
            mood=mood
        )
        
        self.entries.append(entry)
        self.save_state()
        
        return entry
    
    def set_goal(self, habit_type: HabitType, target_value: float, frequency: str, unit: str):
        """Set a habit goal."""
        
        goal = HabitGoal(
            habit_type=habit_type,
            target_value=target_value,
            frequency=frequency,
            unit=unit
        )
        
        self.goals[habit_type.value] = goal
        self.save_state()
        
        return goal
    
    def get_streak(self, habit_type: HabitType) -> int:
        """Calculate current streak for a habit."""
        
        entries = [e for e in self.entries if e.habit_type == habit_type]
        if not entries:
            return 0
        
        # Sort by date descending
        entries.sort(key=lambda x: x.date, reverse=True)
        
        streak = 0
        current_date = date.today()
        
        for entry in entries:
            entry_date = date.fromisoformat(entry.date)
            
            if entry_date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif entry_date < current_date:
                break
        
        return streak
    
    def get_weekly_summary(self, habit_type: HabitType = None) -> Dict:
        """Get summary for the past week."""
        
        week_ago = date.today() - timedelta(days=7)
        
        if habit_type:
            entries = [e for e in self.entries 
                      if e.habit_type == habit_type and 
                      date.fromisoformat(e.date) >= week_ago]
        else:
            entries = [e for e in self.entries 
                      if date.fromisoformat(e.date) >= week_ago]
        
        if not entries:
            return {"total": 0, "average": 0, "days_tracked": 0}
        
        total = sum(e.value for e in entries)
        days_tracked = len(set(e.date for e in entries))
        average = total / days_tracked if days_tracked > 0 else 0
        
        return {
            "total": total,
            "average": average,
            "days_tracked": days_tracked,
            "entries": len(entries)
        }
    
    def get_progress_toward_goal(self, habit_type: HabitType) -> Dict:
        """Check progress toward goal."""
        
        if habit_type.value not in self.goals:
            return {"has_goal": False}
        
        goal = self.goals[habit_type.value]
        
        if goal.frequency == "daily":
            # Check today's progress
            today_entries = [e for e in self.entries 
                           if e.habit_type == habit_type and 
                           e.date == date.today().isoformat()]
            current = sum(e.value for e in today_entries)
        else:  # weekly
            summary = self.get_weekly_summary(habit_type)
            current = summary["total"]
        
        progress = (current / goal.target_value) * 100 if goal.target_value > 0 else 0
        
        return {
            "has_goal": True,
            "current": current,
            "target": goal.target_value,
            "progress": min(progress, 100),
            "unit": goal.unit,
            "frequency": goal.frequency,
            "on_track": current >= goal.target_value
        }
    
    def get_insights(self) -> Dict:
        """Get AI-powered insights about habits."""
        
        insights = {
            "streaks": {},
            "weekly_summaries": {},
            "goal_progress": {}
        }
        
        for habit_type in HabitType:
            insights["streaks"][habit_type.value] = self.get_streak(habit_type)
            insights["weekly_summaries"][habit_type.value] = self.get_weekly_summary(habit_type)
            insights["goal_progress"][habit_type.value] = self.get_progress_toward_goal(habit_type)
        
        return insights
    
    def save_state(self, filepath: str = "habits_state.json"):
        """Save habit data."""
        
        state = {
            "entries": [
                {
                    "habit_type": e.habit_type.value,
                    "date": e.date,
                    "value": e.value,
                    "notes": e.notes,
                    "mood": e.mood
                }
                for e in self.entries
            ],
            "goals": {
                k: {
                    "habit_type": g.habit_type.value,
                    "target_value": g.target_value,
                    "frequency": g.frequency,
                    "unit": g.unit
                }
                for k, g in self.goals.items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str = "habits_state.json"):
        """Load habit data."""
        
        if not os.path.exists(filepath):
            return
        
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.entries = [
                HabitEntry(
                    habit_type=HabitType(e["habit_type"]),
                    date=e["date"],
                    value=e["value"],
                    notes=e.get("notes"),
                    mood=e.get("mood")
                )
                for e in state.get("entries", [])
            ]
            
            self.goals = {
                k: HabitGoal(
                    habit_type=HabitType(g["habit_type"]),
                    target_value=g["target_value"],
                    frequency=g["frequency"],
                    unit=g["unit"]
                )
                for k, g in state.get("goals", {}).items()
            }
            
        except Exception as e:
            print(f"Error loading habits: {e}")

class HabitInsightGenerator:
    """Generate AI insights about habits."""
    
    def __init__(self, api_key: str):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def generate_insights(self, insights: Dict) -> str:
        """Generate personalized habit insights."""
        
        prompt = f"""Analyze these habit tracking data and provide insights.

Data:
{json.dumps(insights, indent=2)}

Provide:
1. What's going well (celebrate wins)
2. Areas for improvement
3. Specific actionable recommendations
4. Patterns you notice

Be encouraging and specific."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            temperature=0.6,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text

def main():
    """Demo habit tracking."""
    
    print("🏃 HABIT TRACKING")
    print("="*70)
    
    tracker = HabitTracker()
    
    # Set goals
    print("\n📌 Setting goals...")
    tracker.set_goal(HabitType.EXERCISE, 1.0, "daily", "hours")
    tracker.set_goal(HabitType.SLEEP, 8.0, "daily", "hours")
    tracker.set_goal(HabitType.WATER, 8.0, "daily", "glasses")
    print("  ✓ Goals set")
    
    # Log some habits
    print("\n📝 Logging habits...")
    tracker.log_habit(HabitType.EXERCISE, 0.5, "Morning run", mood=4)
    tracker.log_habit(HabitType.SLEEP, 7.5, "Slept well")
    tracker.log_habit(HabitType.WATER, 6.0)
    print("  ✓ Habits logged")
    
    # Get insights
    print("\n📊 HABIT INSIGHTS")
    print("-"*70)
    
    insights = tracker.get_insights()
    
    for habit_type in HabitType:
        habit_name = habit_type.value.capitalize()
        streak = insights["streaks"][habit_type.value]
        summary = insights["weekly_summaries"][habit_type.value]
        progress = insights["goal_progress"][habit_type.value]
        
        if summary["days_tracked"] > 0:
            print(f"\n{habit_name}:")
            print(f"  Streak: {streak} days")
            print(f"  This week: {summary['average']:.1f} avg ({summary['days_tracked']} days)")
            
            if progress["has_goal"]:
                status = "✅" if progress["on_track"] else "⚠️"
                print(f"  Goal: {progress['current']:.1f}/{progress['target']:.1f} {progress['unit']} {status}")
                print(f"  Progress: {progress['progress']:.0f}%")
    
    # Generate AI insights
    if os.getenv("ANTHROPIC_API_KEY"):
        print("\n\n🤖 AI INSIGHTS")
        print("-"*70)
        
        import asyncio
        generator = HabitInsightGenerator(os.getenv("ANTHROPIC_API_KEY"))
        ai_insights = asyncio.run(generator.generate_insights(insights))
        print(ai_insights)
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
