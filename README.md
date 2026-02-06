# Fun Agentic Apps 🤖

> A collection of autonomous AI agents built to solve real-world problems

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub stars](https://img.shields.io/github/stars/ndgbg/fun-agentic-apps?style=social)](https://github.com/ndgbg/fun-agentic-apps/stargazers)

## What Makes These Apps "Agentic"?

These aren't just smart apps — they're **autonomous agents** that:
- 🎯 Operate independently without constant user input
- 💡 Proactively identify problems and suggest solutions
- 🧠 Reason through complex situations with explainable logic
- 📈 Learn from patterns and adapt recommendations
- 🎪 Pursue goals autonomously

## 🤖 Apps

### [Calendar Negotiation Agent](calendar-negotiation-agent/)
Autonomous scheduling that handles the entire meeting coordination process.

**What it does:**
- Analyzes timezone constraints and participant preferences
- Proposes optimal meeting times with reasoning
- Handles responses and objections autonomously
- Books conference rooms and creates video links
- Manages rescheduling when conflicts arise

**Why it's agentic:**
- Multi-step reasoning about constraints
- Tool use (calendar APIs, email, room booking)
- Adaptive strategy based on feedback
- Autonomous decision-making (confirm vs. renegotiate)
- State management across negotiation rounds

### [Product Spec Reviewer](product-spec-reviewer/)
Your toughest stakeholder — automated. Reviews product specs using LLM reasoning.

**What it does:**
- Flags critical issues with evidence from your spec
- Asks brutal questions from 6 personas (CTO, CEO, User Advocate, Risk Manager, AI Ethics, Finance)
- Suggests specific improvements
- Answers follow-up questions

**Why it's agentic:**
- Understands context, not just pattern matching
- Reasons about implications and consequences
- Adapts questions based on spec content
- Provides evidence-based feedback

### [Multi-Agent Workflow Playground](multi-agent-workflow-playground/)
LangChain, but opinionated and visual. Build and execute multi-agent systems with drag-and-drop.

**What it does:**
- Drag-and-drop visual workflow builder
- Configure agent roles, memory, and tools
- Execute workflows with real LLM calls
- Inspect execution traces and failures
- Compare different architectures

**Why it's agentic:**
- Autonomous agent execution with decision-making
- Dynamic routing based on conditions
- Stateful memory (short-term, long-term, shared)
- Real tool integration (web search, calculator, file I/O)
- Adaptive behavior based on previous outputs

### [LLM Evaluation Agent](llm-evaluation-agent/)
Eval-as-a-service, but local. Autonomous evaluation system for LLM outputs.

**What it does:**
- Autonomously generates evaluation rubrics
- Scores outputs with detailed reasoning
- Detects quality regressions automatically
- Tracks hallucinations over time
- Provides trend analysis and alerts

**Why it's agentic:**
- Analyzes tasks to create appropriate rubrics
- Reasons about quality with evidence
- Learns baselines and adapts over time
- Identifies patterns in failures
- Makes pass/fail decisions autonomously

### [Personal Chief of Staff](personal-chief-of-staff/)
A local AI that runs your life ops. Self-hosted, proactive, and memory-enabled.

**What it does:**
- Generates daily briefings with priorities and warnings
- Autonomously re-ranks tasks based on context
- Proactively warns about approaching deadlines
- Provides context switching support
- Answers "What should I focus on today?"

**Why it's agentic:**
- Learns your work patterns and energy levels
- Reasons about urgency vs importance tradeoffs
- Aligns daily tasks with long-term goals
- Proactively identifies conflicts and blockers
- Adapts recommendations to current context
- Makes decisions about priority ranking

### [Home Maintenance Agent](home-maintenance-agent/)
Sophisticated multi-agent system for complete home management - maintenance, cleaning, and organization.

**What it does:**
- Predicts system failures before they occur (ML-powered)
- Manages 19 tasks: maintenance, cleaning, organization
- Tracks everything from HVAC to trash day to closet organization
- Optimizes schedule (budget, time, weather, season)
- Generates contextual alerts (overdue, predictive, weather-based)
- Integrates with Google Calendar (auto-scheduling)
- Optimizes costs (DIY vs professional, bulk purchasing)
- Generates detailed guides for every task

**Why it's agentic:**
- 6 specialized agents working in coordination
- Predictive analytics using LLM reasoning
- Multi-constraint optimization (budget, time, weather, dependencies)
- Autonomous decision-making and scheduling
- Real-time adaptation to conditions
- Knowledge synthesis from maintenance data

### [MomOps Agent](momops-agent/)
Truly agentic baby care assistant for new parents.

**What it does:**
- Continuously monitors feeding, sleep, and diaper patterns
- Proactively suggests feeding times and sleep schedules
- Learns from your responses and adapts to baby's unique patterns
- Provides intelligent chat with contextual awareness
- Tracks caregiver schedules and milestones
- Visual analytics and pattern detection

**Why it's agentic:**
- Autonomous background monitoring
- Proactive recommendations (suggests before you ask)
- Continuous learning from interactions
- Adapts to baby's unique patterns
- LLM-powered contextual advice
- Progressive enhancement (works offline, better with AI)

### [Montessori AI Agent](montessori-ai-agent/)
Autonomous AI assistant for Montessori-based early childhood development.

**What it does:**
- Generates personalized Montessori activities for your child
- Adapts recommendations based on engagement patterns
- Provides age-appropriate developmental activities
- Learns from child's interests and progress
- Privacy-first (all data stored locally)

**Why it's agentic:**
- Observes child's engagement patterns
- Reasons about developmental needs using Montessori principles
- Autonomously generates personalized activities
- Continuous learning loop (observe → reason → act → learn)
- Real LLM integration (OpenAI, Anthropic, Ollama)
- Adapts difficulty based on child's progress

### [Demo Screenshot Agent](demo-screenshot-agent/)
Autonomous agent that runs your applications and captures professional screenshots.

**What it does:**
- Controls real browsers using Playwright
- Generates realistic demo scenarios using LLM
- Intelligently interacts with UI (analyzes, clicks, fills)
- Captures screenshots at perfect moments
- Generates organized markdown reports
- Demos multiple apps in sequence

**Why it's agentic:**
- Autonomous exploration (no predefined scripts)
- Visual reasoning (analyzes page content)
- Adaptive behavior (adjusts based on what it sees)
- Goal-oriented (showcases key features)
- Self-documenting (generates reports automatically)
- Intelligent timing (knows when to capture)
- Real LLM integration (OpenAI, Anthropic, Ollama)
- Adapts difficulty based on child's progress

## 🤝 Contributing

Want to add your own agentic app? We welcome contributions!

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📫 Connect

- GitHub: [@ndgbg](https://github.com/ndgbg)
- LinkedIn: [Nida Beig](https://www.linkedin.com/in/nida-beig/)

## ⭐ Show Your Support

If you find these projects helpful, give them a star! It helps others discover autonomous AI agents.

---

Built with [Kiro](https://kiro.dev/) - AI-powered development environment
