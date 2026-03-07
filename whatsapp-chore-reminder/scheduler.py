"""
Background scheduler for WhatsApp chore reminders.

Polls the database every minute for reminders that are due and sends
them to all configured household members via WhatsApp.
"""

import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler(daemon=True)


def _send_due_reminders():
    """Check for due reminders and send them via WhatsApp."""
    import database as db
    import whatsapp

    reminders = db.get_pending_reminders()
    if not reminders:
        return

    phone1 = os.environ.get("HOUSEHOLD_USER1_PHONE", "").lstrip("+")
    phone2 = os.environ.get("HOUSEHOLD_USER2_PHONE", "").lstrip("+")
    phones = [p for p in [phone1, phone2] if p]

    for reminder in reminders:
        text = f"⏰ Reminder: {reminder['message']}"
        any_sent = False
        for phone in phones:
            if whatsapp.send_message(phone, text):
                any_sent = True

        if any_sent:
            db.mark_reminder_sent(reminder["id"])
            logger.info("Sent reminder #%s to %d recipients", reminder["id"], len(phones))
        else:
            logger.warning("Failed to send reminder #%s – will retry next minute", reminder["id"])


def start():
    """Start the background scheduler."""
    _scheduler.add_job(
        _send_due_reminders,
        trigger=IntervalTrigger(minutes=1),
        id="reminder_check",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Reminder scheduler started (polling every minute)")


def stop():
    """Gracefully shut down the scheduler."""
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Reminder scheduler stopped")
