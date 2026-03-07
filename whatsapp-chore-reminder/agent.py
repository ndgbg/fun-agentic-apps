"""
Claude-powered household chores agent.

Uses the Anthropic tool-use agentic loop so Claude can read/write the chore
database, schedule reminders, and notify the partner – all via natural language.
"""

import json
import logging
import os
from datetime import datetime
from typing import Optional

import anthropic

import database as db
import whatsapp

logger = logging.getLogger(__name__)

client = anthropic.Anthropic()

# ---------------------------------------------------------------------------
# Tool definitions (JSON schema format)
# ---------------------------------------------------------------------------

TOOLS: list = [
    {
        "name": "add_chore",
        "description": (
            "Add a new household chore or task to the shared list. "
            "Use this whenever someone wants to track something that needs to be done."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Short, clear title for the chore, e.g. 'Vacuum living room'",
                },
                "description": {
                    "type": "string",
                    "description": "Optional extra details about the chore",
                },
                "assigned_to": {
                    "type": "string",
                    "description": (
                        "Who should do it. Use 'both' for shared, or the person's first name "
                        "(e.g. 'Alice', 'Bob'). Leave out if unspecified."
                    ),
                },
                "due_date": {
                    "type": "string",
                    "description": "Due date in YYYY-MM-DD format. Omit if there's no deadline.",
                },
                "recurrence": {
                    "type": "string",
                    "enum": ["daily", "weekly", "monthly", "none"],
                    "description": "How often this repeats. Use 'none' for one-off chores.",
                },
            },
            "required": ["title"],
        },
    },
    {
        "name": "list_chores",
        "description": "Retrieve chores from the database, with optional filters.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed", "all"],
                    "description": "Filter by status. Defaults to 'pending'.",
                },
                "assigned_to": {
                    "type": "string",
                    "description": "Filter to chores assigned to a specific person or 'both'.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "complete_chore",
        "description": "Mark a chore as done. For recurring chores, automatically creates the next occurrence.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chore_id": {
                    "type": "integer",
                    "description": "The numeric ID of the chore to complete.",
                },
                "completed_by": {
                    "type": "string",
                    "description": "Name of the person who completed it.",
                },
            },
            "required": ["chore_id"],
        },
    },
    {
        "name": "delete_chore",
        "description": "Permanently remove a chore from the list. Also cancels any linked reminders.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chore_id": {
                    "type": "integer",
                    "description": "The numeric ID of the chore to delete.",
                },
            },
            "required": ["chore_id"],
        },
    },
    {
        "name": "update_chore",
        "description": "Edit an existing chore – change its title, due date, assignee, recurrence, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "chore_id": {
                    "type": "integer",
                    "description": "The numeric ID of the chore to update.",
                },
                "title": {"type": "string"},
                "description": {"type": "string"},
                "assigned_to": {"type": "string"},
                "due_date": {
                    "type": "string",
                    "description": "New due date in YYYY-MM-DD format.",
                },
                "recurrence": {
                    "type": "string",
                    "enum": ["daily", "weekly", "monthly", "none"],
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed"],
                },
            },
            "required": ["chore_id"],
        },
    },
    {
        "name": "schedule_reminder",
        "description": (
            "Schedule a WhatsApp reminder that will be sent to both household members "
            "at the specified date and time."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "remind_at": {
                    "type": "string",
                    "description": (
                        "When to send the reminder, in ISO format: YYYY-MM-DDTHH:MM "
                        "(e.g. '2025-03-15T09:00')."
                    ),
                },
                "message": {
                    "type": "string",
                    "description": "The reminder text to send.",
                },
                "chore_id": {
                    "type": "integer",
                    "description": "Optionally link this reminder to a specific chore.",
                },
            },
            "required": ["remind_at", "message"],
        },
    },
    {
        "name": "list_reminders",
        "description": "List all upcoming (unsent) scheduled reminders.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "delete_reminder",
        "description": "Cancel a scheduled reminder before it fires.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reminder_id": {
                    "type": "integer",
                    "description": "The numeric ID of the reminder to delete.",
                },
            },
            "required": ["reminder_id"],
        },
    },
    {
        "name": "get_household_summary",
        "description": (
            "Get a quick overview of the household chore situation: total pending, "
            "overdue count, due this week, completed today, and upcoming reminders."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "notify_partner",
        "description": (
            "Send a WhatsApp message directly to the other household member. "
            "Use this to keep them in the loop about changes or to ask for help."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message to send to the partner.",
                },
            },
            "required": ["message"],
        },
    },
]


# ---------------------------------------------------------------------------
# Tool executor
# ---------------------------------------------------------------------------

def _get_partner_phone(current_phone: str) -> Optional[str]:
    phone1 = os.environ.get("HOUSEHOLD_USER1_PHONE", "").lstrip("+")
    phone2 = os.environ.get("HOUSEHOLD_USER2_PHONE", "").lstrip("+")
    if current_phone == phone1:
        return phone2 or None
    if current_phone == phone2:
        return phone1 or None
    return None


