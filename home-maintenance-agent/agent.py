#!/usr/bin/env python3
"""
Home Maintenance Agent - Agentic Multi-Tool System for Proactive Home Care
Uses an Anthropic tool_use loop where a coordinator LLM decides which sub-agent
capability to invoke, observes results, and adapts its plan dynamically.
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import anthropic

class MaintenanceCategory(Enum):
    HVAC = "hvac"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    APPLIANCES = "appliances"
    EXTERIOR = "exterior"
    INTERIOR = "interior"
    LANDSCAPING = "landscaping"
    SAFETY = "safety"
    SEASONAL = "seasonal"
    CLEANING = "cleaning"
    ORGANIZATION = "organization"

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"

@dataclass
class MaintenanceTask:
    id: str
    title: str
    category: MaintenanceCategory
    description: str
    priority: Priority
    frequency_days: int
    last_completed: Optional[str]
    next_due: str
    estimated_cost: float
    estimated_hours: float
    requires_professional: bool
    season_dependent: bool
    weather_dependent: bool
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Alert:
    id: str
    task_id: str
    severity: str
    message: str
    created_at: str
    acknowledged: bool = False

@dataclass
class HomeProfile:
    home_age: int
    square_footage: int
    num_bedrooms: int
    num_bathrooms: int
    has_basement: bool
    has_attic: bool
    has_garage: bool
    hvac_type: str
    hvac_age: int
    roof_age: int
    location: str
    climate_zone: str

class PredictiveMaintenanceAgent:
    """Uses ML patterns to predict maintenance needs before failures."""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    async def predict_failures(self, home_profile: HomeProfile,
                              maintenance_history: List[MaintenanceTask]) -> List[Dict]:
        """Predict potential failures based on home profile and history."""

        prompt = f"""You are a predictive maintenance expert. Analyze this home and predict potential failures.

Home Profile:
- Age: {home_profile.home_age} years
- Size: {home_profile.square_footage} sq ft
- HVAC: {home_profile.hvac_type}, {home_profile.hvac_age} years old
- Roof: {home_profile.roof_age} years old
- Location: {home_profile.location}
- Climate: {home_profile.climate_zone}

Recent Maintenance:
{self._format_history(maintenance_history[-10:])}

Predict:
1. Systems likely to fail in next 6 months
2. Probability of failure (0-100%)
3. Estimated cost if failure occurs
4. Preventive actions to take now

Return JSON array:
[
  {{
    "system": "HVAC compressor",
    "failure_probability": 65,
    "time_to_failure_days": 120,
    "failure_cost": 2500,
    "preventive_action": "Schedule HVAC inspection and refrigerant check",
    "preventive_cost": 150,
    "reasoning": "HVAC is 12 years old, approaching typical compressor lifespan"
  }}
]"""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        import re
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return []

    def _format_history(self, tasks: List[MaintenanceTask]) -> str:
        if not tasks:
            return "No recent maintenance"
        return "\n".join([f"- {t.title} ({t.category.value}): {t.last_completed or 'Never'}"
                         for t in tasks])

class SchedulingAgent:
    """Optimizes maintenance scheduling based on multiple constraints."""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    async def optimize_schedule(self, tasks: List[MaintenanceTask],
                                constraints: Dict) -> List[Dict]:
        """Create optimal maintenance schedule."""

        tasks_text = "\n".join([
            f"- {t.title} (Due: {t.next_due}, Priority: {t.priority.value}, "
            f"Cost: ${t.estimated_cost}, Hours: {t.estimated_hours}h, "
            f"Professional: {t.requires_professional})"
            for t in tasks[:20]
        ])

        prompt = f"""You are a scheduling optimization expert. Create an optimal maintenance schedule.

Tasks to Schedule:
{tasks_text}

Constraints:
- Budget: ${constraints.get('monthly_budget', 500)}/month
- Available time: {constraints.get('hours_per_week', 4)}h/week
- Season: {constraints.get('current_season', 'spring')}
- Weather: {constraints.get('weather_forecast', 'normal')}

Optimize for:
1. Prevent critical failures
2. Minimize total cost (do preventive vs reactive)
3. Group related tasks
4. Consider seasonal appropriateness
5. Balance DIY vs professional work

