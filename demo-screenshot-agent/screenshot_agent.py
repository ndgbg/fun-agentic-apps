#!/usr/bin/env python3
"""
Demo Screenshot Agent
Autonomous agent that runs applications, interacts intelligently, and captures screenshots.
Uses Anthropic tool_use API for a proper agentic loop.
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

            print("Browser initialized with video recording")
            return True

        except ImportError:
            print("Playwright not installed. Run: pip install playwright && playwright install")
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

    async def get_page_url(self) -> str:
        """Get current page URL."""
        return self.page.url

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

SYSTEM_PROMPT = (
    "You are an autonomous demo agent. You control a web browser to demonstrate "
    "applications. You can navigate, click, fill inputs, take screenshots, and read "
    "page content. Explore the application systematically: navigate to the app, read "
    "the page, interact with key features, and take screenshots at interesting moments. "
    "Be thorough - try different features and capture the app's best moments."
)

class DemoScreenshotAgent:
    """Main orchestrator for demo screenshot generation."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.browser_agent = BrowserAgent()
        self.screenshots: List[Screenshot] = []
        self.videos: List[Dict] = []

        # Create output directories
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        self.video_dir = Path("videos")
        self.video_dir.mkdir(exist_ok=True)

    def _get_tool_definitions(self) -> List[Dict]:
        """Return Anthropic tool schemas for browser interaction."""
        return [
            {
                "name": "navigate_to_url",
                "description": "Navigate the browser to a specific URL.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to navigate to."
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "click_element",
                "description": "Click on an element identified by a CSS selector.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector of the element to click."
                        }
                    },
                    "required": ["selector"]
                }
            },
            {
                "name": "fill_input",
                "description": "Type text into an input field identified by a CSS selector.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector of the input element."
                        },
                        "value": {
                            "type": "string",
                            "description": "The text to type into the input."
                        }
                    },
                    "required": ["selector", "value"]
                }
            },
            {
                "name": "take_screenshot",
                "description": "Capture a screenshot of the current page state.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "A short descriptive name for this screenshot (used in filename)."
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of what this screenshot captures."
                        }
                    },
                    "required": ["name", "description"]
                }
            },
            {
                "name": "get_page_content",
                "description": "Read the current page's text content. Returns the visible text on the page.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "wait",
                "description": "Wait for a specified number of seconds for content to load.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "seconds": {
                            "type": "number",
                            "description": "Number of seconds to wait."
                        }
                    },
                    "required": ["seconds"]
                }
            },
            {
                "name": "get_page_url",
                "description": "Get the current page URL.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    async def _execute_tool(self, name: str, tool_input: Dict) -> Dict:
        """Dispatch a tool call to the appropriate BrowserAgent method."""
        try:
            if name == "navigate_to_url":
                url = tool_input["url"]
                print(f"   -> Navigating to {url}")
                await self.browser_agent.navigate(url)
                return {"status": "success", "message": f"Navigated to {url}"}

            elif name == "click_element":
                selector = tool_input["selector"]
                print(f"   -> Clicking {selector}")
                await self.browser_agent.click(selector)
                return {"status": "success", "message": f"Clicked {selector}"}

            elif name == "fill_input":
                selector = tool_input["selector"]
                value = tool_input["value"]
                print(f"   -> Filling {selector} with: {value}")
                await self.browser_agent.fill(selector, value)
                return {"status": "success", "message": f"Filled {selector}"}

            elif name == "take_screenshot":
                screenshot_name = tool_input["name"]
                description = tool_input["description"]
                filepath = self._generate_filepath(self._current_app_name, screenshot_name)
                print(f"   [screenshot] {filepath}")
                await self.browser_agent.screenshot(filepath)
                self.screenshots.append(Screenshot(
                    app_name=self._current_app_name,
                    scenario="tool_use_exploration",
                    filepath=filepath,
                    timestamp=datetime.now().isoformat(),
                    description=description
                ))
                return {"status": "success", "filepath": filepath, "message": f"Screenshot saved to {filepath}"}

            elif name == "get_page_content":
                print("   -> Reading page content")
                content = await self.browser_agent.get_page_content()
                # Truncate to avoid massive token usage
                truncated = content[:3000]
                if len(content) > 3000:
                    truncated += "\n... (content truncated)"
                return {"status": "success", "content": truncated}

            elif name == "wait":
                seconds = tool_input["seconds"]
                print(f"   -> Waiting {seconds}s")
                await asyncio.sleep(seconds)
                return {"status": "success", "message": f"Waited {seconds} seconds"}

            elif name == "get_page_url":
                url = await self.browser_agent.get_page_url()
                print(f"   -> Current URL: {url}")
                return {"status": "success", "url": url}

            else:
                return {"status": "error", "message": f"Unknown tool: {name}"}

        except Exception as e:
            print(f"   [error] {name}: {e}")
            return {"status": "error", "message": str(e)}

    async def demo_app(self, app_info: Dict, max_actions: int = 30):
        """Run a complete demo for an app using the agentic tool-use loop."""

        print(f"\n{'='*70}")
        print(f"DEMO: {app_info['name']}")
        print(f"{'='*70}")

        # Initialize browser
        if not await self.browser_agent.initialize():
            print("Browser initialization failed")
            return

        self._current_app_name = app_info["name"]

        try:
            await self._run_agentic_loop(app_info, max_actions)

            # Save video
            video_path = await self.browser_agent.get_video_path()
            if video_path:
                self.videos.append({
                    'app_name': app_info['name'],
                    'path': video_path
                })
                print(f"\nVideo saved: {video_path}")

        finally:
            await self.browser_agent.close()

        print(f"\nDemo complete! Captured {len(self.screenshots)} screenshots and {len(self.videos)} videos")

    async def _run_agentic_loop(self, app_info: Dict, max_actions: int):
        """Core agentic loop: LLM decides actions via tool_use, agent executes them."""

        messages = [
            {
                "role": "user",
                "content": (
                    f"Demo this app: {app_info['name']}. "
                    f"URL: {app_info['url']}. "
                    f"Description: {app_info['description']}. "
                    "Navigate to it, explore the features, interact with UI elements, "
                    "and take screenshots of interesting states."
                )
            }
        ]

        tools = self._get_tool_definitions()

        for i in range(max_actions):
            print(f"\n--- Agent step {i + 1}/{max_actions} ---")

            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=messages
            )

            # Append the assistant's response to the conversation
            messages.append({"role": "assistant", "content": response.content})

            # If the model stopped naturally, we are done
            if response.stop_reason == "end_turn":
                # Print any final text the model emitted
                for block in response.content:
                    if hasattr(block, "text"):
                        print(f"   Agent: {block.text}")
                print("\nAgent finished exploration.")
                break

            # Process tool calls
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"   Tool call: {block.name}({json.dumps(block.input)})")
                        result = await self._execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, default=str)
                        })
                    elif hasattr(block, "text") and block.text:
                        print(f"   Agent: {block.text}")

                messages.append({"role": "user", "content": tool_results})

    def _generate_filepath(self, app_name: str, screenshot_name: str) -> str:
        """Generate screenshot filepath."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_app_name = app_name.lower().replace(' ', '_')
        safe_screenshot = screenshot_name.lower().replace(' ', '_')
        filename = f"{safe_app_name}_{safe_screenshot}_{timestamp}.png"
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
                f.write("## Demo Videos\n\n")
                for video in self.videos:
                    f.write(f"### {video['app_name']}\n\n")
                    f.write(f"[Download Video]({video['path']})\n\n")
                    f.write("---\n\n")

            # Screenshots section
            f.write("## Screenshots\n\n")

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

        print(f"\nReport generated: {report_path}")

async def main():
    """Demo the screenshot agent."""

    print("DEMO SCREENSHOT AGENT")
    print("="*70)
    print("Autonomous agent that demos apps and captures screenshots")
    print("using Anthropic tool_use for a proper agentic loop")
    print("="*70)

    agent = DemoScreenshotAgent()

    # Define apps to demo
    apps = [
        {
            "name": "Home Maintenance Agent",
            "description": "Multi-agent system for home maintenance, cleaning, and organization",
            "type": "python_cli",
            "url": "http://localhost:8000",
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

    print("\nApps to demo:")
    for i, app in enumerate(apps, 1):
        print(f"   {i}. {app['name']}")

    print("\nNote: Make sure apps are running locally first!")
    print("   - MomOps: cd momops-agent && npm run dev")
    print("   - Montessori: cd montessori-ai-agent && npm run dev")
    print()

    # Demo each app using the agentic loop
    for app in apps:
        await agent.demo_app(app)

    # Generate report
    agent.generate_report()

if __name__ == "__main__":
    asyncio.run(main())
