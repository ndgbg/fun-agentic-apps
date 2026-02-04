# Calendar Negotiation Agent 📅

Autonomous scheduling agent that handles the entire meeting coordination process.

## What It Does

Coordinates meetings across multiple participants by:
- Analyzing timezone constraints and preferences
- Proposing optimal meeting times with reasoning
- Handling participant responses and objections
- Adapting strategy based on feedback
- Booking conference rooms automatically
- Generating video conference links
- Managing rescheduling when conflicts arise

## Agentic Architecture

### Multi-Step Reasoning
- Analyzes participant constraints (timezones, preferences, availability)
- Generates candidate time slots with confidence scores
- Ranks options based on fairness and feasibility
- Adapts strategy when initial proposals fail

### Tool Use
- Calendar API integration
- Email communication
- Room booking systems
- Video conferencing (Zoom/Meet)
- Conflict resolution

### Autonomous Decision-Making
- Decides when to confirm vs. renegotiate
- Handles objections without human intervention
- Escalates only when necessary
- Learns from negotiation patterns

### State Management
- Tracks negotiation rounds
- Maintains conversation history
- Remembers participant preferences
- Handles async responses

## Quick Start

```bash
# Set API key
export ANTHROPIC_API_KEY=your_key

# Install dependencies
pip install -r requirements.txt

# Run demo
python agent.py
```

## Example Usage

```python
from agent import CalendarNegotiationAgent, MeetingRequest, Participant, Priority
from datetime import datetime, timedelta

# Create meeting request
request = MeetingRequest(
    title="Product Review",
    duration_minutes=60,
    participants=[
        Participant(
            email="alice@company.com",
            name="Alice Chen",
            timezone="America/Los_Angeles",
            preferences={"morning_person": True}
        ),
        Participant(
            email="bob@company.com",
            name="Bob Smith",
            timezone="Europe/London",
            preferences={"no_early_meetings": True}
        )
    ],
    priority=Priority.HIGH,
    deadline=datetime.now() + timedelta(days=7),
    preferences={"video_required": True}
)

# Let agent negotiate
agent = CalendarNegotiationAgent()
result = await agent.negotiate_meeting(request)

print(f"Meeting scheduled: {result['meeting_time']}")
print(f"Zoom link: {result['zoom_link']}")
print(f"Room: {result['room']['room_name']}")
```

## How It Works

### Phase 1: Constraint Analysis
```
Agent analyzes:
- Timezone overlaps
- Participant preferences
- Priority and urgency
- Deadline constraints
```

### Phase 2: Candidate Generation
```
Generates 5 candidate slots:
- Ranks by confidence (0-1)
- Considers fairness (no 3am meetings)
- Respects business hours
- Accounts for preferences
```

### Phase 3: Proposal Creation
```
Crafts intelligent proposal:
- Primary time + alternatives
- Explains reasoning
- Easy response mechanism
- Shows constraint awareness
```

### Phase 4: Negotiation Loop
```
Handles responses:
- Accepts confirmations
- Addresses objections
- Proposes alternatives
- Adapts strategy
- Confirms when consensus reached
```

### Phase 5: Resource Booking
```
Automatically:
- Books conference room
- Creates video link
- Sends calendar invites
- Includes all details
```

## Advanced Features

### Intelligent Rescheduling
When conflicts arise, agent:
- Analyzes impact on all participants
- Finds minimal-disruption alternatives
- Communicates changes clearly
- Updates all resources

### Preference Learning
Agent remembers:
- Participant timezone patterns
- Preferred meeting times
- Response patterns
- Flexibility levels

### Conflict Resolution
Handles:
- Overlapping availability
- Timezone challenges
- Priority conflicts
- Resource constraints

### Adaptive Communication
Adjusts tone based on:
- Meeting priority
- Deadline urgency
- Participant seniority
- Previous interactions

## Configuration

```python
agent = CalendarNegotiationAgent(
    api_key="your_key",
    max_negotiation_rounds=3,
    auto_book_resources=True,
    send_reminders=True
)
```

## Integration

### Calendar APIs
- Google Calendar
- Outlook Calendar
- Apple Calendar

### Video Conferencing
- Zoom
- Google Meet
- Microsoft Teams

### Room Booking
- Office 365
- Google Workspace
- Custom systems

### Email
- SMTP
- SendGrid
- AWS SES

## Real-World Scenarios

### Scenario 1: Cross-Timezone Team
```
3 participants across US, Europe, Asia
Agent finds 9am PST / 5pm GMT / 1am+1 SGT
Proposes with reasoning about timezone fairness
```

### Scenario 2: Conflicting Preferences
```
One prefers mornings, another afternoons
Agent finds compromise: late morning
Explains tradeoff in proposal
```

### Scenario 3: Urgent Meeting
```
High priority, 24-hour deadline
Agent prioritizes speed over perfection
Proposes first viable slot
Escalates if no quick consensus
```

### Scenario 4: Rescheduling
```
Participant cancels confirmed meeting
Agent analyzes impact
Finds new time minimizing disruption
Notifies all parties with context
```

## Why It's Agentic

**Traditional scheduling tools:**
- Show availability
- Let humans negotiate
- Require manual coordination

**This agent:**
- Understands constraints
- Proposes solutions
- Handles objections
- Makes decisions
- Takes actions
- Learns patterns

## Limitations

- Requires OAuth setup for Google Calendar
- SMTP credentials needed for email
- Zoom API key for video links
- Real integrations need proper authentication

## License

MIT

---

*"The agent that finally solves 'finding a time that works.'"*