Return JSON array of scheduled tasks:
[
  {{
    "task_id": "task_1",
    "scheduled_date": "2026-02-15",
    "reasoning": "Critical HVAC filter change, prevents $2000 repair",
    "grouped_with": ["task_2"],
    "estimated_total_cost": 45,
    "estimated_total_hours": 1.5
  }}
]"""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2500,
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        import re
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return []

class AlertAgent:
    """Monitors conditions and generates intelligent alerts."""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.alerts = []

    async def generate_alerts(self, tasks: List[MaintenanceTask],
                             predictions: List[Dict],
                             weather: Dict) -> List[Alert]:
        """Generate contextual alerts based on multiple factors."""

        alerts = []
        now = datetime.now()

        # Overdue tasks
        for task in tasks:
            if task.status != TaskStatus.COMPLETED:
                due_date = datetime.fromisoformat(task.next_due)
                days_until = (due_date - now).days

                if days_until < 0:
                    alerts.append(Alert(
                        id=f"alert_{len(alerts)}",
                        task_id=task.id,
                        severity="critical",
                        message=f"OVERDUE: {task.title} was due {abs(days_until)} days ago",
                        created_at=now.isoformat()
                    ))
                elif days_until <= 7 and task.priority == Priority.CRITICAL:
                    alerts.append(Alert(
                        id=f"alert_{len(alerts)}",
                        task_id=task.id,
                        severity="high",
                        message=f"URGENT: {task.title} due in {days_until} days",
                        created_at=now.isoformat()
                    ))
                elif days_until <= 14 and task.priority == Priority.HIGH:
                    alerts.append(Alert(
                        id=f"alert_{len(alerts)}",
                        task_id=task.id,
                        severity="medium",
                        message=f"Reminder: {task.title} due in {days_until} days",
                        created_at=now.isoformat()
                    ))

        # Predictive alerts
        for pred in predictions:
            if pred.get('failure_probability', 0) > 60:
                alerts.append(Alert(
                    id=f"alert_{len(alerts)}",
                    task_id="predictive",
                    severity="high",
                    message=f"PREDICTION: {pred['system']} has {pred['failure_probability']}% "
                           f"chance of failure in {pred['time_to_failure_days']} days. "
                           f"Take action: {pred['preventive_action']}",
                    created_at=now.isoformat()
                ))

        # Weather-based alerts
        if weather.get('severe_weather'):
            weather_tasks = [t for t in tasks if t.weather_dependent]
            if weather_tasks:
                alerts.append(Alert(
                    id=f"alert_{len(alerts)}",
                    task_id="weather",
                    severity="medium",
                    message=f"Weather alert: {weather['condition']}. "
                           f"Postpone outdoor tasks: {', '.join([t.title for t in weather_tasks[:3]])}",
                    created_at=now.isoformat()
                ))

        self.alerts.extend(alerts)
        return alerts

class CalendarIntegrationAgent:
    """Integrates with Google Calendar for scheduling and reminders."""

    def __init__(self):
        self.calendar_service = None
        self._initialize()

    def _initialize(self):
        """Initialize Google Calendar API."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            SCOPES = ['https://www.googleapis.com/auth/calendar']

            creds = None
            if os.path.exists('calendar_token.json'):
                creds = Credentials.from_authorized_user_file('calendar_token.json', SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if os.path.exists('credentials.json'):
                        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                        creds = flow.run_local_server(port=0)

                with open('calendar_token.json', 'w') as token:
                    token.write(creds.to_json())

            self.calendar_service = build('calendar', 'v3', credentials=creds)

        except Exception as e:
            print(f"Calendar integration not configured: {e}")

    def add_maintenance_event(self, task: MaintenanceTask, scheduled_date: str) -> Optional[str]:
        """Add maintenance task to Google Calendar."""

        if not self.calendar_service:
            print(f"[MOCK] Would add to calendar: {task.title} on {scheduled_date}")
            return f"mock_event_{task.id}"

        try:
            event = {
                'summary': f"Home Maintenance: {task.title}",
                'description': f"{task.description}\n\n"
                              f"Category: {task.category.value}\n"
                              f"Estimated time: {task.estimated_hours}h\n"
                              f"Estimated cost: ${task.estimated_cost}\n"
                              f"Professional required: {task.requires_professional}",
                'start': {
                    'dateTime': f"{scheduled_date}T09:00:00",
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': f"{scheduled_date}T{9 + int(task.estimated_hours):02d}:00:00",
                    'timeZone': 'America/Los_Angeles',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 60},
                    ],
                },
            }

            event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            return event.get('id')

        except Exception as e:
            print(f"Error adding to calendar: {e}")
            return None

    def add_reminder(self, alert: Alert, days_before: int = 1) -> Optional[str]:
        """Add reminder for alert."""

        if not self.calendar_service:
            print(f"[MOCK] Would add reminder: {alert.message}")
            return f"mock_reminder_{alert.id}"

        try:
            reminder_date = (datetime.now() + timedelta(days=days_before)).isoformat()

            event = {
                'summary': f"Maintenance Alert",
                'description': alert.message,
                'start': {
                    'dateTime': reminder_date,
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': reminder_date,
                    'timeZone': 'America/Los_Angeles',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 0},
                        {'method': 'popup', 'minutes': 0},
                    ],
                },
            }

            event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()

            return event.get('id')

        except Exception as e:
            print(f"Error adding reminder: {e}")
            return None

