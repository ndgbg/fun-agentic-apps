# 🏠 Home Maintenance Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude%203.5-orange.svg)](https://www.anthropic.com/)
[![Google Calendar](https://img.shields.io/badge/Google-Calendar%20API-green.svg)](https://developers.google.com/calendar)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Sophisticated multi-agent system for proactive home maintenance management.**

Never miss maintenance again. Predict failures before they happen. Optimize costs automatically.

## What It Does

- **Predicts failures** - ML-powered analysis predicts system failures before they occur
- **Optimizes scheduling** - Intelligent scheduling based on budget, time, weather, and season
- **Generates alerts** - Contextual alerts for overdue tasks and predicted failures
- **Calendar integration** - Auto-adds tasks and reminders to Google Calendar
- **Cost optimization** - Analyzes DIY vs professional, bulk purchasing, preventive vs reactive
- **Knowledge base** - Generates detailed maintenance guides for every task

## Why It's Agentic

This showcases advanced multi-agent patterns:

- **6 specialized agents** working in coordination
- **Predictive analytics** using LLM reasoning
- **Multi-constraint optimization** (cost, time, weather, season)
- **Autonomous decision-making** (schedule, prioritize, alert)
- **Real-time adaptation** based on conditions
- **Knowledge synthesis** from maintenance data

## Architecture

```
HomeMaintenanceOrchestrator
├── PredictiveMaintenanceAgent
│   └── Predicts failures using home profile + history
├── SchedulingAgent
│   └── Optimizes schedule with multi-constraint solving
├── AlertAgent
│   └── Generates contextual alerts
├── CalendarIntegrationAgent
│   └── Google Calendar API integration
├── KnowledgeBaseAgent
│   └── Generates maintenance guides
└── CostOptimizationAgent
    └── Analyzes and optimizes costs
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run
python agent.py
```

## Features

### 1. Predictive Maintenance

Analyzes your home profile and maintenance history to predict failures:

```python
predictions = await predictive_agent.predict_failures(home_profile, history)

# Example output:
{
  "system": "HVAC compressor",
  "failure_probability": 65,
  "time_to_failure_days": 120,
  "failure_cost": 2500,
  "preventive_action": "Schedule HVAC inspection",
  "preventive_cost": 150
}
```

**Considers:**
- Home age and size
- System ages (HVAC, roof, appliances)
- Climate zone
- Maintenance history
- Typical failure patterns

### 2. Intelligent Scheduling

Optimizes maintenance schedule based on multiple constraints:

```python
schedule = await scheduling_agent.optimize_schedule(tasks, constraints)
```

**Optimizes for:**
- Budget constraints
- Available time
- Seasonal appropriateness
- Weather conditions
- Task dependencies
- DIY vs professional balance

**Groups related tasks:**
- HVAC filter + thermostat check
- Gutter cleaning + roof inspection
- Multiple plumbing tasks for one plumber visit

### 3. Contextual Alerts

Generates intelligent alerts based on multiple factors:

- **Overdue tasks** - Critical tasks past due date
- **Upcoming deadlines** - Tasks due within 7-14 days
- **Predictive alerts** - Systems likely to fail
- **Weather alerts** - Postpone outdoor tasks in bad weather
- **Seasonal reminders** - Time-sensitive maintenance

**Alert severity:**
- 🔴 Critical - Immediate action required
- 🟡 High - Action needed soon
- 🟢 Medium - Plan ahead

### 4. Calendar Integration

Automatically adds to Google Calendar:

- Maintenance tasks with estimated time
- Reminders (24h before, 1h before)
- Detailed descriptions with costs
- Professional vs DIY indication

### 5. Cost Optimization

Analyzes and optimizes maintenance costs:

```python
cost_analysis = await cost_agent.optimize_costs(tasks, budget)

# Identifies:
- DIY opportunities (save $1000s)
- Bulk purchase items (filters, bulbs)
- Contractor bundles (save 20-30%)
- Preventive vs reactive costs
```

**Example savings:**
- HVAC filter: $150/year → $45/year (DIY + bulk)
- Gutter cleaning: $200/visit → $0 (DIY)
- Preventive HVAC service: $150 → Saves $2500 repair

### 6. Knowledge Base

Generates detailed guides for every task:

- Step-by-step instructions
- Tools and materials needed
- Safety precautions
- Common mistakes to avoid
- When to call a professional
- Time and cost breakdowns

## Home Profile

System adapts to your specific home:

```python
home = HomeProfile(
    home_age=15,
    square_footage=2500,
    num_bedrooms=4,
    num_bathrooms=3,
    has_basement=True,
    has_attic=True,
    has_garage=True,
    hvac_type="Central AC + Gas Furnace",
    hvac_age=12,
    roof_age=8,
    location="Seattle, WA",
    climate_zone="Marine"
)
```

## Maintenance Categories

Tracks 9 categories with comprehensive tasks:

1. **HVAC** - Filters (every 3 months), annual service, duct cleaning
2. **Plumbing** - Water heater flush, pipes, fixtures
3. **Electrical** - Panels, outlets, lighting
4. **Appliances** - Washing machine cleaning (every 3 weeks), refrigerator, dryer
5. **Exterior** - Roof, gutters, siding, paint
6. **Interior** - Flooring, walls, doors, windows
7. **Landscaping** - Lawn, trees, irrigation
8. **Safety** - Smoke detectors (every 6 months), CO detectors, fire extinguishers
9. **Seasonal** - Winterization (outdoor faucet covers, sprinkler blowout, HVAC prep), spring de-winterization

### Seasonal Tasks Included

**Winterization (Fall):**
- Install insulated covers on outdoor faucets
- Blow out sprinkler system lines
- Cover outdoor AC unit
- Drain garden hoses

**Spring Preparation:**
- Remove faucet covers
- Turn on outdoor water supply
- Uncover AC unit
- Test sprinkler system

**Regular Appliance Maintenance:**
- Washing machine cleaning every 3 weeks (prevents mold, odors)
- Dryer vent cleaning every 6 months
- Refrigerator coil cleaning every 6 months

## Example Output

```
🏠 HOME MAINTENANCE AGENT - Daily Analysis
======================================================================

🔮 Running predictive analysis...
   Found 3 potential issues
   ⚠️  HVAC compressor: 65% risk
   ⚠️  Water heater element: 45% risk
   ⚠️  Roof shingles: 30% risk

🚨 Generating alerts...
   Generated 5 alerts
   🔴 URGENT: Test smoke detectors due in 7 days
   🟡 Reminder: HVAC annual service due in 60 days
   🟡 PREDICTION: HVAC compressor has 65% chance of failure

📅 Optimizing schedule...
   Scheduled 8 tasks
   📌 2026-02-15: Critical HVAC filter change, prevents $2000 repair
   📌 2026-02-20: Group gutter cleaning with roof inspection
   📌 2026-03-01: Schedule HVAC service before summer

📆 Adding to calendar...
   ✓ Added: Replace HVAC filters
   ✓ Added: HVAC annual service
   ✓ Added: Clean gutters

💰 Analyzing costs...
   Original cost: $5,000.00
   Optimized cost: $3,500.00
   Savings: $1,500.00

📚 Generating maintenance guides...
   ✓ Guide ready: Replace HVAC filters
   ✓ Guide ready: Test smoke detectors

======================================================================
✅ Daily analysis complete!
```

## Advanced Features

### Multi-Agent Coordination

Agents work together autonomously:

1. **Predictive Agent** identifies risks
2. **Alert Agent** generates warnings
3. **Scheduling Agent** creates optimal plan
4. **Cost Agent** optimizes expenses
5. **Knowledge Agent** provides guidance
6. **Calendar Agent** schedules everything

### Constraint Solving

Handles complex constraints:

- Budget limits
- Time availability
- Weather dependencies
- Seasonal requirements
- Task dependencies
- Professional availability

### Adaptive Learning

System improves over time:

- Learns actual task durations
- Tracks cost accuracy
- Identifies failure patterns
- Refines predictions

## Use Cases

### Homeowners
- Never miss critical maintenance
- Prevent costly failures
- Optimize maintenance budget
- Get expert guidance

### Property Managers
- Manage multiple properties
- Automate maintenance scheduling
- Track costs across portfolio
- Ensure compliance

### Real Estate Investors
- Maintain property value
- Prevent tenant issues
- Budget accurately
- Scale operations

## Technical Highlights

**Multi-Agent System:**
- 6 specialized agents
- Autonomous coordination
- Real-time adaptation

**LLM-Powered:**
- Predictive failure analysis
- Constraint optimization
- Knowledge synthesis
- Cost analysis

**Real Integrations:**
- Google Calendar API
- OAuth authentication
- Event creation
- Reminder management

**State Management:**
- JSON persistence
- Task tracking
- Alert history
- Schedule optimization

## Comparison

| Feature | Traditional Apps | Home Maintenance Agent |
|---------|------------------|------------------------|
| Scheduling | Manual | Autonomous optimization |
| Predictions | None | ML-powered failure prediction |
| Cost optimization | None | Automatic analysis |
| Alerts | Basic reminders | Contextual + predictive |
| Guides | Generic | Task-specific, detailed |
| Calendar sync | Manual entry | Automatic integration |
| Multi-constraint | No | Yes (budget, time, weather) |

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Google Calendar (Optional)

```bash
# Download credentials.json from Google Cloud Console
# Place in project directory
# First run will open browser for OAuth
```

### 3. Set API Key

```bash
export ANTHROPIC_API_KEY=your_key_here
```

### 4. Run

```bash
python agent.py
```

## State Persistence

All data saved to `home_maintenance_state.json`:

```json
{
  "home_profile": {...},
  "tasks": [...],
  "alerts": [...],
  "schedule": [...]
}
```

## Future Enhancements

The architecture supports:
- IoT sensor integration (detect issues automatically)
- Contractor marketplace integration
- Parts ordering automation
- Photo documentation
- Warranty tracking
- Home value impact analysis

## License

MIT

---

Built with Claude 3.5 Sonnet. Part of the [Fun Agentic Apps](https://github.com/ndgbg/fun-agentic-apps) collection.
