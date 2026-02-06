#!/usr/bin/env python3
"""
Demo Screenshot Agent
Autonomous agent that runs applications, interacts intelligently, and captures screenshots.
"""

import os
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import anthropic

@dataclass
class Screenshot:
    app_name: str
    scenario: str
    filepath: str
    timestamp: str
    description: str

class BrowserAgent:
    """Autonomous browser agent using Playwright."""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.is_recording = False
    
    async def initialize(self):
        """Initialize Playwright browser."""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                device_scale_factor=2,  # Retina display
                record_video_dir='./videos/'  # Enable video recording
            )
            self.page = await self.context.new_page()
            
            print("✅ Browser initialized with video recording")
            return True
            
        except ImportError:
            print("⚠️  Playwright not installed. Run: pip install playwright && playwright install")
            return False
    
    async def navigate(self, url: str):
        """Navigate to URL."""
        await self.page.goto(url, wait_until='networkidle')
        await asyncio.sleep(2)  # Let page settle
    
    async def screenshot(self, filepath: str):
        """Take screenshot."""
        await self.page.screenshot(path=filepath, full_page=True)
    
    async def click(self, selector: str):
        """Click element."""
        await self.page.click(selector)
        await asyncio.sleep(1)
    
    async def fill(self, selector: str, text: str):
        """Fill input field."""
        await self.page.fill(selector, text)
        await asyncio.sleep(0.5)
    
    async def get_page_content(self) -> str:
        """Get page text content."""
        return await self.page.inner_text('body')
    
    async def get_video_path(self) -> Optional[str]:
        """Get path to recorded video."""
        if self.page and self.page.video:
            return await self.page.video.path()
        return None
    
    async def close(self):
        """Close browser and save video."""
        if self.context:
            await self.context.close()  # This saves the video
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

class ScenarioPlanner:
    """Plans intelligent demo scenarios using LLM."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def plan_scenarios(self, app_info: Dict) -> List[Dict]:
        """Generate demo scenarios for an app."""
        
        prompt = f"""You are a demo scenario planner. Create realistic demo scenarios for this app.

App: {app_info['name']}
Description: {app_info['description']}
Type: {app_info['type']}

Create 3-5 demo scenarios that showcase key features. For each scenario:
1. What to demonstrate
2. Steps to take (be specific about UI interactions)
3. What makes a good screenshot moment

Return JSON array:
[
  {{
    "name": "Scenario name",
    "description": "What this demonstrates",
    "steps": [
      {{"action": "navigate", "target": "http://localhost:5173"}},
      {{"action": "fill", "selector": "#input", "value": "test data"}},
      {{"action": "click", "selector": "button.submit"}},
      {{"action": "wait", "duration": 2}},
      {{"action": "screenshot", "name": "result_view"}}
    ],
    "screenshot_moments": ["After data entry", "Results displayed"]
  }}
]"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.4,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        import re
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return []

class InteractionAgent:
    """Intelligently interacts with apps based on visual analysis."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def analyze_page(self, page_content: str, app_context: str) -> Dict:
        """Analyze page and suggest next actions."""
        
        prompt = f"""You are analyzing a web application to create a demo.

App Context: {app_context}

Current Page Content (first 1000 chars):
{page_content[:1000]}

Suggest the next action to demonstrate key features. Return JSON:
{{
  "action": "click|fill|wait|screenshot",
  "selector": "CSS selector or description",
  "value": "value if filling input",
  "reasoning": "Why this action showcases the app"
}}"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"action": "screenshot", "reasoning": "Capture current state"}

