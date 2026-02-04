#!/usr/bin/env python3
"""
Slack/Teams Integration - Meeting reminders and notifications
Real API integration.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict

class SlackIntegration:
    """Real Slack API integration."""
    
    def __init__(self, bot_token: str = None):
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Slack client."""
        try:
            from slack_sdk import WebClient
            from slack_sdk.errors import SlackApiError
            
            if self.bot_token:
                self.client = WebClient(token=self.bot_token)
                # Test connection
                self.client.auth_test()
            else:
                print("⚠️  Set SLACK_BOT_TOKEN environment variable")
                
        except Exception as e:
            print(f"⚠️  Slack setup needed: {e}")
            self.client = None
    
    def send_message(self, channel: str, text: str, blocks: List[Dict] = None):
        """Send message to Slack channel."""
        
        if not self.client:
            print(f"[MOCK] Would send to {channel}: {text}")
            return
        
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            return response
            
        except Exception as e:
            print(f"Error sending Slack message: {e}")
            return None
    
    def send_daily_briefing(self, channel: str, briefing: Dict):
        """Send daily briefing to Slack."""
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📋 Daily Briefing - {briefing['date']}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:*\n{briefing['summary']}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*🎯 Top Priorities:*\n" + "\n".join([
                        f"{i+1}. {p}" for i, p in enumerate(briefing['top_priorities'])
                    ])
                }
            }
        ]
        
        if briefing.get('deadline_warnings'):
            warnings_text = "\n".join([
                f"• {w['title']}: {w['hours_remaining']:.1f}h remaining"
                for w in briefing['deadline_warnings'][:3]
            ])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*⚠️ Deadline Warnings:*\n{warnings_text}"
                }
            })
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*💡 Suggested Focus:*\n{briefing['suggested_focus']}"
            }
        })
        
        return self.send_message(channel, "Daily Briefing", blocks)
    
    def send_meeting_reminder(self, channel: str, meeting: Dict):
        """Send meeting reminder."""
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"⏰ Meeting Reminder"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{meeting['title']}*\n"
                           f"📅 {meeting['start_time']}\n"
                           f"📍 {meeting.get('location', 'No location')}\n"
                           f"👥 {len(meeting.get('attendees', []))} attendees"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Join Meeting"
                        },
                        "url": meeting.get('join_url', '#'),
                        "action_id": "join_meeting"
                    }
                ]
            }
        ]
        
        return self.send_message(channel, f"Meeting: {meeting['title']}", blocks)
    
    def send_deadline_alert(self, channel: str, task: Dict):
        """Send deadline alert."""
        
        urgency = "🔴 CRITICAL" if task['hours_remaining'] < 24 else "🟡 WARNING"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{urgency}: *{task['title']}*\n"
                           f"⏰ {task['hours_remaining']:.1f} hours remaining\n"
                           f"📊 Estimated: {task['estimated_hours']}h"
                }
            }
        ]
        
        return self.send_message(channel, f"Deadline Alert: {task['title']}", blocks)

