"""
WhatsApp Cloud API (Meta) client.
Handles sending messages and marking them as read.
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

_GRAPH_URL = "https://graph.facebook.com/v18.0"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.environ['WHATSAPP_ACCESS_TOKEN']}",
        "Content-Type": "application/json",
    }


def send_message(to_number: str, text: str) -> bool:
    """
    Send a text message to a WhatsApp number.

    Args:
        to_number: E.164 phone number without the leading '+', e.g. '15551234567'.
                   Meta's webhook delivers numbers in this format already.
        text: The message body (max 4096 chars; longer messages are silently truncated).

    Returns:
        True if the API accepted the message, False otherwise.
    """
    phone_number_id = os.environ["WHATSAPP_PHONE_NUMBER_ID"]
    # Truncate to WhatsApp's text limit
    text = text[:4096]

    url = f"{_GRAPH_URL}/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text, "preview_url": False},
    }

    try:
        resp = requests.post(url, json=payload, headers=_headers(), timeout=10)
        if resp.status_code == 200:
            return True
        logger.error("WhatsApp send failed (%s): %s", resp.status_code, resp.text)
        return False
    except requests.RequestException as exc:
        logger.error("WhatsApp send exception: %s", exc)
        return False


def mark_message_read(message_id: str):
    """Mark an incoming message as read (shows blue ticks to the sender)."""
    phone_number_id = os.environ["WHATSAPP_PHONE_NUMBER_ID"]
    url = f"{_GRAPH_URL}/{phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }
    try:
        requests.post(url, json=payload, headers=_headers(), timeout=5)
    except requests.RequestException as exc:
        logger.warning("Could not mark message as read: %s", exc)