class KnowledgeBaseAgent:
    """Maintains knowledge base of maintenance procedures and best practices."""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.knowledge_base = {}

    async def get_maintenance_guide(self, task: MaintenanceTask) -> Dict:
        """Generate detailed maintenance guide for a task."""

        prompt = f"""You are a home maintenance expert. Provide a detailed guide for this task.

Task: {task.title}
Category: {task.category.value}
Description: {task.description}

Provide:
1. Step-by-step instructions
2. Tools needed
3. Materials needed
4. Safety precautions
5. Common mistakes to avoid
6. When to call a professional
7. Estimated time breakdown
8. Cost breakdown

Return JSON:
{{
  "steps": ["Step 1", "Step 2"],
  "tools": ["Tool 1", "Tool 2"],
  "materials": ["Material 1"],
  "safety": ["Safety tip 1"],
  "mistakes_to_avoid": ["Mistake 1"],
  "call_professional_if": ["Condition 1"],
  "time_breakdown": {{"prep": 30, "work": 60, "cleanup": 15}},
  "cost_breakdown": {{"materials": 50, "tools": 0, "professional": 0}}
}}"""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            guide = json.loads(json_match.group())
            self.knowledge_base[task.id] = guide
            return guide
        return {}

class CostOptimizationAgent:
    """Optimizes costs by analyzing DIY vs professional, bulk purchasing, etc."""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    async def optimize_costs(self, tasks: List[MaintenanceTask],
                            budget: float) -> Dict:
        """Analyze and optimize maintenance costs."""

        tasks_text = "\n".join([
            f"- {t.title}: ${t.estimated_cost} ({'Pro' if t.requires_professional else 'DIY'})"
            for t in tasks[:15]
        ])

        prompt = f"""You are a cost optimization expert. Analyze these maintenance tasks and optimize costs.

Tasks:
{tasks_text}

Annual Budget: ${budget}

Optimize by:
1. Identifying tasks that can be DIY vs professional
2. Finding bulk purchase opportunities
3. Suggesting preventive maintenance to avoid costly repairs
4. Identifying seasonal discounts
5. Recommending task bundling for contractor discounts

Return JSON:
{{
  "total_estimated_cost": 5000,
  "optimized_cost": 3500,
  "savings": 1500,
  "recommendations": [
    {{
      "task": "HVAC filter replacement",
      "original_cost": 150,
      "optimized_cost": 45,
      "strategy": "DIY + bulk purchase filters",
      "savings": 105
    }}
  ],
  "diy_opportunities": ["Task 1", "Task 2"],
  "bulk_purchase_items": ["Filters", "Light bulbs"],
  "contractor_bundles": [["Task A", "Task B"]]
}}"""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {}