class TeamsIntegration:
    """Real Microsoft Teams API integration."""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.getenv("TEAMS_WEBHOOK_URL")
    
    def send_message(self, text: str, title: str = None):
        """Send message to Teams via webhook."""
        
        if not self.webhook_url:
            print(f"[MOCK] Would send to Teams: {text}")
            return
        
        try:
            import requests
            
            payload = {
                "@type": "MessageCard",
                "@context": "https://schema.org/extensions",
                "summary": title or "Notification",
                "themeColor": "0078D4",
                "title": title,
                "text": text
            }
            
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return response
            
        except Exception as e:
            print(f"Error sending Teams message: {e}")
            return None
    
    def send_daily_briefing(self, briefing: Dict):
        """Send daily briefing to Teams."""
        
        text = f"""
**Summary:**
{briefing['summary']}

**🎯 Top Priorities:**
{chr(10).join([f"{i+1}. {p}" for i, p in enumerate(briefing['top_priorities'])])}

**💡 Suggested Focus:**
{briefing['suggested_focus']}
"""
        
        if briefing.get('deadline_warnings'):
            warnings = "\n".join([
                f"• {w['title']}: {w['hours_remaining']:.1f}h remaining"
                for w in briefing['deadline_warnings'][:3]
            ])
            text += f"\n\n**⚠️ Deadline Warnings:**\n{warnings}"
        
        return self.send_message(text, f"📋 Daily Briefing - {briefing['date']}")
    
    def send_meeting_reminder(self, meeting: Dict):
        """Send meeting reminder to Teams."""
        
        text = f"""
**{meeting['title']}**

📅 {meeting['start_time']}
📍 {meeting.get('location', 'No location')}
👥 {len(meeting.get('attendees', []))} attendees
"""
        
        return self.send_message(text, "⏰ Meeting Reminder")
    
    def send_deadline_alert(self, task: Dict):
        """Send deadline alert to Teams."""
        
        urgency = "🔴 CRITICAL" if task['hours_remaining'] < 24 else "🟡 WARNING"
        
        text = f"""
{urgency}: **{task['title']}**

⏰ {task['hours_remaining']:.1f} hours remaining
📊 Estimated: {task['estimated_hours']}h
"""
        
        return self.send_message(text, "Deadline Alert")

class NotificationManager:
    """Manage notifications across Slack and Teams."""
    
    def __init__(self):
        self.slack = SlackIntegration()
        self.teams = TeamsIntegration()
    
    def send_daily_briefing(self, briefing: Dict, slack_channel: str = None):
        """Send daily briefing to all platforms."""
        
        if slack_channel:
            self.slack.send_daily_briefing(slack_channel, briefing)
        
        self.teams.send_daily_briefing(briefing)
    
    def send_meeting_reminders(self, meetings: List[Dict], slack_channel: str = None):
        """Send meeting reminders."""
        
        for meeting in meetings:
            # Send reminder 15 minutes before
            start_time = datetime.fromisoformat(meeting['start_time'])
            now = datetime.now()
            
            if 0 < (start_time - now).total_seconds() / 60 < 15:
                if slack_channel:
                    self.slack.send_meeting_reminder(slack_channel, meeting)
                self.teams.send_meeting_reminder(meeting)
    
    def send_deadline_alerts(self, tasks: List[Dict], slack_channel: str = None):
        """Send deadline alerts for urgent tasks."""
        
        for task in tasks:
            if task['hours_remaining'] < 24:
                if slack_channel:
                    self.slack.send_deadline_alert(slack_channel, task)
                self.teams.send_deadline_alert(task)

def main():
    """Demo Slack/Teams integration."""
    
    print("💬 SLACK/TEAMS INTEGRATION")
    print("="*70)
    
    # Mock briefing
    briefing = {
        "date": "2026-02-03",
        "summary": "You have 5 active tasks with 2 approaching deadlines.",
        "top_priorities": [
            "Schedule team meeting (6h deadline)",
            "Review design mockups (24h deadline)",
            "Finish product spec (48h deadline)"
        ],
        "suggested_focus": "Start with team meeting scheduling, then design review.",
        "deadline_warnings": [
            {"title": "Schedule team meeting", "hours_remaining": 6.0, "estimated_hours": 0.5}
        ]
    }
    
    # Mock meeting
    meeting = {
        "title": "Team Standup",
        "start_time": (datetime.now() + timedelta(minutes=10)).isoformat(),
        "location": "Zoom",
        "attendees": ["team@example.com"],
        "join_url": "https://zoom.us/j/123456"
    }
    
    # Send notifications
    manager = NotificationManager()
    
    print("\n📤 Sending daily briefing...")
    manager.send_daily_briefing(briefing, slack_channel="#general")
    
    print("\n📤 Sending meeting reminder...")
    manager.send_meeting_reminders([meeting], slack_channel="#general")
    
    print("\n" + "="*70)
    print("✅ Notifications sent (or mocked if credentials not set)")

if __name__ == "__main__":
    main()
