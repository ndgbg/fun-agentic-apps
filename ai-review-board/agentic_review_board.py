#!/usr/bin/env python3
"""
Agentic AI Product Review Board
Uses LLM to intelligently review product specs with reasoning and follow-ups.
"""

import os
import json
from datetime import datetime

class AgenticReviewBoard:
    def __init__(self, api_key=None):
        self.name = "Agentic AI Product Review Board"
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        self.system_prompt = """You are an experienced product review board consisting of multiple stakeholders. Your job is to review product specifications critically and provide actionable feedback.

You embody these personas:
- 😤 Skeptical CTO: Questions technical feasibility, scalability, and architecture
- 📊 Data-Driven CEO: Demands clear metrics, ROI, and business impact
- 👥 User Advocate: Challenges assumptions about user needs and validates with research
- 🛡️ Risk Manager: Identifies safety, compliance, and operational risks
- 🤖 AI Ethics Officer: Evaluates bias, fairness, and responsible AI practices
- 💰 Finance Director: Analyzes costs, revenue impact, and resource allocation

Your review process:
1. Read the spec carefully
2. Identify specific issues with evidence from the text
3. Ask probing questions that expose gaps
4. Suggest concrete improvements
5. Provide an overall verdict

Be direct, specific, and constructive. Quote from the spec when pointing out issues."""

    def review_spec(self, spec_text: str) -> dict:
        """Review a spec using LLM reasoning."""
        
        if not self.api_key:
            return self._mock_review(spec_text)
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"""Review this product specification:

{spec_text}

Provide your review in this JSON format:
{{
    "verdict": {{"status": "BLOCKED|NEEDS_WORK|CONCERNS|APPROVED", "reasoning": "why"}},
    "critical_issues": [
        {{"issue": "description", "evidence": "quote from spec", "impact": "what breaks"}}
    ],
    "questions_by_persona": {{
        "skeptical_cto": ["question1", "question2"],
        "data_driven_ceo": ["question1", "question2"],
        "user_advocate": ["question1", "question2"],
        "risk_manager": ["question1", "question2"],
        "ai_ethics_officer": ["question1", "question2"],
        "finance_director": ["question1", "question2"]
    }},
    "improvements": [
        {{"area": "what to improve", "suggestion": "specific recommendation"}}
    ],
    "strengths": ["what's good about this spec"]
}}"""
                }]
            )
            
            response_text = message.content[0].text
            
            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            review = json.loads(response_text)
            review["reviewed_at"] = datetime.now().isoformat()
            review["model"] = "claude-3-5-sonnet"
            review["agentic"] = True
            
            return review
            
        except Exception as e:
            print(f"Error calling API: {e}")
            return self._mock_review(spec_text)
    
    def _mock_review(self, spec_text: str) -> dict:
        """Fallback review when API not available."""
        return {
            "reviewed_at": datetime.now().isoformat(),
            "model": "mock",
            "agentic": False,
            "verdict": {
                "status": "NEEDS_WORK",
                "reasoning": "Using mock review. Set ANTHROPIC_API_KEY to use real LLM analysis."
            },
            "critical_issues": [
                {
                    "issue": "API key not configured",
                    "evidence": "No ANTHROPIC_API_KEY environment variable",
                    "impact": "Cannot perform intelligent review"
                }
            ],
            "questions_by_persona": {
                "skeptical_cto": ["How will this scale?"],
                "data_driven_ceo": ["What's the ROI?"],
                "user_advocate": ["Did you talk to users?"],
                "risk_manager": ["What could go wrong?"],
                "ai_ethics_officer": ["What about bias?"],
                "finance_director": ["What's the cost?"]
            },
            "improvements": [
                {
                    "area": "Setup",
                    "suggestion": "Set ANTHROPIC_API_KEY environment variable to enable intelligent review"
                }
            ],
            "strengths": ["You're trying the tool!"]
        }
    
    def ask_followup(self, spec_text: str, previous_review: dict, question: str) -> str:
        """Ask follow-up questions about the spec."""
        
        if not self.api_key:
            return "Set ANTHROPIC_API_KEY to enable follow-up questions."
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            context = f"""Original spec:
{spec_text}

Previous review summary:
Verdict: {previous_review['verdict']['status']}
Issues found: {len(previous_review.get('critical_issues', []))}"""
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"""{context}

Follow-up question: {question}

Provide a direct, specific answer based on the spec."""
                }]
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"Error: {e}"
    
    def suggest_improvements(self, spec_text: str, focus_area: str = None) -> dict:
        """Generate specific improvement suggestions."""
        
        if not self.api_key:
            return {"error": "Set ANTHROPIC_API_KEY to enable suggestions"}
        
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            focus = f" Focus on: {focus_area}" if focus_area else ""
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"""Review this spec and provide specific improvements:{focus}

{spec_text}

Provide concrete, actionable suggestions in JSON format:
{{
    "quick_wins": ["easy improvements that have high impact"],
    "must_haves": ["critical additions needed"],
    "nice_to_haves": ["optional enhancements"],
    "rewritten_sections": {{
        "section_name": "improved version of that section"
    }}
}}"""
                }]
            )
            
            response_text = message.content[0].text
            
            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            return {"error": str(e)}
    
    def format_review(self, review: dict) -> str:
        """Format review as readable text."""
        output = []
        output.append("=" * 70)
        output.append("🎭 AGENTIC AI PRODUCT REVIEW BOARD")
        output.append("Powered by Claude - Intelligent spec analysis with reasoning")
        output.append("=" * 70)
        output.append("")
        
        # Verdict
        verdict = review["verdict"]
        status_emoji = {
            "BLOCKED": "🚫",
            "NEEDS_WORK": "⚠️",
            "CONCERNS": "🤔",
            "APPROVED": "✅"
        }
        emoji = status_emoji.get(verdict["status"], "❓")
        
        output.append(f"VERDICT: {emoji} {verdict['status']}")
        output.append(f"Reasoning: {verdict['reasoning']}")
        output.append("")
        
        # Critical Issues
        if review.get("critical_issues"):
            output.append("🚨 CRITICAL ISSUES:")
            output.append("-" * 70)
            for issue in review["critical_issues"]:
                output.append(f"\n❌ {issue['issue']}")
                output.append(f"   Evidence: \"{issue['evidence']}\"")
                output.append(f"   Impact: {issue['impact']}")
        
        # Questions by Persona
        output.append("")
        output.append("💬 QUESTIONS FROM THE BOARD:")
        output.append("-" * 70)
        
        persona_names = {
            "skeptical_cto": "😤 Skeptical CTO",
            "data_driven_ceo": "📊 Data-Driven CEO",
            "user_advocate": "👥 User Advocate",
            "risk_manager": "🛡️ Risk Manager",
            "ai_ethics_officer": "🤖 AI Ethics Officer",
            "finance_director": "💰 Finance Director"
        }
        
        for persona_key, questions in review.get("questions_by_persona", {}).items():
            if questions:
                output.append(f"\n{persona_names.get(persona_key, persona_key)}")
                for q in questions:
                    output.append(f"  • {q}")
        
        # Improvements
        if review.get("improvements"):
            output.append("")
            output.append("💡 SUGGESTED IMPROVEMENTS:")
            output.append("-" * 70)
            for imp in review["improvements"]:
                output.append(f"\n📌 {imp['area']}")
                output.append(f"   {imp['suggestion']}")
        
        # Strengths
        if review.get("strengths"):
            output.append("")
            output.append("✨ STRENGTHS:")
            output.append("-" * 70)
            for strength in review["strengths"]:
                output.append(f"  ✓ {strength}")
        
        output.append("")
        output.append("=" * 70)
        output.append(f"Model: {review.get('model', 'unknown')}")
        output.append(f"Reviewed at: {review.get('reviewed_at', 'unknown')}")
        output.append("=" * 70)
        
        return "\n".join(output)

