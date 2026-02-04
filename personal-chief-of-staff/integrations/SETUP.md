# Integration Setup Guide

Complete guide for setting up all integrations with the Personal Chief of Staff.

## Overview

The Chief of Staff supports 6 major integrations:
1. **Calendar** (Google Calendar, Outlook)
2. **Email** (Gmail, IMAP)
3. **Slack** (Bot API)
4. **Microsoft Teams** (Webhooks)
5. **Habit Tracking** (Built-in)

## Installation

```bash
cd integrations
pip install -r requirements.txt
```

## 1. Google Calendar Integration

### Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to this directory

### Usage

```python
from calendar_integration import GoogleCalendarIntegration

calendar = GoogleCalendarIntegration("credentials.json")
events = calendar.get_todays_events()

for event in events:
    print(f"{event.title} at {event.start_time}")
```

### Features

- ✅ Read today's events
- ✅ Get upcoming events (7 days)
- ✅ Extract tasks from event descriptions
- ✅ Auto-add prep/follow-up tasks

## 2. Outlook Calendar Integration

### Setup

1. Go to [Azure Portal](https://portal.azure.com/)
2. Register an application
3. Add Microsoft Graph API permissions: `Calendars.Read`
4. Set environment variables:

```bash
export OUTLOOK_CLIENT_ID=your_client_id
export OUTLOOK_CLIENT_SECRET=your_client_secret
```

### Usage

```python
from calendar_integration import OutlookCalendarIntegration

outlook = OutlookCalendarIntegration()
events = outlook.get_todays_events()
```

## 3. Gmail Integration

### Setup

1. Use same Google Cloud project as Calendar
2. Enable Gmail API
3. Use same `credentials.json`

### Usage

```python
from email_integration import GmailIntegration

gmail = GmailIntegration("credentials.json")
emails = gmail.get_unread_emails(max_results=10)

for email in emails:
    print(f"{email['subject']} from {email['from']}")
```

### Features

- ✅ Read unread emails
- ✅ Extract action items from emails
- ✅ Auto-create tasks with deadlines
- ✅ Priority detection

## 4. IMAP Email Integration

For non-Gmail providers (Outlook, Yahoo, etc.)

### Setup

```bash
export EMAIL_SERVER=imap.gmail.com  # or your provider
export EMAIL_ADDRESS=your@email.com
export EMAIL_PASSWORD=your_app_password
```

### Usage

```python
from email_integration import IMAPIntegration

imap = IMAPIntegration(
    server="imap.gmail.com",
    email="your@email.com",
    password="your_password"
)

emails = imap.get_unread_emails()
```

## 5. Slack Integration

### Setup

1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app
3. Add Bot Token Scopes:
   - `chat:write`
   - `chat:write.public`
4. Install app to workspace
5. Copy Bot User OAuth Token

```bash
export SLACK_BOT_TOKEN=xoxb-your-token
```

### Usage

```python
from slack_teams_integration import SlackIntegration

slack = SlackIntegration()

# Send daily briefing
slack.send_daily_briefing("#general", briefing_data)

# Send meeting reminder
slack.send_meeting_reminder("#general", meeting_data)

# Send deadline alert
slack.send_deadline_alert("#general", task_data)
```

### Features

- ✅ Daily briefings
- ✅ Meeting reminders (15 min before)
- ✅ Deadline alerts
- ✅ Rich formatting with blocks

## 6. Microsoft Teams Integration

### Setup

1. Go to your Teams channel
2. Click "..." → Connectors → Incoming Webhook
3. Create webhook and copy URL

```bash
export TEAMS_WEBHOOK_URL=your_webhook_url
```

### Usage

```python
from slack_teams_integration import TeamsIntegration

teams = TeamsIntegration()

# Send daily briefing
teams.send_daily_briefing(briefing_data)

# Send meeting reminder
teams.send_meeting_reminder(meeting_data)
```

## 7. Habit Tracking

No setup required - built-in!

### Usage

```python
from habit_tracking import HabitTracker, HabitType

tracker = HabitTracker()

# Set goals
tracker.set_goal(HabitType.EXERCISE, 1.0, "daily", "hours")
tracker.set_goal(HabitType.SLEEP, 8.0, "daily", "hours")

# Log habits
tracker.log_habit(HabitType.EXERCISE, 0.5, "Morning run", mood=4)
tracker.log_habit(HabitType.SLEEP, 7.5)

# Get insights
insights = tracker.get_insights()
print(f"Exercise streak: {insights['streaks']['exercise']} days")
```

### Features

- ✅ Track 6 habit types (exercise, sleep, meditation, reading, water, nutrition)
- ✅ Set goals (daily/weekly)
- ✅ Calculate streaks
- ✅ Weekly summaries
- ✅ Progress tracking
- ✅ AI-powered insights

## Complete Integration Example

```python
#!/usr/bin/env python3
"""
Complete integration example
"""

import asyncio
from chief import ChiefOfStaff, Priority
from integrations.calendar_integration import GoogleCalendarIntegration, CalendarTaskExtractor
from integrations.email_integration import GmailIntegration, EmailTaskExtractor
from integrations.slack_teams_integration import NotificationManager
from integrations.habit_tracking import HabitTracker, HabitType

async def main():
    # Initialize Chief of Staff
    chief = ChiefOfStaff()
    
    # 1. Import from calendar
    print("📅 Importing from calendar...")
    calendar = GoogleCalendarIntegration()
    events = calendar.get_todays_events()
    
    extractor = CalendarTaskExtractor(chief.api_key)
    calendar_tasks = await extractor.extract_tasks_from_events(events)
    
    for task in calendar_tasks:
        chief.add_task(
            task['title'],
            task['description'],
            Priority[task['priority'].upper()],
            deadline=task['deadline'],
            estimated_hours=task['estimated_hours']
        )
    
    print(f"  ✓ Added {len(calendar_tasks)} tasks from calendar")
    
    # 2. Import from email
    print("\n📧 Importing from email...")
    gmail = GmailIntegration()
    emails = gmail.get_unread_emails(max_results=5)
    
    email_extractor = EmailTaskExtractor(chief.api_key)
    email_tasks = await email_extractor.extract_tasks_from_emails(emails)
    
    for task in email_tasks:
        chief.add_task(
            task.subject,
            task.body,
            Priority[task.priority.upper()],
            estimated_hours=task.estimated_hours
        )
    
    print(f"  ✓ Added {len(email_tasks)} tasks from email")
    
    # 3. Generate daily briefing
    print("\n📋 Generating daily briefing...")
    briefing = await chief.generate_daily_briefing()
    
    # 4. Send to Slack/Teams
    print("\n💬 Sending notifications...")
    notifier = NotificationManager()
    notifier.send_daily_briefing(briefing.__dict__, slack_channel="#general")
    
    # 5. Check habits
    print("\n🏃 Checking habits...")
    tracker = HabitTracker()
    insights = tracker.get_insights()
    
    print(f"  Exercise streak: {insights['streaks']['exercise']} days")
    print(f"  Sleep average: {insights['weekly_summaries']['sleep']['average']:.1f}h")
    
    # 6. Save state
    chief.save_state()
    
    print("\n✅ All integrations complete!")

if __name__ == "__main__":
    asyncio.run(main())
```

## Environment Variables Summary

```bash
# Anthropic (required)
export ANTHROPIC_API_KEY=your_key

# Google (Calendar + Gmail)
# Use credentials.json file instead

# Outlook
export OUTLOOK_CLIENT_ID=your_client_id
export OUTLOOK_CLIENT_SECRET=your_client_secret

# IMAP Email
export EMAIL_SERVER=imap.gmail.com
export EMAIL_ADDRESS=your@email.com
export EMAIL_PASSWORD=your_password

# Slack
export SLACK_BOT_TOKEN=xoxb-your-token

# Teams
export TEAMS_WEBHOOK_URL=your_webhook_url
```

## Troubleshooting

### Google Calendar/Gmail

**Error: credentials.json not found**
- Download from Google Cloud Console
- Place in integrations/ directory

**Error: Token expired**
- Delete `token.json` and `gmail_token.json`
- Re-run to re-authenticate

### Slack

**Error: not_authed**
- Check SLACK_BOT_TOKEN is set correctly
- Verify bot is installed in workspace

**Error: channel_not_found**
- Bot needs to be invited to channel
- Use channel ID instead of name

### Teams

**Error: Webhook not found**
- Verify TEAMS_WEBHOOK_URL is correct
- Check webhook is still active in Teams

### IMAP

**Error: Authentication failed**
- Use app-specific password (not account password)
- Enable "Less secure app access" if needed

## Testing

Test each integration individually:

```bash
# Calendar
python calendar_integration.py

# Email
python email_integration.py

# Slack/Teams
python slack_teams_integration.py

# Habits
python habit_tracking.py
```

## Security Notes

1. **Never commit credentials** - Add to .gitignore:
   ```
   credentials.json
   token.json
   gmail_token.json
   .env
   ```

2. **Use environment variables** for tokens

3. **Rotate tokens** regularly

4. **Limit API scopes** to minimum required

## Next Steps

1. Set up one integration at a time
2. Test with mock data first
3. Gradually enable real APIs
4. Monitor API usage/quotas
5. Set up error notifications

## Support

- Google APIs: https://console.cloud.google.com/
- Slack API: https://api.slack.com/
- Microsoft Graph: https://developer.microsoft.com/graph
- GitHub Issues: https://github.com/ndgbg/fun-agentic-apps/issues