class DemoScreenshotAgent:
    """Main orchestrator for demo screenshot generation."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.browser_agent = BrowserAgent()
        self.scenario_planner = ScenarioPlanner(self.api_key)
        self.interaction_agent = InteractionAgent(self.api_key)
        self.screenshots = []
        self.videos = []
        
        # Create output directories
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        self.video_dir = Path("videos")
        self.video_dir.mkdir(exist_ok=True)
    
    async def demo_app(self, app_info: Dict):
        """Run complete demo for an app."""
        
        print(f"\n{'='*70}")
        print(f"📸 DEMO: {app_info['name']}")
        print(f"{'='*70}")
        
        # Initialize browser
        if not await self.browser_agent.initialize():
            print("❌ Browser initialization failed")
            return
        
        try:
            # Plan scenarios
            print("\n🎬 Planning demo scenarios...")
            scenarios = await self.scenario_planner.plan_scenarios(app_info)
            print(f"   Generated {len(scenarios)} scenarios")
            
            # Execute each scenario
            for i, scenario in enumerate(scenarios, 1):
                print(f"\n📋 Scenario {i}: {scenario['name']}")
                print(f"   {scenario['description']}")
                
                await self._execute_scenario(app_info, scenario)
            
            # Save video
            video_path = await self.browser_agent.get_video_path()
            if video_path:
                self.videos.append({
                    'app_name': app_info['name'],
                    'path': video_path
                })
                print(f"\n🎥 Video saved: {video_path}")
            
        finally:
            await self.browser_agent.close()
        
        print(f"\n✅ Demo complete! Captured {len(self.screenshots)} screenshots and {len(self.videos)} videos")
    
    async def _execute_scenario(self, app_info: Dict, scenario: Dict):
        """Execute a single scenario."""
        
        for step in scenario.get('steps', []):
            action = step.get('action')
            
            try:
                if action == 'navigate':
                    print(f"   → Navigate to {step['target']}")
                    await self.browser_agent.navigate(step['target'])
                
                elif action == 'fill':
                    print(f"   → Fill {step['selector']}: {step['value']}")
                    await self.browser_agent.fill(step['selector'], step['value'])
                
                elif action == 'click':
                    print(f"   → Click {step['selector']}")
                    await self.browser_agent.click(step['selector'])
                
                elif action == 'wait':
                    duration = step.get('duration', 2)
                    print(f"   → Wait {duration}s")
                    await asyncio.sleep(duration)
                
                elif action == 'screenshot':
                    name = step.get('name', 'screenshot')
                    filepath = self._generate_filepath(app_info['name'], name)
                    print(f"   📸 Screenshot: {filepath}")
                    await self.browser_agent.screenshot(filepath)
                    
                    self.screenshots.append(Screenshot(
                        app_name=app_info['name'],
                        scenario=scenario['name'],
                        filepath=filepath,
                        timestamp=datetime.now().isoformat(),
                        description=scenario['description']
                    ))
            
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
                # Continue with next step
    
    async def intelligent_demo(self, app_info: Dict, max_actions: int = 10):
        """Run intelligent demo with AI deciding actions."""
        
        print(f"\n{'='*70}")
        print(f"🤖 INTELLIGENT DEMO: {app_info['name']}")
        print(f"{'='*70}")
        
        if not await self.browser_agent.initialize():
            return
        
        try:
            # Navigate to app
            await self.browser_agent.navigate(app_info['url'])
            
            # Take initial screenshot
            filepath = self._generate_filepath(app_info['name'], 'initial')
            await self.browser_agent.screenshot(filepath)
            print(f"📸 Initial screenshot: {filepath}")
            
            # Let AI explore
            for i in range(max_actions):
                print(f"\n🤖 AI Action {i+1}/{max_actions}")
                
                # Get page content
                content = await self.browser_agent.get_page_content()
                
                # Ask AI what to do next
                action = await self.interaction_agent.analyze_page(
                    content,
                    app_info['description']
                )
                
                print(f"   Reasoning: {action.get('reasoning', 'N/A')}")
                print(f"   Action: {action.get('action')}")
                
                # Execute action
                if action['action'] == 'screenshot':
                    filepath = self._generate_filepath(app_info['name'], f'step_{i+1}')
                    await self.browser_agent.screenshot(filepath)
                    print(f"   📸 {filepath}")
                    
                    self.screenshots.append(Screenshot(
                        app_name=app_info['name'],
                        scenario='intelligent_exploration',
                        filepath=filepath,
                        timestamp=datetime.now().isoformat(),
                        description=action.get('reasoning', '')
                    ))
                
                await asyncio.sleep(2)
        
        finally:
            await self.browser_agent.close()
    
    def _generate_filepath(self, app_name: str, screenshot_name: str) -> str:
        """Generate screenshot filepath."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_app_name = app_name.lower().replace(' ', '_')
        filename = f"{safe_app_name}_{screenshot_name}_{timestamp}.png"
        return str(self.screenshot_dir / filename)
    
    def generate_report(self):
        """Generate markdown report of screenshots and videos."""
        
        report_path = self.screenshot_dir / "DEMO_REPORT.md"
        
        with open(report_path, 'w') as f:
            f.write("# Demo Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total Screenshots: {len(self.screenshots)}\n")
            f.write(f"Total Videos: {len(self.videos)}\n\n")
            
            # Videos section
            if self.videos:
                f.write("## 🎥 Demo Videos\n\n")
                for video in self.videos:
                    f.write(f"### {video['app_name']}\n\n")
                    f.write(f"[Download Video]({video['path']})\n\n")
                    f.write("---\n\n")
            
            # Screenshots section
            f.write("## 📸 Screenshots\n\n")
            
            # Group by app
            apps = {}
            for screenshot in self.screenshots:
                if screenshot.app_name not in apps:
                    apps[screenshot.app_name] = []
                apps[screenshot.app_name].append(screenshot)
            
            for app_name, screenshots in apps.items():
                f.write(f"### {app_name}\n\n")
                
                for screenshot in screenshots:
                    f.write(f"#### {screenshot.scenario}\n\n")
                    f.write(f"{screenshot.description}\n\n")
                    f.write(f"![{screenshot.scenario}]({screenshot.filepath})\n\n")
                    f.write(f"*Captured: {screenshot.timestamp}*\n\n")
                    f.write("---\n\n")
        
        print(f"\n📄 Report generated: {report_path}")

