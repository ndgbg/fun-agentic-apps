"""
WhatsApp Household Chores Reminder — Flask webhook server.

Receives incoming WhatsApp messages via Meta's Webhooks API,
routes them to the Claude agent, and sends the reply back.

Quick start:
    cp .env.example .env   # fill in your keys
    python app.py
"""

import logging
import os

from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()

import database as db
import scheduler
from agent import process_message
from whatsapp import mark_message_read, send_message

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = Flask(__name__)

# phone_number (no '+') → display name, populated at startup
HOUSEHOLD_USERS: dict[str, str] = {}


def _load_household_users():
    for i in ("1", "2"):
        phone = os.environ.get(f"HOUSEHOLD_USER{i}_PHONE", "").lstrip("+")
        name = os.environ.get(f"HOUSEHOLD_USER{i}_NAME", f"User {i}")
        if phone:
            HOUSEHOLD_USERS[phone] = name
    logger.info("Household users: %s", HOUSEHOLD_USERS)


# ---------------------------------------------------------------------------
# Webhook verification (GET)
# ---------------------------------------------------------------------------

@app.get("/webhook")
def webhook_verify():
    """
    Meta sends a one-time GET request to verify the webhook URL.
    We must echo back hub.challenge when hub.verify_token matches our secret.
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == os.environ.get("WHATSAPP_VERIFY_TOKEN"):
        logger.info("Webhook verified ✓")
        return challenge, 200

    logger.warning("Webhook verification failed (token mismatch?)")
    return "Forbidden", 403


# ---------------------------------------------------------------------------
# Incoming messages (POST)
# ---------------------------------------------------------------------------

@app.post("/webhook")
def webhook_receive():
    """
    Meta delivers all incoming message events here as JSON.
    We acknowledge immediately with 200 OK and process synchronously
    (for a production deployment, move processing to a task queue).
    """
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify(status="no data"), 400

    try:
        # WhatsApp webhook structure: payload → entry[] → changes[] → value
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for msg in value.get("messages", []):
                    _handle_message(msg)
    except Exception:
        logger.exception("Unhandled error in webhook handler")
        # Always return 200 so Meta doesn't keep retrying
    return jsonify(status="ok"), 200


def _handle_message(msg: dict):
    """Process a single incoming WhatsApp message object."""
    from_number = msg.get("from", "")
    message_id = msg.get("id", "")
    msg_type = msg.get("type", "")

    # Only handle plain text messages
    if msg_type != "text":
        logger.debug("Ignoring message type '%s' from %s", msg_type, from_number)
        return

    text = (msg.get("text") or {}).get("body", "").strip()
    if not text:
        return

    logger.info("Incoming from %s: %.60s…", from_number, text)

    # Mark as read (shows ✓✓ to sender)
    if message_id:
        mark_message_read(message_id)

    # Authorisation check
    user_name = HOUSEHOLD_USERS.get(from_number)
    if not user_name:
        logger.warning("Unauthorised sender: %s", from_number)
        send_message(
            from_number,
            "Sorry, you're not registered as a household member. "
            "Ask your partner to add your number to the .env file.",
        )
        return

    # Process with the Claude agent
    try:
        reply = process_message(
            user_phone=from_number,
            user_name=user_name,
            message_text=text,
        )
        send_message(from_number, reply)
    except Exception:
        logger.exception("Agent error for %s", from_number)
        send_message(
            from_number,
            "Something went wrong on my end – sorry! Try again in a moment.",
        )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return jsonify(status="ok", service="whatsapp-chore-reminder")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _load_household_users()
    db.init_db()
    scheduler.start()

    port = int(os.environ.get("PORT", 5000))
    logger.info("Starting server on port %d", port)

    try:
        # Use threaded=True so the scheduler's background thread can co-exist
        app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
    finally:
        scheduler.stop()
