#!/usr/bin/env python3
"""
Calendar Negotiation Agent
Autonomous scheduling agent that negotiates meeting times across multiple participants.
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

class CalendarNegotiationAgent:
    """
    Agentic calendar negotiation system with multi-step reasoning,
    tool use, and autonomous decision-making.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.state = NegotiationState.INITIATED
        self.negotiation_history = []
        self.tools = self._initialize_tools()
        
    def _initialize_tools(self) -> Dict:
        """Initialize available tools for the agent."""
        return {
            "check_availability": self._check_availability,
            "propose_time": self._propose_time,
            "send_email": self._send_email,
            "book_room": self._book_meeting_room,
            "create_zoom": self._create_zoom_link,
            "analyze_preferences": self._analyze_preferences,
            "resolve_conflicts": self._resolve_conflicts
        }
    
    async def negotiate_meeting(self, request: MeetingRequest) -> Dict:
        """
        Main agentic loop: autonomously negotiate meeting time.
        
        Agent capabilities:
        1. Multi-step reasoning about participant constraints
        2. Tool use (calendar APIs, email, room booking)
        3. Adaptive strategy based on responses
        4. Conflict resolution with fallback options
        5. Learning from negotiation patterns
        """
        
        if not self.api_key:
            return self._mock_negotiation(request)
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Phase 1: Analyze constraints and preferences
            analysis = await self._analyze_constraints(client, request)
            
            # Phase 2: Generate candidate time slots
            candidates = await self._generate_candidates(client, request, analysis)
            
            # Phase 3: Rank and propose
            proposal = await self._create_proposal(client, request, candidates)
            
            # Phase 4: Handle negotiation rounds
            result = await self._execute_negotiation(client, request, proposal)
            
            return result
            
        except Exception as e:
            return {"error": str(e), "state": "failed"}
    
    async def _analyze_constraints(self, client, request: MeetingRequest) -> Dict:
        """Use LLM to analyze participant constraints and preferences."""
        
        participants_info = "\n".join([
            f"- {p.name} ({p.email}): TZ={p.timezone}, Prefs={json.dumps(p.preferences)}"
            for p in request.participants
        ])
        
        prompt = f"""Analyze this meeting scheduling request and identify constraints:

Meeting: {request.title}
Duration: {request.duration_minutes} minutes
Priority: {request.priority.value}
Deadline: {request.deadline}

Participants:
{participants_info}

Analyze:
1. Timezone challenges and optimal windows
2. Participant preferences and conflicts
3. Priority-based scheduling strategy
4. Potential obstacles

Provide analysis in JSON:
{{
    "timezone_strategy": "approach for handling timezones",
    "optimal_windows": ["time windows that work for most"],
    "constraints": ["key constraints to respect"],
    "risks": ["potential scheduling risks"],
    "recommended_approach": "negotiation strategy"
}}"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response = message.content[0].text
        
        # Extract JSON
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            response = response[json_start:json_end].strip()
        
        return json.loads(response)
    
    async def _generate_candidates(self, client, request: MeetingRequest, analysis: Dict) -> List[TimeSlot]:
        """Generate and rank candidate time slots using LLM reasoning."""
        
        prompt = f"""Based on this analysis, generate 5 candidate meeting times:

Analysis: {json.dumps(analysis, indent=2)}

Meeting requirements:
- Duration: {request.duration_minutes} minutes
- Priority: {request.priority.value}
- Deadline: {request.deadline}

For each candidate, consider:
1. Timezone fairness (no one gets 3am meetings)
2. Participant preferences
3. Business hours overlap
4. Buffer time between meetings

