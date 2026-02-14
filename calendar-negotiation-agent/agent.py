#!/usr/bin/env python3
"""
Calendar Negotiation Agent
Autonomous scheduling agent that negotiates meeting times across multiple participants
using Anthropic's tool_use API for truly agentic decision-making.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class NegotiationState(Enum):
    INITIATED = "initiated"
    PROPOSING = "proposing"
    NEGOTIATING = "negotiating"
    CONFIRMED = "confirmed"
    RESCHEDULING = "rescheduling"
    FAILED = "failed"


class Priority(Enum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class Participant:
    email: str
    name: str
    timezone: str
    preferences: Dict[str, any]


@dataclass
class TimeSlot:
    start: datetime
    end: datetime
    confidence: float  # 0-1 score of how good this slot is


@dataclass
class MeetingRequest:
    title: str
    duration_minutes: int
    participants: List[Participant]
    priority: Priority
    deadline: Optional[datetime]
    preferences: Dict[str, any]


SYSTEM_PROMPT = """\
You are an expert calendar negotiation agent. Your job is to schedule a meeting \
that works for all participants by using the tools available to you.

Your workflow:
1. First, gather participant preferences to understand scheduling constraints.
2. Check availability for each participant across a reasonable time range.
3. Based on availability and preferences, propose a set of candidate time slots.
4. Send a proposal email to all participants with the best options.
5. Book a meeting room if one is needed.
6. Create a video conference link if video is required.
7. Finalize the meeting once all resources are secured.

Guidelines:
- Always check availability before proposing times.
- Respect timezone differences -- never propose a slot that falls outside \
  business hours (8am-6pm) in any participant's local timezone.
