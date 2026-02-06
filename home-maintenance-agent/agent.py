#!/usr/bin/env python3
"""
Home Maintenance Agent - Multi-Agent System for Proactive Home Care
Sophisticated autonomous system that predicts, schedules, and manages all home maintenance.
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
            model="claude-3-5-sonnet-20241022",
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
            model="claude-3-5-sonnet-20241022",
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
            print(f"⚠️  Calendar integration not configured: {e}")
    
    def add_maintenance_event(self, task: MaintenanceTask, scheduled_date: str) -> Optional[str]:
        """Add maintenance task to Google Calendar."""
        
        if not self.calendar_service:
            print(f"[MOCK] Would add to calendar: {task.title} on {scheduled_date}")
            return f"mock_event_{task.id}"
        
        try:
            event = {
                'summary': f"🏠 {task.title}",
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
                'summary': f"⚠️ Maintenance Alert",
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
            model="claude-3-5-sonnet-20241022",
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
            model="claude-3-5-sonnet-20241022",
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
    """Main orchestrator coordinating all agents."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        # Initialize agents
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
        ]
        
        self.tasks.extend(baseline)
    
    async def run_daily_analysis(self):
        """Run daily analysis and generate alerts."""
        
        print("\n🏠 HOME MAINTENANCE AGENT - Daily Analysis")
        print("="*70)
        
        # 1. Predictive analysis
        print("\n🔮 Running predictive analysis...")
        predictions = await self.predictive_agent.predict_failures(
            self.home_profile,
            self.tasks
        )
        
        print(f"   Found {len(predictions)} potential issues")
        for pred in predictions[:3]:
            print(f"   ⚠️  {pred['system']}: {pred['failure_probability']}% risk")
        
        # 2. Generate alerts
        print("\n🚨 Generating alerts...")
        weather = {"condition": "normal", "severe_weather": False}
        alerts = await self.alert_agent.generate_alerts(
            self.tasks,
            predictions,
            weather
        )
        
        print(f"   Generated {len(alerts)} alerts")
        for alert in alerts[:5]:
            icon = "🔴" if alert.severity == "critical" else "🟡" if alert.severity == "high" else "🟢"
            print(f"   {icon} {alert.message}")
        
        # 3. Optimize schedule
        print("\n📅 Optimizing schedule...")
        constraints = {
            "monthly_budget": 500,
            "hours_per_week": 4,
            "current_season": "winter",
            "weather_forecast": "normal"
        }
        
        schedule = await self.scheduling_agent.optimize_schedule(
            self.tasks,
            constraints
        )
        
        print(f"   Scheduled {len(schedule)} tasks")
        for item in schedule[:3]:
            print(f"   📌 {item.get('scheduled_date')}: {item.get('reasoning', 'N/A')[:60]}...")
        
        # 4. Add to calendar
        print("\n📆 Adding to calendar...")
        for item in schedule[:3]:
            task = next((t for t in self.tasks if t.id == item.get('task_id')), None)
            if task:
                event_id = self.calendar_agent.add_maintenance_event(
                    task,
                    item.get('scheduled_date')
                )
                if event_id:
                    print(f"   ✓ Added: {task.title}")
        
        # 5. Cost optimization
        print("\n💰 Analyzing costs...")
        cost_analysis = await self.cost_agent.optimize_costs(
            self.tasks,
            6000  # Annual budget
        )
        
        if cost_analysis:
            print(f"   Original cost: ${cost_analysis.get('total_estimated_cost', 0):.2f}")
            print(f"   Optimized cost: ${cost_analysis.get('optimized_cost', 0):.2f}")
            print(f"   Savings: ${cost_analysis.get('savings', 0):.2f}")
        
        # 6. Generate guides for upcoming tasks
        print("\n📚 Generating maintenance guides...")
        upcoming = [t for t in self.tasks if t.status == TaskStatus.PENDING][:2]
        for task in upcoming:
            guide = await self.knowledge_agent.get_maintenance_guide(task)
            if guide:
                print(f"   ✓ Guide ready: {task.title}")
        
        self.alerts = alerts
        self.schedule = schedule
        
        print("\n" + "="*70)
        print("✅ Daily analysis complete!")
        
        return {
            "predictions": predictions,
            "alerts": alerts,
            "schedule": schedule,
            "cost_analysis": cost_analysis
        }
    
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
        
        print(f"\n💾 State saved to {filepath}")

async def main():
    """Demo the home maintenance system."""
    
    print("🏠 HOME MAINTENANCE AGENT")
    print("="*70)
    print("Multi-Agent System for Proactive Home Care")
    print("="*70)
    
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
    
    print(f"\n🏡 Home Profile:")
    print(f"   Age: {home.home_age} years")
    print(f"   Size: {home.square_footage} sq ft")
    print(f"   HVAC: {home.hvac_type} ({home.hvac_age} years old)")
    print(f"   Location: {home.location}")
    
    orchestrator.initialize_home(home)
    
    print(f"\n📋 Initialized with {len(orchestrator.tasks)} baseline tasks")
    
    # Run daily analysis
    results = await orchestrator.run_daily_analysis()
    
    # Save state
    orchestrator.save_state()
    
    print("\n" + "="*70)
    print("System ready! Run daily for continuous monitoring.")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
