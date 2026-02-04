# 👔 Personal Chief of Staff

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude%203.5-orange.svg)](https://www.anthropic.com/)
[![Google APIs](https://img.shields.io/badge/Google-Calendar%20%2B%20Gmail-green.svg)](https://developers.google.com/)
[![Slack](https://img.shields.io/badge/Slack-API-purple.svg)](https://api.slack.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A local AI that runs your life ops. Self-hosted, proactive, and memory-enabled.

## What It Does

- **Daily briefings** - Comprehensive morning briefings with priorities and warnings
- **Priority re-ranking** - Autonomous task prioritization based on context
- **Deadline warnings** - Proactive alerts for approaching deadlines
- **Context switching support** - Minimizes cognitive load when switching tasks
- **"What should I focus on today?"** - Intelligent focus recommendations
- **Calendar integration** - Auto-import tasks from Google Calendar and Outlook
- **Email integration** - Extract action items from Gmail and IMAP
- **Slack/Teams notifications** - Daily briefings and meeting reminders
- **Habit tracking** - Track exercise, sleep, and wellness with AI insights

## What's Different

Unlike todo apps or calendar tools:

- **Self-hosted** - Your data stays local, runs on your machine
- **Memory + goals** - Learns your patterns and aligns with long-term goals
- **Proactive, not reactive** - Anticipates needs, doesn't wait for you to ask
- **Real integrations** - Connects to your actual calendar, email, and chat tools

## Why It's Agentic

This isn't a smart todo list. The agent:

- **Autonomously prioritizes** - Re-ranks tasks based on deadlines, energy, dependencies, and goals
- **Learns patterns** - Tracks when you work best, how long tasks really take, context switch costs
- **Reasons about tradeoffs** - Balances urgency vs importance, short-term vs long-term
- **Proactively warns** - Identifies deadline conflicts before they become problems
- **Adapts recommendations** - Considers current time, energy level, and context
- **Aligns with goals** - Ensures daily work connects to long-term objectives

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run
python chief.py
```

## Core Components

### 1. Memory System

Learns from your behavior:

```python
memory = MemorySystem()

# Tracks patterns
- When you work best (peak hours)
- How accurate your time estimates are
- Cost of context switching
- Task completion patterns
```

**What it learns:**
- Best work times (e.g., 9-12am, 2-5pm)
- Estimation accuracy (you typically take 1.3x estimated time)
- Context switch cost (average 15 minutes)
- Energy patterns throughout the day

### 2. Priority Engine

Autonomous task ranking:

```python
ranked_tasks = await priority_engine.rank_tasks(
    tasks, goals, memory, current_time
)
```

**Considers:**
- Deadlines (urgent vs important)
- Goal alignment (does this move you toward goals?)
- Dependencies (what's blocking what?)
- Energy levels (match task to current energy)
- Context switching costs (minimize disruption)
- Estimated effort (can you finish today?)

**Output:**
- Re-ranked task list
- Reasoning for each ranking
- Suggested order of execution

### 3. Deadline Monitor

Proactive deadline tracking:

```python
warnings = deadline_monitor.check_deadlines(tasks)
```

**Warning thresholds:**
- Critical priority: 24 hours
- High priority: 48 hours
- Medium priority: 72 hours
- Low priority: 168 hours (1 week)

**Provides:**
- Hours remaining
- Urgency level (CRITICAL/WARNING)
- Feasibility (can you complete in time?)

### 4. Daily Briefing

Comprehensive morning briefing:

```python
briefing = await chief.generate_daily_briefing()
```

**Includes:**
- Executive summary
- Top 3 priorities
- Deadline warnings
- Suggested focus area
- Time allocation recommendation
- Blockers to address
- Yesterday's wins

### 5. Focus Advisor

Answers "What should I focus on?"

```python
recommendation = await chief.what_should_i_focus_on(
    "Just finished a meeting, have 2 hours before lunch"
)
```

**Considers:**
- Current time and energy level
- Available time window
- Task priorities and deadlines
- Context switching costs
- Goal alignment

**Provides:**
- Specific task to focus on RIGHT NOW
- Why it's the best use of time
- How long to spend
- What to do next

## Example Usage

```python
from chief import ChiefOfStaff, Priority
from datetime import datetime, timedelta

# Initialize
chief = ChiefOfStaff()

# Add goals
chief.add_goal(
    "Launch new product",
    "Complete MVP and launch to first customers",
    "2026-03-15",
    ["Complete design", "Build MVP", "Get 10 beta users"]
)

# Add tasks
chief.add_task(
    "Finish product spec",
    "Complete technical specification",
    Priority.HIGH,
    deadline=(datetime.now() + timedelta(days=2)).isoformat(),
    estimated_hours=4.0
)

# Get daily briefing
briefing = await chief.generate_daily_briefing()

# Ask for focus
recommendation = await chief.what_should_i_focus_on()

# Complete task (agent learns)
chief.complete_task("task_1", actual_hours=5.0)

# Save state
chief.save_state()
```

## Daily Briefing Example

```
DAILY BRIEFING - 2026-02-03
======================================================================

📊 SUMMARY
You have 5 active tasks with 2 approaching deadlines. Focus on 
high-priority items this morning while energy is high. One blocker 
needs immediate attention.

🎯 TOP PRIORITIES
1. Schedule team meeting (6h deadline, blocks other work)
2. Review design mockups (24h deadline, high impact)
3. Finish product spec (48h deadline, critical for launch)

⚠️ DEADLINE WARNINGS (2)
🔴 Schedule team meeting: 6.0h remaining
🟡 Review design mockups: 24.0h remaining

💡 SUGGESTED FOCUS
Start with the team meeting scheduling (30 min) to unblock others, 
then dive into design review (2h) while energy is high. Save product 
spec for afternoon deep work session.

⏰ TIME ALLOCATION
  deep_work: 4.0h
  meetings: 2.0h
  admin: 1.0h

🚧 BLOCKERS TO ADDRESS
  - Waiting on design team feedback before finalizing spec

✅ WINS YESTERDAY
  - Completed competitor research analysis
  - Sent investor update ahead of schedule
```

## Focus Recommendation Example

```
FOCUS RECOMMENDATION
======================================================================

RIGHT NOW (High Energy):

Focus on the design review for the next 2 hours. This requires 
creative thinking and you're at peak energy.

Why: It's due in 24h, requires deep focus, and unblocks the product 
spec work.

Next: After lunch, tackle the product spec (4h deep work session).

Quick win: Spend 15 minutes scheduling that team meeting first to 
unblock others.
```

## Memory & Learning

The agent learns from your behavior:

### Time Estimation
```python
# You estimate: 2 hours
# Actually takes: 3 hours
# Agent learns: You typically underestimate by 1.5x
# Future estimates adjusted automatically
```

### Work Patterns
```python
# Agent observes:
- Most tasks completed 9-12am
- Fewer completions 1-3pm
- Good productivity 3-6pm

# Recommends:
- Deep work in morning
- Meetings/admin after lunch
- Creative work mid-afternoon
```

### Context Switching
```python
# Agent tracks:
- Switched from coding to meeting: 20 min to refocus
- Switched from email to writing: 10 min to refocus
- Average cost: 15 minutes

# Optimizes:
- Batches similar tasks
- Minimizes switches
- Warns about high-cost switches
```

## Dashboard

Visual interface for daily operations:

```bash
open dashboard.html
```

**Features:**
- Daily briefing display
- Priority list
- Deadline warnings
- Time allocation
- Focus recommendation button
- Task list with status

## Integrations

### Calendar Integration

Import tasks automatically from your calendar:

```python
from integrations.calendar_integration import GoogleCalendarIntegration

calendar = GoogleCalendarIntegration()
events = calendar.get_todays_events()

# AI extracts tasks from events
extractor = CalendarTaskExtractor(api_key)
tasks = await extractor.extract_tasks_from_events(events)
```

**Supports:**
- ✅ Google Calendar (OAuth)
- ✅ Outlook/Microsoft Graph
- ✅ Auto-extract prep and follow-up tasks
- ✅ Meeting reminders

### Email Integration

Extract action items from emails:

```python
from integrations.email_integration import GmailIntegration

gmail = GmailIntegration()
emails = gmail.get_unread_emails()

# AI extracts tasks from emails
extractor = EmailTaskExtractor(api_key)
tasks = await extractor.extract_tasks_from_emails(emails)
```

**Supports:**
- ✅ Gmail (OAuth)
- ✅ Any IMAP provider
- ✅ Priority detection
- ✅ Deadline extraction

### Slack/Teams Integration

Send briefings and reminders:

```python
from integrations.slack_teams_integration import SlackIntegration

slack = SlackIntegration()
slack.send_daily_briefing("#general", briefing)
slack.send_meeting_reminder("#general", meeting)
slack.send_deadline_alert("#general", task)
```

**Supports:**
- ✅ Slack (Bot API)
- ✅ Microsoft Teams (Webhooks)
- ✅ Daily briefings
- ✅ Meeting reminders (15 min before)
- ✅ Deadline alerts

### Habit Tracking

Track wellness and get insights:

```python
from integrations.habit_tracking import HabitTracker, HabitType

tracker = HabitTracker()

# Set goals
tracker.set_goal(HabitType.EXERCISE, 1.0, "daily", "hours")
tracker.set_goal(HabitType.SLEEP, 8.0, "daily", "hours")

# Log habits
tracker.log_habit(HabitType.EXERCISE, 0.5, "Morning run", mood=4)

# Get insights
insights = tracker.get_insights()
print(f"Exercise streak: {insights['streaks']['exercise']} days")
```

**Tracks:**
- ✅ Exercise
- ✅ Sleep
- ✅ Meditation
- ✅ Reading
- ✅ Water intake
- ✅ Nutrition

**Setup:** See [integrations/SETUP.md](integrations/SETUP.md) for complete setup guide.

## State Persistence

All data stored locally:

```json
{
  "tasks": [...],
  "goals": [...],
  "memory": {
    "task_history": [...],
    "context_switches": [...],
    "preferences": {...}
  }
}
```

## Use Cases

### Morning Routine
```python
# Start your day
briefing = await chief.generate_daily_briefing()
# Get clear priorities and plan
```

### Mid-Day Check
```python
# Lost focus?
recommendation = await chief.what_should_i_focus_on(
    "Just finished lunch, feeling a bit sluggish"
)
# Get specific guidance
```

### End of Day
```python
# Complete tasks
chief.complete_task("task_1", actual_hours=3.5)
# Agent learns from actual time spent

# Save state
chief.save_state()
```

### Weekly Planning
```python
# Review goals
for goal in chief.goals:
    print(f"{goal.title}: {goal.progress*100:.0f}% complete")

# Adjust priorities based on progress
```

## Advanced Features

### Goal Alignment

Tasks automatically linked to goals:

```python
goal = chief.add_goal("Launch product", ...)
task = chief.add_task("Build feature X", ...)

# Agent ensures daily work aligns with goals
# Warns if you're off track
```

### Dependency Tracking

```python
task1 = chief.add_task("Design API", ...)
task2 = chief.add_task("Implement API", dependencies=["task_1"])

# Agent won't recommend task2 until task1 is done
# Identifies blocking tasks automatically
```

### Energy-Aware Scheduling

```python
# Morning (high energy): Deep work, creative tasks
# Afternoon (medium): Meetings, collaboration
# Evening (low): Admin, email, planning
```

### Context Preservation

```python
# When switching tasks, agent provides:
- Summary of where you left off
- Key context to remember
- Estimated time to get back in flow
```

## Architecture

```
ChiefOfStaff
├── MemorySystem
│   └── Learns patterns, tracks history
├── PriorityEngine
│   └── Autonomous task ranking
├── DeadlineMonitor
│   └── Proactive warnings
├── BriefingGenerator
│   └── Daily briefings
└── FocusAdvisor
    └── Real-time recommendations
```

## Technical Details

**Models**: Claude 3.5 Sonnet  
**Storage**: Local JSON files  
**Privacy**: All data stays on your machine  
**Learning**: Continuous from task completions  
**Integrations**: Google Calendar, Gmail, Slack, Teams, IMAP

## Comparison

| Feature | Todo Apps | Calendar | Chief of Staff |
|---------|-----------|----------|----------------|
| Task tracking | ✅ | ❌ | ✅ |
| Deadlines | ✅ | ✅ | ✅ |
| Prioritization | Manual | ❌ | Autonomous |
| Learning | ❌ | ❌ | ✅ |
| Proactive | ❌ | ❌ | ✅ |
| Goal alignment | ❌ | ❌ | ✅ |
| Context aware | ❌ | ❌ | ✅ |
| Focus guidance | ❌ | ❌ | ✅ |
| Calendar sync | ❌ | ✅ | ✅ |
| Email parsing | ❌ | ❌ | ✅ |
| Chat notifications | ❌ | ❌ | ✅ |
| Habit tracking | ❌ | ❌ | ✅ |

## Best Practices

1. **Update daily** - Run briefing each morning
2. **Track actual time** - Help agent learn your patterns
3. **Set clear goals** - Agent aligns tasks to goals
4. **Trust the ranking** - Agent considers factors you might miss
5. **Use focus advisor** - When feeling scattered or overwhelmed
6. **Connect integrations** - Let agent auto-import from calendar/email
7. **Track habits** - Get insights on energy and productivity patterns

## Limitations

- Requires API key (uses Claude for reasoning)
- Best for knowledge work (not physical tasks)
- Learns over time (needs data to improve)
- English language only

## Complete Integration Example

See [integrations/full_integration_example.py](integrations/full_integration_example.py) for end-to-end workflow:

```python
# Morning workflow
1. Import from calendar → Extract tasks
2. Scan emails → Extract action items
3. Check habits → Get insights
4. Generate briefing → Send to Slack/Teams
5. Get focus recommendation
6. Save state
```

## Setup Integrations

See [integrations/SETUP.md](integrations/SETUP.md) for detailed setup:

- Google Calendar (OAuth)
- Gmail (OAuth)
- Outlook (Microsoft Graph)
- Slack (Bot Token)
- Teams (Webhook)
- IMAP (Any provider)

## License

MIT

---

Built with Claude 3.5 Sonnet. Part of the [Fun Agentic Apps](https://github.com/ndgbg/fun-agentic-apps) collection.
