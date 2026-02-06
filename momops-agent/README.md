# MomOps - Truly Agentic Baby Care Assistant

New parents struggle to track feeding, sleep, and diaper patterns while managing caregivers and remembering pediatrician advice. Existing apps are either too complex or lack intelligent insights. MomOps is a **truly agentic** baby care assistant that autonomously monitors patterns, proactively suggests actions, and continuously learns from your interactions.

**Built with:** React 18, Vite, CSS3, LocalStorage + **Lightweight LLM Integration**

## 🎥 Demo

https://github.com/user-attachments/assets/c21db00e-6064-d47e-8f3d-33a5422ddf1b

## 🤖 Autonomous AI Features

**Continuous Monitoring** - Autonomous agent runs in background, analyzing patterns and detecting when action is needed

**Proactive Recommendations** - AI suggests feeding times, sleep schedules, and diaper checks before you need to think about them

**Smart Learning** - Agent learns from your responses and adapts recommendations to your baby's unique patterns

**Lightweight LLM** - Progressive enhancement with Llama integration for intelligent chat and contextual advice

## Core Features

**🏠 Home Dashboard** - Quick-log activities with AI-powered recommendations displayed prominently

**📊 Insights & Analytics** - Visual charts, pattern analysis, and intelligent daily insights powered by autonomous monitoring

**🤖 Agent Dashboard** - View detailed AI reasoning, recommendation confidence scores, and autonomous decision-making process

**💬 Intelligent Chat** - LLM-powered assistant for parenting questions with contextual awareness of your baby's data

**📅 Schedule Manager** - Track caregiver schedules with hourly rates and cumulative hours

**👶 Baby Profile** - Track milestones, age, and memories with AI-suggested developmental activities

## LLM Integration

MomOps uses a **progressive enhancement** approach to AI:

- **Demo Mode**: Works fully offline with simulated AI responses
- **Llama Integration**: Lightweight local LLM for enhanced chat and recommendations
- **Fallback System**: Graceful degradation if LLM unavailable
- **Privacy First**: All AI processing happens locally when possible

## Quick Start

```bash
git clone https://github.com/ndgbg/momops-agent.git
cd momops-agent
npm install
npm run dev
```

Open `http://localhost:5173` and start tracking! 

**To see AI recommendations:** Use the menu (⋮) → "Load Sample Data" to populate with realistic baby care data and activate autonomous monitoring.

## Autonomous Agent Architecture

- **Observe-Reason-Act-Learn Loop**: Continuous monitoring with intelligent decision-making
- **Specialized Sub-Agents**: Dedicated agents for sleep, feeding, and development tracking  
- **Proactive Notifications**: Smart alerts with user action tracking and learning
- **Pattern Recognition**: Analyzes feeding intervals, sleep quality, and developmental progress

## Data Privacy

All data stays local in your browser. LLM processing happens locally when available. Nothing is sent to external servers.

## License

MIT License

---

Made with ❤️ for parents everywhere
