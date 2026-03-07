# 🏠 WhatsApp Chore Reminder

A real WhatsApp chatbot that helps couples manage household chores together.
Both partners can message the bot in plain English to add tasks, check what needs doing, mark things done, and schedule reminders — all in WhatsApp, no app to install.

## Features

| What you can do | Example message |
|---|---|
| Add a chore | *"Add vacuuming the living room, due Friday, weekly"* |
| See the list | *"What chores are still pending?"* |
| Check overdue | *"What's overdue?"* |
| Complete a task | *"I just did the dishes"* |
| Delete a task | *"Remove the grocery run chore"* |
| Reassign | *"Assign the lawn mowing to Bob"* |
| Set a reminder | *"Remind us to take out the bins tomorrow at 7 PM"* |
| View reminders | *"Show all upcoming reminders"* |
| Notify partner | *"Tell Alice I finished cleaning the bathroom"* |
| Summary | *"Give me a household overview"* |

## Architecture

```
app.py          Flask webhook server (receives WhatsApp messages)
agent.py        Claude claude-opus-4-6 agentic loop with 10 tools
database.py     SQLite – chores, reminders, conversation history
whatsapp.py     Meta WhatsApp Cloud API client
scheduler.py    APScheduler – fires reminders every minute
```

## Prerequisites

1. **Meta WhatsApp Business account** (free to create)
2. **Anthropic API key** — [platform.anthropic.com](https://platform.anthropic.com)
3. A public HTTPS URL for the webhook (ngrok works great for local dev)
4. Python 3.10+

## Setup

### 1. Clone & install

```bash
cd whatsapp-chore-reminder
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure `.env`

Fill in all values in `.env`:

```
ANTHROPIC_API_KEY=...

WHATSAPP_PHONE_NUMBER_ID=...   # From Meta Developer Console
WHATSAPP_ACCESS_TOKEN=...       # From Meta Developer Console
WHATSAPP_VERIFY_TOKEN=...       # Any secret string you choose

HOUSEHOLD_USER1_PHONE=+15551234567
HOUSEHOLD_USER1_NAME=Alice
HOUSEHOLD_USER2_PHONE=+15557654321
HOUSEHOLD_USER2_NAME=Bob
```

### 3. Set up Meta WhatsApp Business

1. Go to [developers.facebook.com](https://developers.facebook.com) → Create App → Business
2. Add **WhatsApp** product to your app
3. Under **WhatsApp → API Setup**:
   - Copy your **Phone Number ID** → `WHATSAPP_PHONE_NUMBER_ID`
   - Generate a **Temporary Access Token** (or create a System User token for permanent access) → `WHATSAPP_ACCESS_TOKEN`
4. Under **WhatsApp → Configuration → Webhooks**:
   - **Callback URL**: `https://your-domain.com/webhook`
   - **Verify Token**: same value as `WHATSAPP_VERIFY_TOKEN` in `.env`
   - Subscribe to the `messages` webhook field

### 4. Expose your server (local development)

```bash
# In one terminal – start the app
python app.py

# In another terminal – expose it publicly
ngrok http 5000
```

Use the ngrok HTTPS URL (e.g. `https://abc123.ngrok.io/webhook`) as your Meta webhook callback URL.

### 5. Send your first message

Text your WhatsApp Business number from one of the registered phones. Try:

> "Hi! What chores do we have?"

## Running in production

For a persistent deployment use **gunicorn** behind **nginx** or deploy to any Python-friendly host (Railway, Fly.io, Render, etc.):

```bash
pip install gunicorn
gunicorn "app:app" --bind 0.0.0.0:5000 --workers 1 --threads 4
```

> **Note:** Use a single worker (`--workers 1`) so the APScheduler thread and SQLite writes don't conflict. For high-volume deployments, swap SQLite for PostgreSQL and use Celery for task queuing.

## Conversation examples

**Adding a recurring chore:**
> You: *"Add taking out the bins every Monday morning"*
> Bot: *"✅ Added 'Take out the bins' – weekly, starting Monday. Want me to set a Sunday evening reminder?"*

**Checking what's pending:**
> You: *"What do we need to do this week?"*
> Bot: *"📋 Pending this week (3 chores):*
> *#4 · Clean bathroom · due Wed · Bob · ⚠️ overdue*
> *#7 · Grocery run · due Thu · both*
> *#9 · Water the plants · due Fri · Alice"*

**Marking done with auto-recurrence:**
> You: *"Done the grocery run"*
> Bot: *"✅ Marked 'Grocery run' as complete! Next occurrence created for next Thursday (#12). Nice work 🙌"*

**Scheduling a reminder:**
> You: *"Remind us about the bins Sunday at 8pm"*
> Bot: *"⏰ Reminder set for Sunday at 8:00 PM – I'll message you both then!"*

**Notifying partner:**
> You: *"Tell Bob that I cleaned the kitchen"*
> Bot: *"Sent Bob a message! I let him know you've taken care of the kitchen ✨"*

## Database

A `chores.db` SQLite file is created automatically on first run. Tables:

| Table | Purpose |
|---|---|
| `chores` | All tasks with status, assignee, due date, recurrence |
| `reminders` | Scheduled reminders (checked every minute by the scheduler) |
| `conversation_history` | Last 50 messages per user for Claude context |