def _execute_tool(name: str, tool_input: dict, user_phone: str, user_name: str) -> str:
    """Run a tool and return a JSON string result."""
    try:
        if name == "add_chore":
            result = db.add_chore(
                title=tool_input["title"],
                created_by=user_name,
                description=tool_input.get("description"),
                assigned_to=tool_input.get("assigned_to", "both"),
                due_date=tool_input.get("due_date"),
                recurrence=tool_input.get("recurrence"),
            )

        elif name == "list_chores":
            result = db.list_chores(
                status=tool_input.get("status", "pending"),
                assigned_to=tool_input.get("assigned_to"),
            )

        elif name == "complete_chore":
            result = db.complete_chore(
                chore_id=tool_input["chore_id"],
                completed_by=tool_input.get("completed_by", user_name),
            )

        elif name == "delete_chore":
            result = db.delete_chore(chore_id=tool_input["chore_id"])

        elif name == "update_chore":
            chore_id = tool_input.pop("chore_id")
            result = db.update_chore(chore_id=chore_id, **tool_input)

        elif name == "schedule_reminder":
            result = db.schedule_reminder(
                remind_at=tool_input["remind_at"],
                message=tool_input["message"],
                chore_id=tool_input.get("chore_id"),
            )

        elif name == "list_reminders":
            result = db.list_reminders()

        elif name == "delete_reminder":
            result = db.delete_reminder(reminder_id=tool_input["reminder_id"])

        elif name == "get_household_summary":
            result = db.get_household_summary()

        elif name == "notify_partner":
            partner = _get_partner_phone(user_phone)
            if partner:
                sent = whatsapp.send_message(partner, tool_input["message"])
                result = {"success": sent, "sent_to": partner}
            else:
                result = {"success": False, "error": "No partner phone number configured"}

        else:
            result = {"error": f"Unknown tool: {name}"}

    except Exception as exc:
        logger.exception("Tool '%s' raised an error", name)
        result = {"error": str(exc)}

    return json.dumps(result, default=str)


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

def _system_prompt(current_user_name: str) -> str:
    name1 = os.environ.get("HOUSEHOLD_USER1_NAME", "User 1")
    name2 = os.environ.get("HOUSEHOLD_USER2_NAME", "User 2")
    today = datetime.now().strftime("%A, %B %d, %Y")
    time_now = datetime.now().strftime("%I:%M %p")

    return f"""You are a friendly household assistant for {name1} and {name2}, helping them manage shared chores and reminders via WhatsApp.

Today: {today}  |  Time: {time_now}
Currently talking to: **{current_user_name}**
Household members: {name1}, {name2}

## Your capabilities
- Add, view, update, delete, and complete chores
- Schedule WhatsApp reminders at specific times
- Notify the partner when something changes
- Summarise the household's chore status

## Guidelines
- Be warm, concise, and WhatsApp-friendly (no long walls of text)
- Always use tools to fetch current data — don't make up chore IDs or details
- When listing chores, show ID, title, due date, assignee, and ⚠️ for overdue items
- When adding chores with due dates, proactively offer to set a reminder
- For recurring chores, mention the cadence clearly
- If the request is ambiguous (e.g. "delete the cleaning chore" but multiple match), list the matches and ask which one
- After completing or adding a chore assigned to the partner, offer to notify them
- Use emoji lightly: ✅ done, ⏰ reminders, 📋 lists, ⚠️ overdue
- Keep responses under ~200 words unless the user needs a detailed list"""


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def process_message(user_phone: str, user_name: str, message_text: str) -> str:
    """
    Process an incoming WhatsApp message through the Claude agentic loop.

    Loads conversation history for context, runs the tool-use loop until
    Claude produces a final text response, then persists the exchange.
    """
    history = db.get_conversation_history(user_phone, limit=10)

    # Build messages: prior history + current user turn
    messages: list = [*history, {"role": "user", "content": message_text}]

    system = _system_prompt(user_name)

    # Agentic loop
    while True:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            thinking={"type": "adaptive"},
            system=system,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            # Collect the final text block
            final_text = " ".join(
                block.text for block in response.content if block.type == "text"
            ).strip()
            if not final_text:
                final_text = "Done! Let me know if there's anything else."

            # Persist exchange (text only – keeps history readable)
            db.add_to_conversation_history(user_phone, "user", message_text)
            db.add_to_conversation_history(user_phone, "assistant", final_text)
            return final_text

        elif response.stop_reason == "tool_use":
            # Append Claude's full response (including tool_use blocks)
            messages.append({"role": "assistant", "content": response.content})

            # Execute each tool call and collect results
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    logger.info("Tool call: %s(%s)", block.name, block.input)
                    result_str = _execute_tool(
                        block.name, dict(block.input), user_phone, user_name
                    )
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_str,
                        }
                    )

            messages.append({"role": "user", "content": tool_results})

        else:
            # Unexpected stop reason – return whatever text is available
            fallback = " ".join(
                block.text for block in response.content if block.type == "text"
            ).strip()
            return fallback or "I had trouble processing that. Please try again."