def main():
    """Demo the agentic review board."""
    
    board = AgenticReviewBoard()
    
    # Example spec
    spec = """
    New Feature: AI-Powered Content Generator
    
    We want to build an AI that automatically generates social media posts for users.
    It will analyze their past content and create new posts in their style.
    
    The AI will post automatically to save users time.
    
    This will improve engagement and make our platform better.
    
    Users will love it because it's innovative and uses AI.
    """
    
    print("📝 REVIEWING SPEC:")
    print("-" * 70)
    print(spec)
    print()
    
    # Review the spec
    print("🤖 Running agentic review with LLM reasoning...")
    print()
    
    review = board.review_spec(spec)
    
    # Print formatted review
    print(board.format_review(review))
    
    # Save as JSON
    with open("agentic_review_output.json", "w") as f:
        json.dump(review, f, indent=2)
    
    print("\n💾 Full review saved to: agentic_review_output.json")
    
    # Demo follow-up question
    if review.get("agentic"):
        print("\n" + "=" * 70)
        print("💬 FOLLOW-UP QUESTION DEMO:")
        print("-" * 70)
        
        followup = board.ask_followup(
            spec, 
            review, 
            "What specific metrics should we track for this feature?"
        )
        print(f"\nQ: What specific metrics should we track for this feature?")
        print(f"A: {followup}")

if __name__ == "__main__":
    main()