Generate candidates in JSON:
{{
    "candidates": [
        {{
            "start_time": "ISO datetime",
            "end_time": "ISO datetime",
            "confidence": 0.0-1.0,
            "reasoning": "why this slot works",
            "tradeoffs": "what compromises are made"
        }}
    ]
}}"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response = message.content[0].text
        
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            response = response[json_start:json_end].strip()
        
        data = json.loads(response)
        
        return [
            TimeSlot(
                start=datetime.fromisoformat(c["start_time"]),
                end=datetime.fromisoformat(c["end_time"]),
                confidence=c["confidence"]
            )
            for c in data["candidates"]
        ]
    
    async def _create_proposal(self, client, request: MeetingRequest, candidates: List[TimeSlot]) -> Dict:
        """Create intelligent proposal with reasoning."""
        
        # Sort by confidence
        candidates.sort(key=lambda x: x.confidence, reverse=True)
        top_candidate = candidates[0]
        alternatives = candidates[1:3]
        
        participants_str = ", ".join([p.name for p in request.participants])
        
        prompt = f"""Draft a meeting proposal email for this scheduling request:

Meeting: {request.title}
Participants: {participants_str}
Duration: {request.duration_minutes} minutes

Proposed time: {top_candidate.start} - {top_candidate.end}
Confidence: {top_candidate.confidence}

Alternative times:
{chr(10).join([f"- {alt.start} - {alt.end}" for alt in alternatives])}

Write a professional, concise email that:
1. Proposes the primary time
2. Offers alternatives
3. Explains the reasoning briefly
4. Makes it easy to respond
5. Shows you've considered everyone's constraints

Return JSON:
{{
    "subject": "email subject",
    "body": "email body",
    "tone": "professional|friendly|urgent",
    "call_to_action": "what you want recipients to do"
}}"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response = message.content[0].text
        
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            response = response[json_start:json_end].strip()
        
        proposal = json.loads(response)
        proposal["primary_slot"] = asdict(top_candidate)
        proposal["alternatives"] = [asdict(alt) for alt in alternatives]
        
        return proposal
    
    async def _execute_negotiation(self, client, request: MeetingRequest, proposal: Dict) -> Dict:
        """Execute multi-round negotiation with adaptive strategy."""
        
        self.state = NegotiationState.PROPOSING
        
        # Simulate sending proposal
        self.negotiation_history.append({
            "round": 1,
            "action": "proposal_sent",
            "proposal": proposal,
            "timestamp": datetime.now().isoformat()
        })
        
        # Simulate responses (in real implementation, would wait for actual responses)
        responses = self._simulate_responses(request, proposal)
        
        # Analyze responses and decide next action
        next_action = await self._analyze_responses(client, request, proposal, responses)
        
        if next_action["action"] == "confirm":
            # Book resources
            room = await self._book_meeting_room(request, proposal["primary_slot"])
            zoom = await self._create_zoom_link(request)
            
            # Send confirmation
            confirmation = await self._send_confirmation(client, request, proposal, room, zoom)
            
            self.state = NegotiationState.CONFIRMED
            
            return {
                "state": "confirmed",
                "meeting_time": proposal["primary_slot"],
                "room": room,
                "zoom_link": zoom,
                "confirmation": confirmation,
                "negotiation_rounds": len(self.negotiation_history)
            }
        
        elif next_action["action"] == "renegotiate":
            self.state = NegotiationState.NEGOTIATING
            
            # Generate new proposal based on feedback
            new_proposal = await self._create_counter_proposal(
                client, request, proposal, responses, next_action
            )
            
            return {
                "state": "negotiating",
                "new_proposal": new_proposal,
                "reason": next_action["reason"],
                "negotiation_rounds": len(self.negotiation_history)
            }
        
        else:
            self.state = NegotiationState.FAILED
            return {
                "state": "failed",
                "reason": next_action["reason"]
            }
    
    async def _analyze_responses(self, client, request: MeetingRequest, proposal: Dict, responses: List[Dict]) -> Dict:
        """Analyze participant responses and decide next action."""
        
        responses_str = json.dumps(responses, indent=2)
        
        prompt = f"""Analyze these responses to the meeting proposal and decide next action:

Original proposal: {json.dumps(proposal, indent=2)}

Responses:
{responses_str}

Decide:
1. Can we confirm the meeting? (all accepted or enough key people)
2. Should we renegotiate? (conflicts or better options suggested)
3. Should we escalate? (deadline approaching, no consensus)

Return JSON:
{{
    "action": "confirm|renegotiate|escalate",
    "reason": "explanation",
    "key_insights": ["what we learned from responses"],
    "recommended_next_steps": ["specific actions to take"]
}}"""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response = message.content[0].text
        
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            response = response[json_start:json_end].strip()
        
        return json.loads(response)
    
    async def _create_counter_proposal(self, client, request: MeetingRequest, 
                                      original: Dict, responses: List[Dict], 
                                      analysis: Dict) -> Dict:
        """Create intelligent counter-proposal based on feedback."""
        
        prompt = f"""Create a counter-proposal based on this feedback:

