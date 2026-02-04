#!/usr/bin/env python3
"""
Calendar Integration - Google Calendar and Outlook
Real API integration for reading events and creating tasks.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class CalendarEvent:
    id: str
    title: str
    start_time: str
    end_time: str
    attendees: List[str]
    location: Optional[str]
    description: Optional[str]

class GoogleCalendarIntegration:
    """Real Google Calendar API integration."""
    
    def __init__(self, credentials_path: str = "credentials.json"):
        self.credentials_path = credentials_path
        self.service = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Google Calendar API."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
            
            creds = None
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if os.path.exists(self.credentials_path):
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, SCOPES)
                        creds = flow.run_local_server(port=0)
                
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=creds)
            
        except Exception as e:
            print(f"⚠️  Google Calendar setup needed: {e}")
            self.service = None
    
    def get_todays_events(self) -> List[CalendarEvent]:
        """Get today's calendar events."""
        
        if not self.service:
            return self._mock_events()
        
        try:
            now = datetime.utcnow()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_of_day,
                timeMax=end_of_day,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return [
                CalendarEvent(
                    id=event['id'],
                    title=event.get('summary', 'No title'),
                    start_time=event['start'].get('dateTime', event['start'].get('date')),
                    end_time=event['end'].get('dateTime', event['end'].get('date')),
                    attendees=[a.get('email') for a in event.get('attendees', [])],
                    location=event.get('location'),
                    description=event.get('description')
                )
                for event in events
            ]
            
        except Exception as e:
            print(f"Error fetching events: {e}")
            return self._mock_events()
    
    def get_upcoming_events(self, days: int = 7) -> List[CalendarEvent]:
        """Get upcoming events for next N days."""
        
        if not self.service:
            return self._mock_events()
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            end_date = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end_date,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return [
                CalendarEvent(
                    id=event['id'],
                    title=event.get('summary', 'No title'),
                    start_time=event['start'].get('dateTime', event['start'].get('date')),
                    end_time=event['end'].get('dateTime', event['end'].get('date')),
                    attendees=[a.get('email') for a in event.get('attendees', [])],
                    location=event.get('location'),
                    description=event.get('description')
                )
                for event in events
            ]
            
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def _mock_events(self) -> List[CalendarEvent]:
        """Mock events for demo."""
        now = datetime.now()
        return [
            CalendarEvent(
                id="mock_1",
                title="Team standup",
                start_time=(now + timedelta(hours=1)).isoformat(),
                end_time=(now + timedelta(hours=1, minutes=30)).isoformat(),
                attendees=["team@example.com"],
                location="Zoom",
                description="Daily standup"
            ),
            CalendarEvent(
                id="mock_2",
                title="Product review",
                start_time=(now + timedelta(hours=3)).isoformat(),
                end_time=(now + timedelta(hours=4)).isoformat(),
                attendees=["product@example.com"],
                location="Conference Room A",
                description="Review Q1 roadmap"
            )
        ]

class OutlookCalendarIntegration:
    """Real Outlook/Microsoft Graph API integration."""
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        self.client_id = client_id or os.getenv("OUTLOOK_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("OUTLOOK_CLIENT_SECRET")
        self.access_token = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Microsoft Graph API."""
        try:
            import msal
            
            authority = "https://login.microsoftonline.com/common"
            scopes = ["https://graph.microsoft.com/Calendars.Read"]
            
            app = msal.PublicClientApplication(
                self.client_id,
                authority=authority
            )
            
            # Try to get token from cache
            accounts = app.get_accounts()
            if accounts:
                result = app.acquire_token_silent(scopes, account=accounts[0])
                if result:
                    self.access_token = result['access_token']
                    return
            
            # Interactive login
            result = app.acquire_token_interactive(scopes)
            if "access_token" in result:
                self.access_token = result['access_token']
            
        except Exception as e:
            print(f"⚠️  Outlook Calendar setup needed: {e}")
            self.access_token = None
    
    def get_todays_events(self) -> List[CalendarEvent]:
        """Get today's calendar events."""
        
        if not self.access_token:
            return []
        
        try:
            import requests
            
            now = datetime.utcnow()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat() + 'Z'
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"https://graph.microsoft.com/v1.0/me/calendarview?startDateTime={start_of_day}&endDateTime={end_of_day}"
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            events = response.json().get('value', [])
            
            return [
                CalendarEvent(
                    id=event['id'],
                    title=event.get('subject', 'No title'),
                    start_time=event['start']['dateTime'],
                    end_time=event['end']['dateTime'],
                    attendees=[a['emailAddress']['address'] for a in event.get('attendees', [])],
                    location=event.get('location', {}).get('displayName'),
                    description=event.get('bodyPreview')
                )
                for event in events
            ]
            
        except Exception as e:
            print(f"Error fetching Outlook events: {e}")
            return []

class CalendarTaskExtractor:
    """Extract tasks from calendar events using AI."""
    
    def __init__(self, api_key: str):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def extract_tasks_from_events(self, events: List[CalendarEvent]) -> List[Dict]:
        """Analyze calendar events and extract actionable tasks."""
        
        if not events:
            return []
        
        events_text = "\n".join([
            f"- {e.title} ({e.start_time} to {e.end_time})"
            f"{f' | {e.description}' if e.description else ''}"
            for e in events
        ])
        
        prompt = f"""Analyze these calendar events and extract actionable tasks.

Events:
{events_text}

For each event, identify:
1. Preparation tasks (before the meeting)
2. Follow-up tasks (after the meeting)
3. Deliverables mentioned

Return JSON array:
[
  {{
    "title": "Prepare slides for product review",
    "description": "Create deck with Q1 metrics",
    "priority": "high",
    "deadline": "2026-02-03T14:00:00",
    "estimated_hours": 2.0,
    "related_event": "Product review"
  }}
]"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        # Extract JSON
        import re
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        
        return []

async def main():
    """Demo calendar integration."""
    
    print("📅 CALENDAR INTEGRATION")
    print("="*70)
    
    # Google Calendar
    print("\n🔵 Google Calendar")
    google = GoogleCalendarIntegration()
    events = google.get_todays_events()
    
    print(f"Found {len(events)} events today:")
    for event in events:
        print(f"  • {event.title} at {event.start_time}")
    
    # Extract tasks from events
    if os.getenv("ANTHROPIC_API_KEY"):
        print("\n🤖 Extracting tasks from calendar...")
        extractor = CalendarTaskExtractor(os.getenv("ANTHROPIC_API_KEY"))
        tasks = await extractor.extract_tasks_from_events(events)
        
        print(f"Extracted {len(tasks)} tasks:")
        for task in tasks:
            print(f"  • {task['title']} (Priority: {task['priority']})")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
