#!/usr/bin/env python3
"""
Complete integration example - All features working together
"""

import os
import sys
import asyncio
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chief import ChiefOfStaff, Priority
from integrations.calendar_integration import GoogleCalendarIntegration, CalendarTaskExtractor
from integrations.email_integration import GmailIntegration, EmailTaskExtractor
from integrations.slack_teams_integration import NotificationManager
from integrations.habit_tracking import HabitTracker, HabitType, HabitInsightGenerator

async def main():
    """Run complete integrated workflow."""
    
    print("👔 PERSONAL CHIEF OF STAFF - FULL INTEGRATION")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
    print("="*70)
    
    # Initialize
    chief = ChiefOfStaff()
    notifier = NotificationManager()
    tracker = HabitTracker()
    
    # ========================================================================
    # STEP 1: Import from Calendar
    # ========================================================================
    
    print("\n📅 STEP 1: Calendar Integration")
    print("-"*70)
    
    calendar = GoogleCalendarIntegration()
    events = calendar.get_todays_events()
    
    print(f"Found {len(events)} events today:")
    for event in events:
        start = datetime.fromisoformat(event.start_time.replace('Z', '+00:00'))
        print(f"  • {event.title} at {start.strftime('%I:%M %p')}")
    
    # Extract tasks from events
    if events and chief.api_key:
        print("\n🤖 Extracting tasks from calendar events...")
        extractor = CalendarTaskExtractor(chief.api_key)
        calendar_tasks = await extractor.extract_tasks_from_events(events)
        
        for task in calendar_tasks:
            chief.add_task(
                task['title'],
                task['description'],
                Priority[task['priority'].upper()],
                deadline=task.get('deadline'),
                estimated_hours=task['estimated_hours']
            )
        
        print(f"  ✓ Added {len(calendar_tasks)} tasks from calendar")
    
    # ========================================================================
    # STEP 2: Import from Email
    # ========================================================================
    
    print("\n\n📧 STEP 2: Email Integration")
    print("-"*70)
    
    gmail = GmailIntegration()
    emails = gmail.get_unread_emails(max_results=5)
    
    if emails:
        print(f"Found {len(emails)} unread emails:")
        for email in emails[:3]:
            print(f"  • {email['subject'][:50]}...")
        
        # Extract tasks from emails
        if chief.api_key:
            print("\n🤖 Extracting tasks from emails...")
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
    else:
        print("  No unread emails (or Gmail not configured)")
    
    # ========================================================================
    # STEP 3: Check Habits
    # ========================================================================
    
    print("\n\n🏃 STEP 3: Habit Tracking")
    print("-"*70)
    
    # Get habit insights
    habit_insights = tracker.get_insights()
    
    print("Today's habits:")
    for habit_type in [HabitType.EXERCISE, HabitType.SLEEP, HabitType.WATER]:
        habit_name = habit_type.value.capitalize()
        progress = habit_insights["goal_progress"][habit_type.value]
        
        if progress["has_goal"]:
            status = "✅" if progress["on_track"] else "⚠️"
            print(f"  {status} {habit_name}: {progress['current']:.1f}/{progress['target']:.1f} {progress['unit']}")
    
    # Generate AI insights
    if chief.api_key:
        print("\n🤖 Generating habit insights...")
        insight_gen = HabitInsightGenerator(chief.api_key)
        ai_insights = await insight_gen.generate_insights(habit_insights)
        print(f"\n{ai_insights[:200]}...")
    
    # ========================================================================
    # STEP 4: Generate Daily Briefing
    # ========================================================================
    
    print("\n\n📋 STEP 4: Daily Briefing")
    print("-"*70)
    
    if chief.api_key:
        briefing = await chief.generate_daily_briefing()
        
        # Add habit summary to briefing
        briefing_dict = {
            "date": briefing.date,
            "summary": briefing.summary,
            "top_priorities": briefing.top_priorities,
            "deadline_warnings": briefing.deadline_warnings,
            "suggested_focus": briefing.suggested_focus,
            "time_allocation": briefing.time_allocation,
            "blockers": briefing.blockers,
            "wins_yesterday": briefing.wins_yesterday
        }
    else:
        print("  ⚠️  Set ANTHROPIC_API_KEY to generate briefing")
        briefing_dict = None
    
    # ========================================================================
    # STEP 5: Send Notifications
    # ========================================================================
    
    print("\n\n💬 STEP 5: Notifications")
    print("-"*70)
    
    if briefing_dict:
        # Send to Slack/Teams
        print("Sending daily briefing to Slack/Teams...")
        notifier.send_daily_briefing(briefing_dict, slack_channel="#general")
        print("  ✓ Briefing sent")
        
        # Send meeting reminders
        if events:
            print("\nSending meeting reminders...")
            meeting_data = [
                {
                    "title": e.title,
                    "start_time": e.start_time,
                    "location": e.location or "No location",
                    "attendees": e.attendees,
                    "join_url": "#"
                }
                for e in events
            ]
            notifier.send_meeting_reminders(meeting_data, slack_channel="#general")
            print(f"  ✓ {len(events)} reminders sent")
        
        # Send deadline alerts
        if briefing_dict["deadline_warnings"]:
            print("\nSending deadline alerts...")
            notifier.send_deadline_alerts(
                briefing_dict["deadline_warnings"],
                slack_channel="#general"
            )
            print(f"  ✓ {len(briefing_dict['deadline_warnings'])} alerts sent")
    
    # ========================================================================
    # STEP 6: Focus Recommendation
    # ========================================================================
    
    print("\n\n🎯 STEP 6: Focus Recommendation")
    print("-"*70)
    
    if chief.api_key:
        context = f"Just finished morning routine. Have {len(events)} meetings today."
        recommendation = await chief.what_should_i_focus_on(context)
    else:
        print("  ⚠️  Set ANTHROPIC_API_KEY for focus recommendations")
    
    # ========================================================================
    # STEP 7: Save State
    # ========================================================================
    
    print("\n\n💾 STEP 7: Save State")
    print("-"*70)
    
    chief.save_state()
    tracker.save_state()
    print("  ✓ All data saved")
    
    # ========================================================================
    # Summary
    # ========================================================================
    
    print("\n\n" + "="*70)
    print("✅ INTEGRATION COMPLETE")
    print("="*70)
    print(f"\nSummary:")
    print(f"  • Calendar events: {len(events)}")
    print(f"  • Unread emails: {len(emails) if emails else 0}")
    print(f"  • Total tasks: {len(chief.tasks)}")
    print(f"  • Active goals: {len(chief.goals)}")
    print(f"  • Habit streaks tracked: {len([s for s in habit_insights['streaks'].values() if s > 0])}")
    print(f"\nAll systems operational! 🚀")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