Original proposal: {json.dumps(original, indent=2)}
Responses: {json.dumps(responses, indent=2)}
Analysis: {json.dumps(analysis, indent=2)}

Generate a new proposal that:
1. Addresses the main objections
2. Finds middle ground
3. Maintains meeting priority
4. Shows you listened to feedback

Return JSON with new proposal details."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response = message.content[0].text
        
        if "```json" in response:
            json_start = response.find("```json") + 7
            json_end = response.find("```", json_start)
            response = response[json_start:json_end].strip()
        
        return json.loads(response)
    
    # Tool implementations
    
    def _check_availability(self, participant: Participant, time_range: tuple) -> Dict:
        """Check participant availability (mock)."""
        return {
            "available": True,
            "conflicts": [],
            "preferences_met": 0.8
        }
    
    def _propose_time(self, slot: TimeSlot, participants: List[Participant]) -> Dict:
        """Propose time to participants (mock)."""
        return {
            "sent": True,
            "recipients": [p.email for p in participants]
        }
    
    def _send_email(self, to: List[str], subject: str, body: str) -> Dict:
        """Send email (mock)."""
        return {
            "sent": True,
            "message_id": f"msg_{datetime.now().timestamp()}"
        }
    
    async def _book_meeting_room(self, request: MeetingRequest, slot: Dict) -> Dict:
        """Book meeting room (mock)."""
        return {
            "room_id": "conf-room-3a",
            "room_name": "Golden Gate Conference Room",
            "capacity": 10,
            "amenities": ["video_conf", "whiteboard", "projector"]
        }
    
    async def _create_zoom_link(self, request: MeetingRequest) -> str:
        """Create Zoom link (mock)."""
        return f"https://zoom.us/j/{datetime.now().timestamp()}"
    
    async def _send_confirmation(self, client, request: MeetingRequest, 
                                 proposal: Dict, room: Dict, zoom: str) -> Dict:
        """Send meeting confirmation."""
        return {
            "sent": True,
            "calendar_invites": "sent",
            "includes": ["zoom_link", "room_details", "agenda"]
        }
    
    def _simulate_responses(self, request: MeetingRequest, proposal: Dict) -> List[Dict]:
        """Simulate participant responses (for demo)."""
        return [
            {
                "participant": request.participants[0].email,
                "response": "accepted",
                "message": "Works for me!"
            },
            {
                "participant": request.participants[1].email if len(request.participants) > 1 else "other@example.com",
                "response": "accepted",
                "message": "Confirmed"
            }
        ]
    
    def _analyze_preferences(self, participants: List[Participant]) -> Dict:
        """Analyze participant preferences."""
        return {
            "common_windows": ["9am-11am PST", "2pm-4pm PST"],
            "timezone_spread": "8 hours",
            "flexibility_score": 0.7
        }
    
    def _resolve_conflicts(self, conflicts: List[Dict]) -> Dict:
        """Resolve scheduling conflicts."""
        return {
            "resolution": "propose_alternative",
            "alternatives": []
        }
    
    def _mock_negotiation(self, request: MeetingRequest) -> Dict:
        """Mock negotiation when API not available."""
        return {
            "state": "mock",
            "message": "Set ANTHROPIC_API_KEY to enable real negotiation",
            "mock_result": {
                "proposed_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "participants_notified": len(request.participants),
                "status": "awaiting_responses"
            }
        }

def main():
    """Demo the calendar negotiation agent."""
    
    print("📅 CALENDAR NEGOTIATION AGENT")
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
    
    print("📋 Meeting Request:")
    print(f"  Title: {request.title}")
    print(f"  Duration: {request.duration_minutes} minutes")
    print(f"  Participants: {len(request.participants)}")
    print(f"  Priority: {request.priority.value}")
    print()
    
    # Run negotiation
    agent = CalendarNegotiationAgent()
    
    print("🤖 Agent analyzing constraints and negotiating...")
    print()
    
    import asyncio
    result = asyncio.run(agent.negotiate_meeting(request))
    
    print("📊 NEGOTIATION RESULT:")
    print("=" * 70)
    print(json.dumps(result, indent=2, default=str))
    
    print()
    print("✅ Negotiation complete!")

if __name__ == "__main__":
    main()
