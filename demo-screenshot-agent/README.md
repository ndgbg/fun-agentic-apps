# 📸 Demo Screenshot Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude%203.5-orange.svg)](https://www.anthropic.com/)
[![Playwright](https://img.shields.io/badge/Playwright-Browser%20Automation-green.svg)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Autonomous agent that runs your applications, interacts intelligently, and captures professional screenshots for documentation.**

Never manually screenshot demos again. Let AI explore your apps and capture the perfect moments.

## What It Does

- **Autonomous browser control** - Uses Playwright to control real browsers
- **Intelligent scenario planning** - LLM generates realistic demo scenarios
- **Smart interaction** - AI analyzes pages and decides what to click/fill
- **Perfect timing** - Captures screenshots at key moments
- **Organized output** - Generates markdown report with all screenshots
- **Multi-app support** - Demos multiple apps in sequence

## Why It's Agentic

This showcases advanced agentic patterns:

- **Autonomous exploration** - Agent explores apps without predefined scripts
- **Visual reasoning** - Analyzes page content to decide next actions
- **Scenario generation** - Creates realistic demo flows using LLM
- **Adaptive behavior** - Adjusts based on what it sees
- **Goal-oriented** - Focuses on showcasing key features
- **Self-documenting** - Generates reports automatically

## Architecture

```
DemoScreenshotAgent
├── BrowserAgent
│   └── Playwright browser automation
├── ScenarioPlanner
│   └── LLM-powered scenario generation
├── InteractionAgent
│   └── Intelligent page analysis and interaction
└── Report Generator
    └── Markdown gallery creation
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Start your apps
cd ../momops-agent && npm run dev &
cd ../montessori-ai-agent && npm run dev &

# Run agent
python screenshot_agent.py
```

## Features

### 1. Scenario Planning

Agent analyzes your app and generates realistic demo scenarios:

```python
scenarios = await planner.plan_scenarios({
    "name": "Home Maintenance Agent",
    "description": "Multi-agent home management system",
    "type": "python_cli"
})

# Generated scenarios:
# 1. "Initial Setup" - Configure home profile
# 2. "Daily Briefing" - Show predictive maintenance
# 3. "Cost Optimization" - Demonstrate savings analysis
```

### 2. Intelligent Interaction

Agent analyzes page content and decides what to do:

```python
action = await interaction_agent.analyze_page(
    page_content,
    app_context
)

# AI decides:
# - What element to click
# - What data to enter
# - When to take screenshot
# - Why this showcases the feature
```

### 3. Perfect Screenshots

Captures at key moments:
- After data entry
- When results are displayed
- During state transitions
- At visual highlights

### 4. Organized Output

Generates professional report:

```markdown
## Home Maintenance Agent

### Initial Setup
Shows home profile configuration with 19 tracked tasks.

![Initial Setup](screenshots/home_maintenance_initial_20260206_120000.png)

*Captured: 2026-02-06T12:00:00*

---

### Predictive Analysis
Demonstrates ML-powered failure prediction.

![Predictive Analysis](screenshots/home_maintenance_prediction_20260206_120030.png)
```

## Usage

### Basic Demo

```python
from screenshot_agent import DemoScreenshotAgent

agent = DemoScreenshotAgent()

app_info = {
    "name": "My App",
    "description": "What it does",
    "url": "http://localhost:3000"
}

await agent.demo_app(app_info)
```

### Intelligent Exploration

Let AI explore autonomously:

```python
await agent.intelligent_demo(app_info, max_actions=10)

# AI will:
# 1. Navigate to app
# 2. Analyze what it sees
# 3. Decide what to interact with
# 4. Capture screenshots at key moments
# 5. Repeat until max_actions
```

### Generate Report

```python
agent.generate_report()

# Creates:
# - screenshots/DEMO_REPORT.md
# - Organized by app
# - Embedded images
# - Timestamps and descriptions
```

## Example Scenarios

### Home Maintenance Agent

**Scenario 1: Daily Briefing**
1. Run `python agent.py`
2. Capture terminal output showing:
   - Predictive analysis (3 potential failures)
   - Alert generation (5 alerts)
   - Schedule optimization (8 tasks)
   - Cost analysis ($1,500 savings)

**Scenario 2: Task Management**
1. Show 19 tracked tasks
2. Highlight seasonal tasks (winterization)
3. Display cleaning schedule
4. Show calendar integration

### MomOps Agent

**Scenario 1: Baby Tracking**
1. Navigate to dashboard
2. Log feeding event
3. Show AI recommendation appearing
4. Capture insights chart

**Scenario 2: AI Chat**
1. Open chat interface
2. Ask parenting question
3. Show contextual AI response
4. Highlight baby data integration

### Montessori AI Agent

**Scenario 1: Activity Generation**
1. Enter child profile
2. Show AI generating activities
3. Display personalized recommendations
4. Capture engagement tracking

## Advanced Features

### Custom Scenarios

Define your own scenarios:

```python
scenario = {
    "name": "User Onboarding",
    "description": "First-time user experience",
    "steps": [
        {"action": "navigate", "target": "http://localhost:3000"},
        {"action": "fill", "selector": "#name", "value": "John Doe"},
        {"action": "click", "selector": "button.start"},
        {"action": "wait", "duration": 2},
        {"action": "screenshot", "name": "welcome_screen"}
    ]
}
```

### Multi-App Batch

Demo multiple apps in sequence:

```python
apps = [
    {"name": "App 1", "url": "http://localhost:3000"},
    {"name": "App 2", "url": "http://localhost:3001"},
    {"name": "App 3", "url": "http://localhost:3002"}
]

for app in apps:
    await agent.demo_app(app)

agent.generate_report()  # Single report for all apps
```

### Screenshot Customization

```python
# High-resolution screenshots
viewport = {'width': 2560, 'height': 1440}
device_scale_factor = 2  # Retina

# Full page vs viewport
full_page = True  # Capture entire scrollable page

# Custom naming
filepath = f"{app_name}_{feature}_{timestamp}.png"
```

## Output Structure

```
screenshots/
├── DEMO_REPORT.md
├── home_maintenance_initial_20260206_120000.png
├── home_maintenance_prediction_20260206_120030.png
├── momops_dashboard_20260206_120100.png
├── momops_ai_chat_20260206_120130.png
├── montessori_activities_20260206_120200.png
└── montessori_engagement_20260206_120230.png
```

## Use Cases

### Documentation
- Automatically update README screenshots
- Generate user guides
- Create tutorial images

### Marketing
- Product demo screenshots
- Feature highlights
- Before/after comparisons

### Testing
- Visual regression testing
- UI consistency checks
- Cross-browser screenshots

### Presentations
- Demo slides
- Investor decks
- Conference talks

## Technical Highlights

**Browser Automation:**
- Playwright for reliable automation
- Headless or headed mode
- Multiple browser support (Chromium, Firefox, WebKit)

**AI-Powered:**
- LLM scenario generation
- Intelligent page analysis
- Adaptive interaction
- Natural language reasoning

**Production-Ready:**
- Error handling
- Retry logic
- Screenshot optimization
- Organized output

## Comparison

| Feature | Manual Screenshots | Selenium Scripts | Screenshot Agent |
|---------|-------------------|------------------|------------------|
| Planning | Manual | Hardcoded | AI-generated |
| Interaction | Manual | Scripted | Intelligent |
| Timing | Manual | Fixed waits | Adaptive |
| Organization | Manual | None | Automatic |
| Maintenance | High | Medium | Low |
| Flexibility | Low | Medium | High |

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY=your_key_here
```

### 3. Start Your Apps

```bash
# Terminal 1
cd momops-agent && npm run dev

# Terminal 2
cd montessori-ai-agent && npm run dev

# Terminal 3
cd home-maintenance-agent && python agent.py
```

### 4. Run Agent

```bash
python screenshot_agent.py
```

### 5. View Results

```bash
open screenshots/DEMO_REPORT.md
```

## Configuration

Edit `screenshot_agent.py` to customize:

```python
# Apps to demo
apps = [
    {
        "name": "Your App",
        "description": "What it does",
        "url": "http://localhost:3000"
    }
]

# Screenshot settings
viewport = {'width': 1920, 'height': 1080}
device_scale_factor = 2

# AI settings
max_actions = 10  # For intelligent exploration
temperature = 0.4  # For scenario generation
```

## Limitations

- Requires apps to be running locally
- Best for web applications
- CLI apps need terminal capture (separate tool)
- Requires Anthropic API key

## Future Enhancements

The architecture supports:
- Video recording (not just screenshots)
- Multi-browser testing
- Mobile device emulation
- Accessibility testing
- Performance metrics
- A/B comparison screenshots

## License

MIT

---

Built with Claude 3.5 Sonnet and Playwright. Part of the [Fun Agentic Apps](https://github.com/ndgbg/fun-agentic-apps) collection.