class HomeMaintenanceOrchestrator:
    """Agentic orchestrator that uses a tool_use loop to coordinate sub-agents."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)

        # Initialize sub-agents (they serve as tool implementations)
        self.predictive_agent = PredictiveMaintenanceAgent(self.api_key)
        self.scheduling_agent = SchedulingAgent(self.api_key)
        self.alert_agent = AlertAgent(self.api_key)
        self.calendar_agent = CalendarIntegrationAgent()
        self.knowledge_agent = KnowledgeBaseAgent(self.api_key)
        self.cost_agent = CostOptimizationAgent(self.api_key)

        # State
        self.home_profile = None
        self.tasks = []
        self.alerts = []
        self.schedule = []

    def initialize_home(self, profile: HomeProfile):
        """Initialize home profile."""
        self.home_profile = profile
        self._generate_baseline_tasks()

    def _generate_baseline_tasks(self):
        """Generate baseline maintenance tasks based on home profile."""

        baseline = [
            MaintenanceTask(
                id="task_hvac_filter",
                title="Replace HVAC filters",
                category=MaintenanceCategory.HVAC,
                description="Replace air filters in HVAC system",
                priority=Priority.HIGH,
                frequency_days=90,
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=30)).isoformat(),
                estimated_cost=45.0,
                estimated_hours=0.5,
                requires_professional=False,
                season_dependent=False,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_hvac_service",
                title="HVAC annual service",
                category=MaintenanceCategory.HVAC,
                description="Professional HVAC inspection and tune-up",
                priority=Priority.HIGH,
                frequency_days=365,
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=60)).isoformat(),
                estimated_cost=150.0,
                estimated_hours=2.0,
                requires_professional=True,
                season_dependent=True,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_gutter_clean",
                title="Clean gutters",
                category=MaintenanceCategory.EXTERIOR,
                description="Remove debris from gutters and downspouts",
                priority=Priority.MEDIUM,
                frequency_days=180,
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=45)).isoformat(),
                estimated_cost=200.0,
                estimated_hours=3.0,
                requires_professional=False,
                season_dependent=True,
                weather_dependent=True
            ),
            MaintenanceTask(
                id="task_smoke_detectors",
                title="Test smoke detectors",
                category=MaintenanceCategory.SAFETY,
                description="Test all smoke detectors and replace batteries",
                priority=Priority.CRITICAL,
                frequency_days=180,
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=7)).isoformat(),
                estimated_cost=20.0,
                estimated_hours=0.5,
                requires_professional=False,
                season_dependent=False,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_water_heater",
                title="Flush water heater",
                category=MaintenanceCategory.PLUMBING,
                description="Drain and flush water heater to remove sediment",
                priority=Priority.MEDIUM,
                frequency_days=365,
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=90)).isoformat(),
                estimated_cost=0.0,
                estimated_hours=1.5,
                requires_professional=False,
                season_dependent=False,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_washing_machine",
                title="Clean washing machine",
                category=MaintenanceCategory.APPLIANCES,
                description="Run cleaning cycle and drain water to prevent mold and odors",
                priority=Priority.MEDIUM,
                frequency_days=21,  # Every 3 weeks
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=21)).isoformat(),
                estimated_cost=5.0,  # Cleaning tablets
                estimated_hours=0.25,
                requires_professional=False,
                season_dependent=False,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_winterize_outdoor_taps",
                title="Winterize outdoor faucets",
                category=MaintenanceCategory.SEASONAL,
                description="Install insulated covers on outdoor faucets and drain hoses",
                priority=Priority.HIGH,
                frequency_days=365,
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=30)).isoformat(),  # Before winter
                estimated_cost=25.0,  # Faucet covers
                estimated_hours=1.0,
                requires_professional=False,
                season_dependent=True,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_winterize_sprinklers",
                title="Winterize sprinkler system",
                category=MaintenanceCategory.SEASONAL,
                description="Blow out sprinkler lines and shut off water supply",
                priority=Priority.HIGH,
                frequency_days=365,
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=30)).isoformat(),
                estimated_cost=75.0,  # Professional blowout
                estimated_hours=1.0,
                requires_professional=True,
                season_dependent=True,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_winterize_hvac",
                title="Winterize HVAC system",
                category=MaintenanceCategory.SEASONAL,
                description="Cover outdoor AC unit and switch to heating mode",
                priority=Priority.MEDIUM,
                frequency_days=365,
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=30)).isoformat(),
                estimated_cost=15.0,  # AC cover
                estimated_hours=0.5,
                requires_professional=False,
                season_dependent=True,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_spring_dewinterize",
                title="Spring de-winterization",
                category=MaintenanceCategory.SEASONAL,
                description="Remove faucet covers, turn on outdoor water, uncover AC unit",
                priority=Priority.MEDIUM,
                frequency_days=365,
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=180)).isoformat(),  # Spring
                estimated_cost=0.0,
                estimated_hours=1.0,
                requires_professional=False,
                season_dependent=True,
                weather_dependent=False
            ),
            # Cleaning & Organization Tasks
            MaintenanceTask(
                id="task_trash_weekly",
                title="Take out trash and recycling",
                category=MaintenanceCategory.CLEANING,
                description="Take trash and recycling bins to curb",
                priority=Priority.MEDIUM,
                frequency_days=7,  # Weekly
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=7)).isoformat(),
                estimated_cost=0.0,
                estimated_hours=0.25,
                requires_professional=False,
                season_dependent=False,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_clean_fridge",
                title="Clean refrigerator",
                category=MaintenanceCategory.CLEANING,
                description="Clean shelves, drawers, check expiration dates, wipe down exterior",
                priority=Priority.MEDIUM,
                frequency_days=30,  # Monthly
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=30)).isoformat(),
                estimated_cost=0.0,
                estimated_hours=1.0,
                requires_professional=False,
                season_dependent=False,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_clean_pantry",
                title="Organize and clean pantry",
                category=MaintenanceCategory.ORGANIZATION,
                description="Check expiration dates, reorganize, wipe shelves, restock",
                priority=Priority.LOW,
                frequency_days=90,  # Quarterly
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=90)).isoformat(),
                estimated_cost=0.0,
                estimated_hours=1.5,
                requires_professional=False,
                season_dependent=False,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_clean_closets",
                title="Organize closets",
                category=MaintenanceCategory.ORGANIZATION,
                description="Sort clothes, donate unused items, reorganize, seasonal rotation",
                priority=Priority.LOW,
                frequency_days=180,  # Twice yearly
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=180)).isoformat(),
                estimated_cost=0.0,
                estimated_hours=3.0,
                requires_professional=False,
                season_dependent=True,  # Spring and fall
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_deep_clean_kitchen",
                title="Deep clean kitchen",
                category=MaintenanceCategory.CLEANING,
                description="Clean oven, microwave, behind appliances, cabinets, floors",
                priority=Priority.MEDIUM,
                frequency_days=90,  # Quarterly
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=90)).isoformat(),
                estimated_cost=0.0,
                estimated_hours=3.0,
                requires_professional=False,
                season_dependent=False,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_deep_clean_bathrooms",
                title="Deep clean bathrooms",
                category=MaintenanceCategory.CLEANING,
                description="Scrub grout, clean exhaust fans, descale fixtures, organize cabinets",
                priority=Priority.MEDIUM,
                frequency_days=60,  # Every 2 months
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=60)).isoformat(),
                estimated_cost=0.0,
                estimated_hours=2.0,
                requires_professional=False,
                season_dependent=False,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_clean_windows",
                title="Clean windows inside and out",
                category=MaintenanceCategory.CLEANING,
                description="Wash windows, clean screens, wipe sills and tracks",
                priority=Priority.LOW,
                frequency_days=180,  # Twice yearly
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=180)).isoformat(),
                estimated_cost=0.0,
                estimated_hours=2.0,
                requires_professional=False,
                season_dependent=True,  # Spring and fall
                weather_dependent=True
            ),
            MaintenanceTask(
                id="task_vacuum_carpets",
                title="Deep vacuum and carpet cleaning",
                category=MaintenanceCategory.CLEANING,
                description="Vacuum all carpets, move furniture, spot clean stains",
                priority=Priority.MEDIUM,
                frequency_days=14,  # Bi-weekly
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=14)).isoformat(),
                estimated_cost=0.0,
                estimated_hours=1.0,
                requires_professional=False,
                season_dependent=False,
                weather_dependent=False
            ),
            MaintenanceTask(
                id="task_clean_garage",
                title="Organize and clean garage",
                category=MaintenanceCategory.ORGANIZATION,
                description="Sweep floor, organize tools, dispose of hazardous materials, declutter",
                priority=Priority.LOW,
                frequency_days=180,  # Twice yearly
                last_completed=None,
                next_due=(datetime.now() + timedelta(days=180)).isoformat(),
                estimated_cost=0.0,
                estimated_hours=3.0,
                requires_professional=False,
                season_dependent=True,
                weather_dependent=False
            ),
        ]

        self.tasks.extend(baseline)

    def _get_tool_definitions(self) -> List[Dict]:
        """Return Anthropic tool schemas for all sub-agent capabilities."""
        return [
            {
                "name": "predict_failures",
                "description": (
                    "Run predictive maintenance analysis on the home to identify systems "
                    "likely to fail in the next 6 months. Returns a list of predictions with "
                    "failure probabilities, estimated costs, and recommended preventive actions. "
                    "Use this first to understand the home's risk profile."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "generate_alerts",
                "description": (
                    "Generate alerts based on current tasks, predictions, and weather conditions. "
                    "Identifies overdue tasks, upcoming critical deadlines, high-risk predictions, "
                    "and weather-related concerns. Optionally accepts predictions from a prior "
                    "predict_failures call and weather data."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "predictions": {
                            "type": "array",
                            "description": "List of failure predictions from predict_failures. Pass the predictions you received earlier.",
                            "items": {"type": "object"}
                        },
                        "weather": {
                            "type": "object",
                            "description": "Weather data with 'condition' (string) and 'severe_weather' (boolean) fields.",
                            "properties": {
                                "condition": {"type": "string"},
                                "severe_weather": {"type": "boolean"}
                            }
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "optimize_schedule",
                "description": (
                    "Create an optimized maintenance schedule considering budget, time, season, "
                    "and weather constraints. Groups related tasks and prioritizes critical items. "
                    "Best used after predict_failures and generate_alerts so the schedule reflects "
                    "the latest risk assessment."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "monthly_budget": {
                            "type": "number",
                            "description": "Monthly maintenance budget in dollars. Default 500."
                        },
                        "hours_per_week": {
                            "type": "number",
                            "description": "Hours available per week for maintenance. Default 4."
                        },
                        "current_season": {
                            "type": "string",
                            "description": "Current season: spring, summer, fall, or winter.",
                            "enum": ["spring", "summer", "fall", "winter"]
                        },
                        "weather_forecast": {
                            "type": "string",
                            "description": "General weather forecast: normal, rain, snow, extreme_heat, etc."
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "add_to_calendar",
                "description": (
                    "Add a specific maintenance task to the calendar on a given date. "
                    "Use this after optimize_schedule to commit scheduled tasks to the calendar."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The ID of the maintenance task to schedule."
                        },
                        "scheduled_date": {
                            "type": "string",
                            "description": "The date to schedule the task (YYYY-MM-DD format)."
                        }
                    },
                    "required": ["task_id", "scheduled_date"]
                }
            },
            {
                "name": "get_maintenance_guide",
                "description": (
                    "Get a detailed step-by-step maintenance guide for a specific task, "
                    "including tools needed, materials, safety precautions, cost breakdown, "
                    "and when to call a professional. Useful for DIY tasks."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The ID of the maintenance task to get a guide for."
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "optimize_costs",
                "description": (
                    "Analyze all maintenance tasks and find cost optimization opportunities: "
                    "DIY vs professional trade-offs, bulk purchasing, task bundling for contractor "
                    "discounts, and preventive vs reactive cost comparisons."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "annual_budget": {
                            "type": "number",
                            "description": "Annual maintenance budget in dollars. Default 6000."
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "get_task_list",
                "description": (
                    "Retrieve the current list of all maintenance tasks with their status, "
                    "priority, due dates, and cost estimates. Use this to understand the full "
                    "scope of maintenance needs before making decisions."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "filter_status": {
                            "type": "string",
                            "description": "Filter tasks by status: pending, scheduled, in_progress, completed, overdue. Leave empty for all tasks.",
                            "enum": ["pending", "scheduled", "in_progress", "completed", "overdue"]
                        },
                        "filter_category": {
                            "type": "string",
                            "description": "Filter tasks by category: hvac, plumbing, electrical, appliances, exterior, interior, landscaping, safety, seasonal, cleaning, organization. Leave empty for all categories."
                        },
                        "filter_priority": {
                            "type": "string",
                            "description": "Filter tasks by priority: critical, high, medium, low. Leave empty for all priorities.",
                            "enum": ["critical", "high", "medium", "low"]
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "update_task_status",
                "description": (
                    "Update the status of a maintenance task. Use this to mark tasks as "
                    "scheduled, in_progress, completed, or overdue."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The ID of the task to update."
                        },
                        "new_status": {
                            "type": "string",
                            "description": "The new status for the task.",
                            "enum": ["pending", "scheduled", "in_progress", "completed", "overdue"]
                        }
                    },
                    "required": ["task_id", "new_status"]
                }
            }
        ]

    def _execute_tool(self, name: str, tool_input: Dict) -> Any:
        """Dispatch tool calls to the appropriate sub-agent method."""

        if name == "predict_failures":
            if not self.home_profile:
                return {"error": "Home profile not initialized. Call initialize_home first."}
            result = asyncio.get_event_loop().run_until_complete(
                self.predictive_agent.predict_failures(self.home_profile, self.tasks)
            )
            return {"predictions": result}

        elif name == "generate_alerts":
            predictions = tool_input.get("predictions", [])
            weather = tool_input.get("weather", {"condition": "normal", "severe_weather": False})
            result = asyncio.get_event_loop().run_until_complete(
                self.alert_agent.generate_alerts(self.tasks, predictions, weather)
            )
            self.alerts = result
            return {"alerts": [asdict(a) for a in result], "total_alerts": len(result)}

        elif name == "optimize_schedule":
            constraints = {
                "monthly_budget": tool_input.get("monthly_budget", 500),
                "hours_per_week": tool_input.get("hours_per_week", 4),
                "current_season": tool_input.get("current_season", "winter"),
                "weather_forecast": tool_input.get("weather_forecast", "normal")
            }
            result = asyncio.get_event_loop().run_until_complete(
                self.scheduling_agent.optimize_schedule(self.tasks, constraints)
            )
            self.schedule = result
            return {"schedule": result, "total_scheduled": len(result)}

        elif name == "add_to_calendar":
            task_id = tool_input.get("task_id")
            scheduled_date = tool_input.get("scheduled_date")
            task = next((t for t in self.tasks if t.id == task_id), None)
            if not task:
                return {"error": f"Task '{task_id}' not found."}
            event_id = self.calendar_agent.add_maintenance_event(task, scheduled_date)
            if event_id:
                return {"success": True, "event_id": event_id, "task": task.title, "date": scheduled_date}
            return {"success": False, "error": "Failed to add event to calendar."}

        elif name == "get_maintenance_guide":
            task_id = tool_input.get("task_id")
            task = next((t for t in self.tasks if t.id == task_id), None)
            if not task:
                return {"error": f"Task '{task_id}' not found."}
            result = asyncio.get_event_loop().run_until_complete(
                self.knowledge_agent.get_maintenance_guide(task)
            )
            return {"task": task.title, "guide": result}

        elif name == "optimize_costs":
            budget = tool_input.get("annual_budget", 6000)
            result = asyncio.get_event_loop().run_until_complete(
                self.cost_agent.optimize_costs(self.tasks, budget)
            )
            return {"cost_analysis": result}

        elif name == "get_task_list":
            filtered = self.tasks
            if tool_input.get("filter_status"):
                status = TaskStatus(tool_input["filter_status"])
                filtered = [t for t in filtered if t.status == status]
            if tool_input.get("filter_category"):
                category = MaintenanceCategory(tool_input["filter_category"])
                filtered = [t for t in filtered if t.category == category]
            if tool_input.get("filter_priority"):
                priority = Priority(tool_input["filter_priority"])
                filtered = [t for t in filtered if t.priority == priority]
            return {
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "category": t.category.value,
                        "priority": t.priority.value,
                        "status": t.status.value,
                        "next_due": t.next_due,
                        "estimated_cost": t.estimated_cost,
                        "estimated_hours": t.estimated_hours,
                        "requires_professional": t.requires_professional,
                        "season_dependent": t.season_dependent,
                        "weather_dependent": t.weather_dependent,
                        "last_completed": t.last_completed
                    }
                    for t in filtered
                ],
                "total_tasks": len(filtered)
            }

        elif name == "update_task_status":
            task_id = tool_input.get("task_id")
            new_status = tool_input.get("new_status")
            task = next((t for t in self.tasks if t.id == task_id), None)
            if not task:
                return {"error": f"Task '{task_id}' not found."}
            task.status = TaskStatus(new_status)
            if new_status == "completed":
                task.last_completed = datetime.now().isoformat()
                task.next_due = (datetime.now() + timedelta(days=task.frequency_days)).isoformat()
            return {
                "success": True,
                "task": task.title,
                "old_status": task.status.value,
                "new_status": new_status
            }

        else:
            return {"error": f"Unknown tool: {name}"}

    async def run(self, task_description: str, max_iterations: int = 20) -> str:
        """Run the agentic loop: the coordinator LLM decides which tools to use and adapts."""

        system_prompt = (
            "You are a home maintenance coordinator. You have tools to predict failures, "
            "generate alerts, optimize schedules, manage calendars, look up guides, and "
            "optimize costs. Analyze the home's current state and take appropriate actions.\n\n"
            "Consider:\n"
            "- Predictions should inform scheduling: if a system has high failure risk, "
            "prioritize its maintenance.\n"
            "- Costs should constrain plans: compare preventive cost vs failure cost to "
            "decide what's worth doing now.\n"
            "- Alerts should trigger re-prioritization: overdue or critical items need "
            "immediate attention.\n"
            "- Guides are useful for upcoming DIY tasks to help the homeowner prepare.\n\n"
            "Work through the analysis step by step. Start by understanding the current "
            "task list, then predict failures, generate alerts, optimize the schedule and "
            "costs, and add important items to the calendar. Adapt your plan based on what "
            "you discover at each step. Provide a final summary of actions taken and "
            "recommendations."
        )

        messages = [{"role": "user", "content": task_description}]
        final_response = ""

        for i in range(max_iterations):
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=system_prompt,
                tools=self._get_tool_definitions(),
                messages=messages
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                # Extract the final text response
                for block in response.content:
                    if hasattr(block, "text"):
                        final_response += block.text
                break

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"  [Tool Call] {block.name}({json.dumps(block.input, default=str)[:100]})")
                        result = self._execute_tool(block.name, block.input)
                        print(f"  [Tool Result] {block.name} -> {json.dumps(result, default=str)[:150]}...")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, default=str) if isinstance(result, (dict, list)) else str(result)
                        })
                messages.append({"role": "user", "content": tool_results})

        return final_response

    async def run_daily_analysis(self):
        """Run daily analysis using the agentic loop."""

        print("\nHOME MAINTENANCE AGENT - Daily Analysis")
        print("=" * 70)

        if not self.home_profile:
            print("ERROR: Home profile not initialized.")
            return None

        now = datetime.now()
        home = self.home_profile

        task_description = (
            f"Today is {now.strftime('%Y-%m-%d')}. Please perform a comprehensive daily "
            f"maintenance analysis for this home.\n\n"
            f"Home Profile:\n"
            f"- Age: {home.home_age} years\n"
            f"- Size: {home.square_footage} sq ft\n"
            f"- Bedrooms: {home.num_bedrooms}, Bathrooms: {home.num_bathrooms}\n"
            f"- HVAC: {home.hvac_type} ({home.hvac_age} years old)\n"
            f"- Roof: {home.roof_age} years old\n"
            f"- Location: {home.location} (Climate: {home.climate_zone})\n"
            f"- Has basement: {home.has_basement}, attic: {home.has_attic}, garage: {home.has_garage}\n\n"
            f"The home currently has {len(self.tasks)} maintenance tasks tracked. "
            f"Please review the task list, predict potential failures, generate any necessary "
            f"alerts, optimize the schedule and costs, and add critical items to the calendar. "
            f"Provide a final summary with your key findings and recommendations."
        )

        result = await self.run(task_description)

        print("\n" + "=" * 70)
        print("ANALYSIS RESULTS")
        print("=" * 70)
        print(result)
        print("\n" + "=" * 70)
        print("Daily analysis complete!")

        return result

    def save_state(self, filepath: str = "home_maintenance_state.json"):
        """Save system state."""

        state = {
            "home_profile": asdict(self.home_profile) if self.home_profile else None,
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "category": t.category.value,
                    "description": t.description,
                    "priority": t.priority.value,
                    "frequency_days": t.frequency_days,
                    "last_completed": t.last_completed,
                    "next_due": t.next_due,
                    "estimated_cost": t.estimated_cost,
                    "estimated_hours": t.estimated_hours,
                    "requires_professional": t.requires_professional,
                    "status": t.status.value
                }
                for t in self.tasks
            ],
            "alerts": [asdict(a) for a in self.alerts],
            "schedule": self.schedule
        }

        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)

        print(f"\nState saved to {filepath}")

async def main():
    """Run the agentic home maintenance system."""

    print("HOME MAINTENANCE AGENT")
    print("=" * 70)
    print("Agentic Multi-Tool System for Proactive Home Care")
    print("=" * 70)

    # Initialize system
    orchestrator = HomeMaintenanceOrchestrator()

    # Set up home profile
    home = HomeProfile(
        home_age=15,
        square_footage=2500,
        num_bedrooms=4,
        num_bathrooms=3,
        has_basement=True,
        has_attic=True,
        has_garage=True,
        hvac_type="Central AC + Gas Furnace",
        hvac_age=12,
        roof_age=8,
        location="Seattle, WA",
        climate_zone="Marine"
    )

    print(f"\nHome Profile:")
    print(f"  Age: {home.home_age} years")
    print(f"  Size: {home.square_footage} sq ft")
    print(f"  HVAC: {home.hvac_type} ({home.hvac_age} years old)")
    print(f"  Location: {home.location}")

    orchestrator.initialize_home(home)

    print(f"\nInitialized with {len(orchestrator.tasks)} baseline tasks")

    # Run daily analysis via the agentic loop
    await orchestrator.run_daily_analysis()

    # Save state
    orchestrator.save_state()

    print("\n" + "=" * 70)
    print("System ready! Run daily for continuous monitoring.")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