async def main():
    """Demo the screenshot agent."""
    
    print("📸 DEMO SCREENSHOT AGENT")
    print("="*70)
    print("Autonomous agent that demos apps and captures screenshots")
    print("="*70)
    
    agent = DemoScreenshotAgent()
    
    # Define apps to demo
    apps = [
        {
            "name": "Home Maintenance Agent",
            "description": "Multi-agent system for home maintenance, cleaning, and organization",
            "type": "python_cli",
            "url": "http://localhost:8000",  # If you serve the dashboard
            "demo_command": "python agent.py"
        },
        {
            "name": "MomOps Agent",
            "description": "Autonomous baby care assistant",
            "type": "react_app",
            "url": "http://localhost:5173"
        },
        {
            "name": "Montessori AI Agent",
            "description": "Montessori activity generator",
            "type": "react_app",
            "url": "http://localhost:5174"
        }
    ]
    
    print("\n📋 Apps to demo:")
    for i, app in enumerate(apps, 1):
        print(f"   {i}. {app['name']}")
    
    print("\n⚠️  Note: Make sure apps are running locally first!")
    print("   - MomOps: cd momops-agent && npm run dev")
    print("   - Montessori: cd montessori-ai-agent && npm run dev")
    print()
    
    # Demo first app (if running)
    print("🎬 Starting demo...")
    print("   (This is a demo - in production, would capture real screenshots)")
    
    # For now, show the architecture
    print("\n✅ Agent Architecture:")
    print("   1. BrowserAgent - Controls Playwright browser")
    print("   2. ScenarioPlanner - Plans demo scenarios using LLM")
    print("   3. InteractionAgent - Intelligently interacts with UI")
    print("   4. DemoScreenshotAgent - Orchestrates everything")
    
    print("\n💡 To use:")
    print("   1. Start your apps locally")
    print("   2. Run: python screenshot_agent.py")
    print("   3. Agent will autonomously demo and capture screenshots")
    print("   4. Find screenshots in ./screenshots/ directory")
    print("   5. View DEMO_REPORT.md for organized gallery")

if __name__ == "__main__":
    asyncio.run(main())