- Prefer times that score highly on participant preferences.
- If a slot has conflicts, try alternatives before giving up.
- When finalizing, include all relevant details: time, room, video link, attendees.
- Be concise in your reasoning. Focus on actions and results.
"""


class CalendarNegotiationAgent:
    """
    Agentic calendar negotiation system that uses Anthropic's tool_use API
    for autonomous, multi-step scheduling decisions.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.state = NegotiationState.INITIATED
        self.negotiation_history = []

    # -------------------------------------------------------------------------
    # Tool schema definitions for the Anthropic API
    # -------------------------------------------------------------------------

    def _get_tool_definitions(self) -> List[Dict]:
        """Return Anthropic-compatible tool schemas for every capability."""
        return [
            {
                "name": "check_availability",
                "description": (
                    "Check a single participant's calendar availability within a "
                    "given time range. Returns busy/free windows."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "participant_email": {
                            "type": "string",
                            "description": "Email address of the participant to check."
                        },
                        "range_start": {
                            "type": "string",
                            "description": "ISO-8601 datetime for the start of the range to check."
                        },
                        "range_end": {
                            "type": "string",
                            "description": "ISO-8601 datetime for the end of the range to check."
                        }
                    },
                    "required": ["participant_email", "range_start", "range_end"]
                }
            },
            {
                "name": "get_participant_preferences",
                "description": (
                    "Retrieve scheduling preferences for a participant, including "
                    "preferred hours, blocked days, and timezone."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "participant_email": {
                            "type": "string",
                            "description": "Email address of the participant."
                        }
                    },
                    "required": ["participant_email"]
                }
            },
            {
                "name": "propose_times",
                "description": (
                    "Record a ranked list of proposed meeting time slots. Each slot "
                    "includes a start time, end time, and a confidence score."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "proposed_slots": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "start": {
                                        "type": "string",
                                        "description": "ISO-8601 start datetime."
                                    },
                                    "end": {
                                        "type": "string",
                                        "description": "ISO-8601 end datetime."
                                    },
                                    "confidence": {
                                        "type": "number",
                                        "description": "0-1 confidence score for this slot."
                                    },
                                    "reasoning": {
                                        "type": "string",
                                        "description": "Why this slot was chosen."
                                    }
                                },
                                "required": ["start", "end", "confidence"]
                            },
                            "description": "Ranked list of proposed time slots."
                        }
                    },
                    "required": ["proposed_slots"]
                }
            },
            {
                "name": "send_proposal_email",
                "description": (
                    "Send a meeting proposal email to specified recipients with a "
                    "subject, body, and list of proposed time options."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of recipient email addresses."
                        },
                        "subject": {
                            "type": "string",
                            "description": "Email subject line."
                        },
                        "body": {
                            "type": "string",
                            "description": "Email body text."
                        }
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            {
                "name": "book_meeting_room",
                "description": (
                    "Book a physical meeting room for the given time slot and "
                    "number of attendees."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "string",
                            "description": "ISO-8601 start datetime for the room booking."
                        },
                        "end": {
                            "type": "string",
                            "description": "ISO-8601 end datetime for the room booking."
                        },
                        "attendee_count": {
                            "type": "integer",
                            "description": "Number of attendees (used to find a suitably sized room)."
                        },
                        "room_preferences": {
                            "type": "string",
                            "description": "Optional preferences like 'whiteboard', 'video-capable', etc."
                        }
                    },
                    "required": ["start", "end", "attendee_count"]
                }
            },
            {
                "name": "create_zoom_link",
                "description": (
                    "Create a Zoom video conference meeting and return the join URL."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Meeting topic / title."
                        },
                        "duration_minutes": {
                            "type": "integer",
                            "description": "Meeting duration in minutes."
                        },
                        "start_time": {
                            "type": "string",
                            "description": "ISO-8601 scheduled start time."
                        }
                    },
                    "required": ["topic", "duration_minutes"]
                }
            },
            {
                "name": "finalize_meeting",
                "description": (
                    "Finalize and confirm the meeting. Sends calendar invites to all "
                    "participants with the confirmed time, room, and video link."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Meeting title."
                        },
                        "start": {
                            "type": "string",
                            "description": "ISO-8601 confirmed start datetime."
                        },
                        "end": {
                            "type": "string",
                            "description": "ISO-8601 confirmed end datetime."
                        },
                        "attendees": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of attendee email addresses."
                        },
                        "zoom_link": {
                            "type": "string",
                            "description": "Video conference join URL."
                        },
                        "room": {
                            "type": "string",
                            "description": "Meeting room name or identifier."
                        },
                        "notes": {
                            "type": "string",
                            "description": "Any additional notes for the invite."
                        }
                    },
                    "required": ["title", "start", "end", "attendees"]
                }
            }
        ]

    # -------------------------------------------------------------------------
    # Tool dispatch
    # -------------------------------------------------------------------------

    def _execute_tool(self, name: str, tool_input: Dict) -> Dict:
        """
        Dispatch a tool call to the appropriate implementation method.
        Falls back to mock results when real integrations are not configured.
        """
        dispatch = {
            "check_availability": self._tool_check_availability,
            "get_participant_preferences": self._tool_get_participant_preferences,
            "propose_times": self._tool_propose_times,
            "send_proposal_email": self._tool_send_proposal_email,
            "book_meeting_room": self._tool_book_meeting_room,
            "create_zoom_link": self._tool_create_zoom_link,
            "finalize_meeting": self._tool_finalize_meeting,
        }

        handler = dispatch.get(name)
        if not handler:
            return {"error": f"Unknown tool: {name}"}

        try:
            return handler(tool_input)
        except Exception as e:
            return {"error": str(e)}

    # -------------------------------------------------------------------------
    # Individual tool handlers (real integration with mock fallback)
    # -------------------------------------------------------------------------

    def _tool_check_availability(self, inp: Dict) -> Dict:
        """Check calendar availability; falls back to mock if Google is not configured."""
        email = inp["participant_email"]
        range_start = inp["range_start"]
        range_end = inp["range_end"]

        # Look up the participant in the current request for timezone info
        participant = self._find_participant(email)

        try:
            result = self._check_availability(participant, (range_start, range_end))
            if "note" not in result or "not configured" not in result.get("note", ""):
                return result
        except Exception:
            pass

        # Mock fallback: simulate realistic availability
        return self._mock_check_availability(email, range_start, range_end)

    def _tool_get_participant_preferences(self, inp: Dict) -> Dict:
        """Return stored preferences for a participant."""
        email = inp["participant_email"]
        participant = self._find_participant(email)
        if participant:
            return {
                "email": participant.email,
                "name": participant.name,
                "timezone": participant.timezone,
                "preferences": participant.preferences
            }
        return {"error": f"Participant {email} not found in the meeting request."}

    def _tool_propose_times(self, inp: Dict) -> Dict:
        """Record proposed time slots in the negotiation history."""
        slots = inp["proposed_slots"]
        self.state = NegotiationState.PROPOSING
        self.negotiation_history.append({
            "action": "times_proposed",
            "slots": slots,
            "timestamp": datetime.now().isoformat()
        })
        return {
            "status": "recorded",
            "slots_proposed": len(slots),
            "top_slot": slots[0] if slots else None
        }

    def _tool_send_proposal_email(self, inp: Dict) -> Dict:
        """Send proposal email; falls back to mock if SMTP is not configured."""
        to = inp["to"]
        subject = inp["subject"]
        body = inp["body"]

        result = self._send_email(to, subject, body)
        if result.get("sent"):
            return result

        # Mock fallback
        self.negotiation_history.append({
            "action": "proposal_email_sent",
            "to": to,
            "subject": subject,
            "timestamp": datetime.now().isoformat()
        })
        return {
            "sent": True,
            "mock": True,
            "message_id": f"mock_msg_{int(datetime.now().timestamp())}",
            "recipients": to,
            "note": "Email simulated (SMTP not configured). In production, participants would receive this email."
        }

    def _tool_book_meeting_room(self, inp: Dict) -> Dict:
        """Book a meeting room; falls back to mock if Google Calendar resources are not configured."""
        start = inp["start"]
        end = inp["end"]
        attendee_count = inp["attendee_count"]
        room_prefs = inp.get("room_preferences", "")

        # Try real booking
        try:
            slot = {"start": start, "end": end}
            # Build a minimal MeetingRequest-like object for the real method
            result = self._book_meeting_room_real(slot)
            if result.get("booked") is not False:
                return result
        except Exception:
            pass

        # Mock fallback
        room_name = "Conference Room A" if attendee_count <= 6 else "Large Meeting Room B"
        return {
            "booked": True,
            "mock": True,
            "room_name": room_name,
            "room_id": f"room_{room_name.lower().replace(' ', '_')}",
            "capacity": 6 if attendee_count <= 6 else 14,
            "start": start,
            "end": end,
            "amenities": ["whiteboard", "video_screen", "speakerphone"],
            "note": "Room booking simulated (Google Calendar resources not configured)."
        }

    def _tool_create_zoom_link(self, inp: Dict) -> Dict:
        """Create a Zoom link; falls back to mock if Zoom API is not configured."""
        topic = inp["topic"]
        duration = inp["duration_minutes"]
        start_time = inp.get("start_time", "")

        # Try real Zoom integration
        try:
            zoom_url = self._create_zoom_link_real(topic, duration)
            if "placeholder" not in zoom_url and "error" not in zoom_url:
                return {"zoom_link": zoom_url, "topic": topic}
        except Exception:
            pass

        # Mock fallback
        mock_id = abs(hash(topic)) % 10000000000
        return {
            "zoom_link": f"https://zoom.us/j/{mock_id}",
            "mock": True,
            "topic": topic,
            "duration_minutes": duration,
            "meeting_id": str(mock_id),
            "passcode": "123456",
            "note": "Zoom link simulated (ZOOM_API_KEY not configured)."
        }

    def _tool_finalize_meeting(self, inp: Dict) -> Dict:
        """Finalize the meeting: send calendar invites and update state."""
        title = inp["title"]
        start = inp["start"]
        end = inp["end"]
        attendees = inp["attendees"]
        zoom_link = inp.get("zoom_link", "")
        room = inp.get("room", "")
        notes = inp.get("notes", "")

        self.state = NegotiationState.CONFIRMED
        self.negotiation_history.append({
            "action": "meeting_finalized",
            "title": title,
            "start": start,
            "end": end,
            "attendees": attendees,
            "zoom_link": zoom_link,
            "room": room,
            "timestamp": datetime.now().isoformat()
        })

        # Try to create a real Google Calendar event
        try:
            creds = self._get_google_credentials()
            if creds:
                from googleapiclient.discovery import build
                service = build('calendar', 'v3', credentials=creds)
                event = {
                    'summary': title,
                    'description': f"Zoom: {zoom_link}\nRoom: {room}\n{notes}",
                    'start': {'dateTime': start, 'timeZone': 'UTC'},
                    'end': {'dateTime': end, 'timeZone': 'UTC'},
                    'attendees': [{'email': e} for e in attendees],
                }
                created = service.events().insert(
                    calendarId='primary', body=event, sendUpdates='all'
                ).execute()
                return {
                    "finalized": True,
                    "event_id": created['id'],
                    "calendar_invites_sent": True,
                    "title": title,
                    "start": start,
                    "end": end,
                    "attendees": attendees,
                    "zoom_link": zoom_link,
                    "room": room
                }
        except Exception:
            pass

        # Mock fallback
        return {
            "finalized": True,
            "mock": True,
            "event_id": f"evt_{int(datetime.now().timestamp())}",
            "calendar_invites_sent": True,
            "title": title,
            "start": start,
            "end": end,
            "attendees": attendees,
            "zoom_link": zoom_link,
            "room": room,
            "note": "Calendar invites simulated (Google Calendar not configured). In production, all attendees would receive calendar invitations."
        }

    # -------------------------------------------------------------------------
    # Helper: find a participant in the current request
    # -------------------------------------------------------------------------

    def _find_participant(self, email: str) -> Optional[Participant]:
        """Look up a participant by email in the current meeting request."""
        if not hasattr(self, '_current_request') or self._current_request is None:
            return None
        for p in self._current_request.participants:
            if p.email == email:
                return p
        return None

    # -------------------------------------------------------------------------
    # Mock availability generator
    # -------------------------------------------------------------------------

    def _mock_check_availability(self, email: str, range_start: str, range_end: str) -> Dict:
        """Generate realistic mock availability data."""
        try:
            start_dt = datetime.fromisoformat(range_start.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(range_end.replace("Z", "+00:00"))
        except ValueError:
            start_dt = datetime.now() + timedelta(days=1)
            end_dt = start_dt + timedelta(days=3)

        # Generate some plausible busy blocks based on email hash
        email_hash = hash(email)
        busy_blocks = []
        current = start_dt
        while current < end_dt:
            # Skip weekends
            if current.weekday() < 5:
                # Create 1-2 busy blocks per day based on email hash
                block_hour = 9 + (abs(email_hash) % 7)
                block_start = current.replace(hour=block_hour, minute=0, second=0, microsecond=0)
                block_end = block_start + timedelta(hours=1)
                if block_start >= start_dt and block_end <= end_dt:
                    busy_blocks.append({
                        "start": block_start.isoformat(),
                        "end": block_end.isoformat()
                    })
                # Second block
                block_hour2 = (block_hour + 3) % 17
                if block_hour2 >= 9:
                    block_start2 = current.replace(hour=block_hour2, minute=30, second=0, microsecond=0)
                    block_end2 = block_start2 + timedelta(minutes=45)
                    if block_start2 >= start_dt and block_end2 <= end_dt:
                        busy_blocks.append({
                            "start": block_start2.isoformat(),
                            "end": block_end2.isoformat()
                        })
            current += timedelta(days=1)

        return {
            "participant": email,
            "range_start": range_start,
            "range_end": range_end,
            "busy_blocks": busy_blocks,
            "free_windows_hint": "Available outside of the listed busy blocks during business hours.",
            "mock": True,
            "note": "Availability simulated (Google Calendar not configured)."
        }

    # -------------------------------------------------------------------------
    # Real integration methods (kept from original)
    # -------------------------------------------------------------------------

    def _check_availability(self, participant: Participant, time_range: tuple) -> Dict:
        """Check participant availability via Google Calendar."""
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = self._get_google_credentials()
            if not creds:
                return {"available": True, "note": "Calendar access not configured"}

            service = build('calendar', 'v3', credentials=creds)

            body = {
                "timeMin": time_range[0] if isinstance(time_range[0], str) else time_range[0].isoformat(),
                "timeMax": time_range[1] if isinstance(time_range[1], str) else time_range[1].isoformat(),
                "items": [{"id": participant.email}]
            }

            result = service.freebusy().query(body=body).execute()
            busy = result['calendars'].get(participant.email, {}).get('busy', [])

            return {
                "available": len(busy) == 0,
                "conflicts": busy,
                "preferences_met": 0.8 if len(busy) == 0 else 0.3
            }
        except Exception as e:
            return {"available": True, "note": f"Calendar check failed: {e}"}

    def _send_email(self, to: List[str], subject: str, body: str) -> Dict:
        """Send email via SMTP."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER")
            smtp_pass = os.getenv("SMTP_PASSWORD")

            if not smtp_user or not smtp_pass:
                return {"sent": False, "note": "SMTP credentials not configured"}

            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = ", ".join(to)
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)

            return {
                "sent": True,
                "message_id": f"msg_{datetime.now().timestamp()}"
            }
        except Exception as e:
            return {"sent": False, "error": str(e)}

    def _book_meeting_room_real(self, slot: Dict) -> Dict:
        """Book meeting room via Google Calendar resource."""
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = self._get_google_credentials()
            if not creds:
                return {"booked": False, "note": "Calendar access not configured"}

            service = build('calendar', 'v3', credentials=creds)

            resources = service.resources().calendars().list(
                customer='my_customer'
            ).execute()

            if resources.get('items'):
                room = resources['items'][0]
                return {
                    "booked": True,
                    "room_id": room['resourceId'],
                    "room_name": room['resourceName'],
                    "capacity": room.get('capacity', 10),
                    "amenities": room.get('featureInstances', [])
                }

            return {"booked": False, "note": "No rooms available"}
        except Exception as e:
            return {"booked": False, "error": str(e)}

    def _create_zoom_link_real(self, topic: str, duration_minutes: int) -> str:
        """Create Zoom meeting via API."""
        try:
            import requests

            zoom_api_key = os.getenv("ZOOM_API_KEY")
            zoom_api_secret = os.getenv("ZOOM_API_SECRET")

            if not zoom_api_key or not zoom_api_secret:
                return "https://zoom.us/j/placeholder (Configure ZOOM_API_KEY)"

            import jwt
            import time

            payload = {
                'iss': zoom_api_key,
                'exp': time.time() + 3600
            }
            token = jwt.encode(payload, zoom_api_secret, algorithm='HS256')

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            data = {
                'topic': topic,
                'type': 2,
                'duration': duration_minutes,
                'settings': {
                    'host_video': True,
                    'participant_video': True,
                    'join_before_host': False
                }
            }

            response = requests.post(
                'https://api.zoom.us/v2/users/me/meetings',
                headers=headers,
                json=data
            )

            if response.status_code == 201:
                meeting = response.json()
                return meeting['join_url']

            return f"https://zoom.us/j/error_{response.status_code}"

        except Exception as e:
            return f"https://zoom.us/j/error (Setup required: {e})"

    def _get_google_credentials(self):
        """Get Google OAuth credentials."""
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow
            import pickle
            import os.path

            SCOPES = ['https://www.googleapis.com/auth/calendar']
            creds = None

            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                    with open('token.pickle', 'wb') as token:
                        pickle.dump(creds, token)
                else:
                    return None

            return creds
        except Exception as e:
            print(f"Google auth error: {e}")
            return None

    # -------------------------------------------------------------------------
    # The agentic loop
    # -------------------------------------------------------------------------

    def negotiate_meeting(self, request: MeetingRequest, max_iterations: int = 20) -> Dict:
        """
        Run the agentic negotiation loop. The LLM autonomously decides which
        tools to call, observes results, and continues until the meeting is
        scheduled or it determines scheduling has failed.
        """
        self._current_request = request

        if not self.api_key:
            return self._mock_negotiation(request)

        try:
            import anthropic
        except ImportError:
            return {
                "error": "The 'anthropic' package is required. Install it with: pip install anthropic",
                "state": "failed"
            }

        client = anthropic.Anthropic(api_key=self.api_key)

        # Build the initial task description
        participants_desc = "\n".join([
            f"  - {p.name} <{p.email}> | Timezone: {p.timezone} | Preferences: {json.dumps(p.preferences)}"
            for p in request.participants
        ])

        task_description = (
            f"Please schedule the following meeting:\n\n"
            f"Title: {request.title}\n"
            f"Duration: {request.duration_minutes} minutes\n"
            f"Priority: {request.priority.value}\n"
            f"Deadline to schedule by: {request.deadline.isoformat() if request.deadline else 'None'}\n"
            f"Meeting preferences: {json.dumps(request.preferences)}\n\n"
            f"Participants:\n{participants_desc}\n\n"
            f"Today's date is {datetime.now().strftime('%Y-%m-%d')}. "
            f"Please find a time that works for everyone within the next 5 business days, "
            f"book any required resources, and finalize the meeting."
        )

        messages = [{"role": "user", "content": task_description}]

        print(f"[Agent] Starting negotiation for: {request.title}")
        print(f"[Agent] Participants: {', '.join(p.name for p in request.participants)}")
        print()

        final_text = ""

        for iteration in range(1, max_iterations + 1):
            print(f"[Agent] Iteration {iteration}/{max_iterations}")

            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=self._get_tool_definitions(),
                messages=messages
            )

            # Append the assistant's response to the conversation
            messages.append({"role": "assistant", "content": response.content})

            # Extract any text blocks for logging
            for block in response.content:
                if hasattr(block, "text"):
                    final_text = block.text
                    print(f"[Agent] {block.text[:200]}{'...' if len(block.text) > 200 else ''}")

            # If the model decided to stop, we are done
            if response.stop_reason == "end_turn":
                print(f"[Agent] Completed after {iteration} iteration(s).")
                break

            # Process tool calls
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"[Tool] Calling: {block.name}({json.dumps(block.input, default=str)[:120]}...)")
                        result = self._execute_tool(block.name, block.input)
                        print(f"[Tool] Result: {json.dumps(result, default=str)[:200]}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, default=str) if isinstance(result, dict) else str(result)
                        })

                messages.append({"role": "user", "content": tool_results})
        else:
            # Reached max iterations without end_turn
            print(f"[Agent] Reached maximum iterations ({max_iterations}).")
            self.state = NegotiationState.FAILED

        return {
            "state": self.state.value,
            "negotiation_history": self.negotiation_history,
            "iterations": min(iteration, max_iterations) if 'iteration' in dir() else max_iterations,
            "final_message": final_text,
        }

    # -------------------------------------------------------------------------
    # Mock negotiation for when API key is missing
    # -------------------------------------------------------------------------

    def _mock_negotiation(self, request: MeetingRequest) -> Dict:
        """Mock negotiation when API not available."""
        return {
            "state": "mock",
            "message": "Set ANTHROPIC_API_KEY to enable real agentic negotiation",
            "mock_result": {
                "proposed_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "participants_notified": len(request.participants),
                "status": "awaiting_responses"
            }
        }


# =============================================================================
# Main
# =============================================================================

def main():
    """Run the calendar negotiation agent."""

    print("CALENDAR NEGOTIATION AGENT")
    print("=" * 70)
    print()

    # Create meeting request
    request = MeetingRequest(
        title="Q1 Planning Session",
        duration_minutes=60,
        participants=[
            Participant(
                email="alice@company.com",
                name="Alice Chen",
                timezone="America/Los_Angeles",
                preferences={"morning_person": True, "no_mondays": False}
            ),
            Participant(
                email="bob@company.com",
                name="Bob Smith",
                timezone="America/New_York",
                preferences={"afternoon_preferred": True, "no_fridays": True}
            ),
            Participant(
                email="carol@company.com",
                name="Carol Martinez",
                timezone="Europe/London",
                preferences={"flexible": True, "lunch_block": "12pm-1pm"}
            )
        ],
        priority=Priority.HIGH,
        deadline=datetime.now() + timedelta(days=7),
        preferences={
            "video_required": True,
            "recurring": False,
            "room_needed": True
        }
    )

    print("Meeting Request:")
    print(f"  Title: {request.title}")
    print(f"  Duration: {request.duration_minutes} minutes")
    print(f"  Participants: {len(request.participants)}")
    for p in request.participants:
        print(f"    - {p.name} ({p.timezone})")
    print(f"  Priority: {request.priority.value}")
    print(f"  Video required: {request.preferences.get('video_required')}")
    print(f"  Room needed: {request.preferences.get('room_needed')}")
    print()

    # Run negotiation
    agent = CalendarNegotiationAgent()

    print("Starting agentic negotiation loop...")
    print("-" * 70)
    print()

    result = agent.negotiate_meeting(request)

    print()
    print("-" * 70)
    print("NEGOTIATION RESULT:")
    print("=" * 70)
    print(json.dumps(result, indent=2, default=str))

    print()
    print(f"Final state: {result.get('state', 'unknown')}")
    print("Negotiation complete.")


if __name__ == "__main__":
    main()
