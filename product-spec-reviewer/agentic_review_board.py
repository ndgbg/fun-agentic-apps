#!/usr/bin/env python3
"""
Agentic AI Product Review Board
Uses Anthropic's tool_use API to iteratively review product specs with
multiple personas, gap analysis, scoring, probing questions, and synthesis.
"""

import os
import json
from datetime import datetime


class AgenticReviewBoard:
    def __init__(self, api_key=None):
        self.name = "Agentic AI Product Review Board"
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = "claude-sonnet-4-5-20250929"

        self.system_prompt = (
            "You are an expert product review board. You have tools to review specs "
            "from different personas (CTO, CEO, User Advocate, Risk Manager, Ethics "
            "Officer, Finance Director), identify gaps, score sections, ask probing "
            "questions, and suggest improvements. Conduct a thorough review: start by "
            "reviewing from the most critical personas, investigate gaps you find, "
            "score key sections, and synthesize a final verdict. Be thorough - don't "
            "just do one pass."
        )

        self.personas = {
            "skeptical_cto": {
                "title": "Skeptical CTO",
                "focus": (
                    "Technical feasibility, scalability, architecture, "
                    "engineering effort, technical debt, and system design"
                ),
            },
            "data_driven_ceo": {
                "title": "Data-Driven CEO",
                "focus": (
                    "Business metrics, ROI, market positioning, competitive "
                    "advantage, strategic alignment, and growth potential"
                ),
            },
            "user_advocate": {
                "title": "User Advocate",
                "focus": (
                    "User experience, accessibility, user research validation, "
                    "pain points addressed, onboarding flow, and usability"
                ),
            },
            "risk_manager": {
                "title": "Risk Manager",
                "focus": (
                    "Safety, compliance, operational risks, disaster recovery, "
                    "security vulnerabilities, and regulatory concerns"
                ),
            },
            "ai_ethics_officer": {
                "title": "AI Ethics Officer",
                "focus": (
                    "Bias and fairness, transparency, consent, data privacy, "
                    "responsible AI practices, and societal impact"
                ),
            },
            "finance_director": {
                "title": "Finance Director",
                "focus": (
                    "Cost analysis, revenue impact, resource allocation, "
                    "budget requirements, unit economics, and financial risk"
                ),
            },
        }

    def _get_tool_definitions(self):
        """Return Anthropic tool schemas for the review board tools."""
        return [
            {
                "name": "review_as_persona",
                "description": (
                    "Review the product spec from a specific persona's viewpoint. "
                    "Each persona brings a unique perspective: skeptical_cto focuses "
                    "on technical feasibility, data_driven_ceo on business metrics, "
                    "user_advocate on UX, risk_manager on risks, ai_ethics_officer "
                    "on ethics, finance_director on costs."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "persona": {
                            "type": "string",
                            "enum": [
                                "skeptical_cto",
                                "data_driven_ceo",
                                "user_advocate",
                                "risk_manager",
                                "ai_ethics_officer",
                                "finance_director",
                            ],
                            "description": "The persona to review as.",
                        },
                        "focus_area": {
                            "type": "string",
                            "description": (
                                "Specific area to focus on within this persona's "
                                "domain (e.g., 'scalability' for CTO, 'onboarding' "
                                "for User Advocate)."
                            ),
                        },
                    },
                    "required": ["persona", "focus_area"],
                },
            },
            {
                "name": "identify_gaps",
                "description": (
                    "Identify missing sections, unclear areas, or information gaps "
                    "in the spec. Use this to find what the spec fails to address."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "section_name": {
                            "type": "string",
                            "description": (
                                "The section or topic to analyze for gaps "
                                "(e.g., 'security', 'user research', 'metrics', "
                                "'technical architecture')."
                            ),
                        },
                    },
                    "required": ["section_name"],
                },
            },
            {
                "name": "score_section",
                "description": (
                    "Score a specific section of the spec on a scale of 1-10 based "
                    "on given criteria. Provides a numeric score with justification."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "section_name": {
                            "type": "string",
                            "description": "The section to score.",
                        },
                        "criteria": {
                            "type": "string",
                            "description": (
                                "The criteria to score against (e.g., 'clarity', "
                                "'completeness', 'technical depth', 'feasibility')."
                            ),
                        },
                    },
                    "required": ["section_name", "criteria"],
                },
            },
            {
                "name": "ask_probing_question",
                "description": (
                    "Generate a probing question about a specific aspect of the "
                    "spec that exposes weaknesses, assumptions, or missing details."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "aspect": {
                            "type": "string",
                            "description": (
                                "The aspect to probe (e.g., 'user consent', "
                                "'data retention', 'failure modes')."
                            ),
                        },
                        "context": {
                            "type": "string",
                            "description": (
                                "Additional context about why this aspect needs "
                                "probing."
                            ),
                        },
                    },
                    "required": ["aspect", "context"],
                },
            },
            {
                "name": "suggest_improvement",
                "description": (
                    "Suggest a specific, actionable improvement for an identified "
                    "issue in the spec."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "issue": {
                            "type": "string",
                            "description": "The issue that needs improvement.",
                        },
                        "section": {
                            "type": "string",
                            "description": (
                                "The section of the spec where this improvement "
                                "applies."
                            ),
                        },
                    },
                    "required": ["issue", "section"],
                },
            },
            {
                "name": "synthesize_verdict",
                "description": (
                    "Combine all findings from persona reviews, gap analysis, "
                    "scores, and questions into a final structured verdict. Call "
                    "this after completing your thorough review."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "findings_summary": {
                            "type": "string",
                            "description": (
                                "A comprehensive summary of all findings gathered "
                                "during the review process."
                            ),
                        },
                    },
                    "required": ["findings_summary"],
                },
            },
        ]

    def _execute_tool(self, name, tool_input, spec_text):
        """Execute a tool by making a focused LLM call for the specific subtask."""
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)

        if name == "review_as_persona":
            return self._tool_review_as_persona(
                client, spec_text, tool_input["persona"], tool_input["focus_area"]
            )
        elif name == "identify_gaps":
            return self._tool_identify_gaps(
                client, spec_text, tool_input["section_name"]
            )
        elif name == "score_section":
            return self._tool_score_section(
                client, spec_text, tool_input["section_name"], tool_input["criteria"]
            )
        elif name == "ask_probing_question":
            return self._tool_ask_probing_question(
                client, spec_text, tool_input["aspect"], tool_input["context"]
            )
        elif name == "suggest_improvement":
            return self._tool_suggest_improvement(
                client, spec_text, tool_input["issue"], tool_input["section"]
            )
        elif name == "synthesize_verdict":
            return self._tool_synthesize_verdict(
                client, spec_text, tool_input["findings_summary"]
            )
        else:
            return {"error": f"Unknown tool: {name}"}

    def _tool_review_as_persona(self, client, spec_text, persona, focus_area):
        """Review spec from a specific persona's viewpoint via focused LLM call."""
        persona_info = self.personas.get(persona, {})
        title = persona_info.get("title", persona)
        focus = persona_info.get("focus", "general review")

        message = client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are the {title} on a product review board. "
                        f"Your domain of expertise: {focus}\n\n"
                        f"Review the following product specification, focusing "
                        f"specifically on: {focus_area}\n\n"
                        f"PRODUCT SPEC:\n{spec_text}\n\n"
                        f"Provide your review as JSON with these fields:\n"
                        f'{{"persona": "{persona}", '
                        f'"focus_area": "{focus_area}", '
                        f'"concerns": ["list of specific concerns with evidence"], '
                        f'"questions": ["pointed questions that expose gaps"], '
                        f'"risk_level": "low|medium|high|critical", '
                        f'"summary": "brief assessment from this persona\'s viewpoint"}}'
                    ),
                }
            ],
        )

        return self._parse_json_response(message.content[0].text)

    def _tool_identify_gaps(self, client, spec_text, section_name):
        """Identify missing sections or unclear areas via focused LLM call."""
        message = client.messages.create(
            model=self.model,
            max_tokens=1200,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are a meticulous spec reviewer. Analyze the following "
                        f"product specification for gaps and missing information in "
                        f"the area of: {section_name}\n\n"
                        f"PRODUCT SPEC:\n{spec_text}\n\n"
                        f"Identify what is missing, unclear, or insufficiently "
                        f"detailed. Respond as JSON:\n"
                        f'{{"section": "{section_name}", '
                        f'"missing_elements": ["specific things that should be '
                        f'included but are not"], '
                        f'"unclear_areas": ["areas that are mentioned but lack '
                        f'sufficient detail"], '
                        f'"severity": "minor|moderate|major|critical", '
                        f'"recommendation": "what the spec author should add"}}'
                    ),
                }
            ],
        )

        return self._parse_json_response(message.content[0].text)

    def _tool_score_section(self, client, spec_text, section_name, criteria):
        """Score a specific section on a 1-10 scale via focused LLM call."""
        message = client.messages.create(
            model=self.model,
            max_tokens=800,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are a product spec quality assessor. Score the "
                        f"following product specification's treatment of "
                        f'"{section_name}" based on the criteria: {criteria}\n\n'
                        f"PRODUCT SPEC:\n{spec_text}\n\n"
                        f"Score on a scale of 1-10 where 1 is completely "
                        f"inadequate and 10 is exemplary. Respond as JSON:\n"
                        f'{{"section": "{section_name}", '
                        f'"criteria": "{criteria}", '
                        f'"score": <number 1-10>, '
                        f'"justification": "why this score", '
                        f'"what_would_make_it_a_10": "specific improvements '
                        f'needed for a perfect score"}}'
                    ),
                }
            ],
        )

        return self._parse_json_response(message.content[0].text)

    def _tool_ask_probing_question(self, client, spec_text, aspect, context):
        """Generate probing questions about a specific aspect via focused LLM call."""
        message = client.messages.create(
            model=self.model,
            max_tokens=800,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are a senior product reviewer known for asking "
                        f"incisive questions that expose hidden assumptions and "
                        f"gaps.\n\n"
                        f"PRODUCT SPEC:\n{spec_text}\n\n"
                        f"Aspect to probe: {aspect}\n"
                        f"Context: {context}\n\n"
                        f"Generate probing questions that the spec author must "
                        f"answer. Respond as JSON:\n"
                        f'{{"aspect": "{aspect}", '
                        f'"probing_questions": ["list of 2-3 sharp questions"], '
                        f'"why_this_matters": "why these questions are critical", '
                        f'"potential_risks_if_unanswered": "what could go wrong '
                        f'if these are not addressed"}}'
                    ),
                }
            ],
        )

        return self._parse_json_response(message.content[0].text)

    def _tool_suggest_improvement(self, client, spec_text, issue, section):
        """Suggest a specific improvement for an identified issue."""
        message = client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are a senior product consultant who provides "
                        f"actionable, specific improvement suggestions.\n\n"
                        f"PRODUCT SPEC:\n{spec_text}\n\n"
                        f"Issue identified: {issue}\n"
                        f"Section affected: {section}\n\n"
                        f"Provide a concrete improvement suggestion. Respond "
                        f"as JSON:\n"
                        f'{{"issue": "{issue}", '
                        f'"section": "{section}", '
                        f'"suggestion": "specific actionable recommendation", '
                        f'"example_text": "example of what improved spec '
                        f'language might look like", '
                        f'"priority": "low|medium|high|critical", '
                        f'"effort": "small|medium|large"}}'
                    ),
                }
            ],
        )

        return self._parse_json_response(message.content[0].text)

    def _tool_synthesize_verdict(self, client, spec_text, findings_summary):
        """Synthesize all findings into a final structured verdict."""
        message = client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are the chairperson of a product review board. "
                        f"Based on all the findings from multiple reviewers, "
                        f"synthesize a final verdict.\n\n"
                        f"PRODUCT SPEC:\n{spec_text}\n\n"
                        f"FINDINGS FROM REVIEW:\n{findings_summary}\n\n"
                        f"Provide the final synthesized verdict as JSON:\n"
                        f'{{"verdict": {{"status": "BLOCKED|NEEDS_WORK|CONCERNS'
                        f'|APPROVED", "reasoning": "comprehensive reasoning"}}, '
                        f'"critical_issues": [{{"issue": "description", '
                        f'"evidence": "quote or reference from spec", '
                        f'"impact": "what breaks or goes wrong"}}], '
                        f'"questions_by_persona": {{"skeptical_cto": '
                        f'["top questions"], "data_driven_ceo": ["top questions"], '
                        f'"user_advocate": ["top questions"], "risk_manager": '
                        f'["top questions"], "ai_ethics_officer": '
                        f'["top questions"], "finance_director": '
                        f'["top questions"]}}, '
                        f'"improvements": [{{"area": "what to improve", '
                        f'"suggestion": "specific recommendation"}}], '
                        f'"strengths": ["what the spec does well"], '
                        f'"section_scores": {{"section_name": '
                        f'{{"score": 0, "criteria": "what was scored"}}}}, '
                        f'"overall_score": 0}}'
                    ),
                }
            ],
        )

        return self._parse_json_response(message.content[0].text)

    def _parse_json_response(self, text):
        """Parse JSON from an LLM response, handling markdown code fences."""
        try:
            if "```json" in text:
                json_start = text.find("```json") + 7
                json_end = text.find("```", json_start)
                text = text[json_start:json_end].strip()
            elif "```" in text:
                json_start = text.find("```") + 3
                json_end = text.find("```", json_start)
                text = text[json_start:json_end].strip()
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw_response": text}

    def review_spec(self, spec_text, max_iterations=25):
        """
        Review a spec using the agentic tool-use loop.

        The LLM orchestrates the review by calling tools iteratively:
        reviewing from different personas, identifying gaps, scoring sections,
        asking probing questions, suggesting improvements, and synthesizing
        a final verdict.
        """
        if not self.api_key:
            return self._mock_review(spec_text)

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            messages = [
                {
                    "role": "user",
                    "content": (
                        f"Review this product specification thoroughly:\n\n"
                        f"{spec_text}"
                    ),
                }
            ]

            all_tool_results = []

            for i in range(max_iterations):
                response = client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    system=self.system_prompt,
                    tools=self._get_tool_definitions(),
                    messages=messages,
                )

                messages.append({"role": "assistant", "content": response.content})

                if response.stop_reason == "end_turn":
                    break

                if response.stop_reason == "tool_use":
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            print(
                                f"  [Iteration {i + 1}] Calling tool: "
                                f"{block.name}({json.dumps(block.input, default=str)[:100]}...)"
                            )
                            result = self._execute_tool(
                                block.name, block.input, spec_text
                            )
                            all_tool_results.append(
                                {
                                    "tool": block.name,
                                    "input": block.input,
                                    "result": result,
                                }
                            )
                            tool_results.append(
                                {
                                    "type": "tool_result",
                                    "tool_use_id": block.id,
                                    "content": json.dumps(result, default=str),
                                }
                            )
                    messages.append({"role": "user", "content": tool_results})

            # Extract the final text response from the last assistant message
            final_text = ""
            for msg in reversed(messages):
                if msg["role"] == "assistant":
                    content = msg["content"]
                    if isinstance(content, list):
                        for block in content:
                            if hasattr(block, "text"):
                                final_text = block.text
                                break
                    elif isinstance(content, str):
                        final_text = content
                    if final_text:
                        break

            # Try to parse the final text as a structured review
            review = self._parse_json_response(final_text)

            # If the synthesize_verdict tool was called, use its result
            # as the primary review structure
            verdict_results = [
                r for r in all_tool_results if r["tool"] == "synthesize_verdict"
            ]
            if verdict_results:
                last_verdict = verdict_results[-1]["result"]
                if isinstance(last_verdict, dict) and "verdict" in last_verdict:
                    review = last_verdict

            # Ensure required fields exist
            if "verdict" not in review:
                review["verdict"] = {
                    "status": "NEEDS_WORK",
                    "reasoning": final_text[:500] if final_text else "Review completed.",
                }
            if "critical_issues" not in review:
                review["critical_issues"] = []
            if "questions_by_persona" not in review:
                review["questions_by_persona"] = {}
            if "improvements" not in review:
                review["improvements"] = []
            if "strengths" not in review:
                review["strengths"] = []

            review["reviewed_at"] = datetime.now().isoformat()
            review["model"] = self.model
            review["agentic"] = True
            review["iterations"] = min(i + 1, max_iterations)
            review["tools_called"] = [
                {"tool": r["tool"], "input": r["input"]} for r in all_tool_results
            ]

            return review

        except Exception as e:
            print(f"Error during agentic review: {e}")
            return self._mock_review(spec_text)

    def _mock_review(self, spec_text):
        """Fallback review when API key is not available."""
        return {
            "reviewed_at": datetime.now().isoformat(),
            "model": "mock",
            "agentic": False,
            "verdict": {
                "status": "NEEDS_WORK",
                "reasoning": (
                    "Using mock review. Set ANTHROPIC_API_KEY to use real "
                    "LLM analysis."
                ),
            },
            "critical_issues": [
                {
                    "issue": "API key not configured",
                    "evidence": "No ANTHROPIC_API_KEY environment variable",
                    "impact": "Cannot perform intelligent review",
                }
            ],
            "questions_by_persona": {
                "skeptical_cto": ["How will this scale?"],
                "data_driven_ceo": ["What's the ROI?"],
                "user_advocate": ["Did you talk to users?"],
                "risk_manager": ["What could go wrong?"],
                "ai_ethics_officer": ["What about bias?"],
                "finance_director": ["What's the cost?"],
            },
            "improvements": [
                {
                    "area": "Setup",
                    "suggestion": (
                        "Set ANTHROPIC_API_KEY environment variable to enable "
                        "intelligent review"
                    ),
                }
            ],
            "strengths": ["You're trying the tool!"],
        }

    def format_review(self, review):
        """Format review as readable text."""
        output = []
        output.append("=" * 70)
        output.append("AGENTIC AI PRODUCT REVIEW BOARD")
        output.append(
            "Powered by Claude - Iterative spec analysis with tool use"
        )
        output.append("=" * 70)
        output.append("")

        # Agentic metadata
        if review.get("agentic"):
            output.append(
                f"Review iterations: {review.get('iterations', 'N/A')}"
            )
            tools_called = review.get("tools_called", [])
            if tools_called:
                tool_names = [t["tool"] for t in tools_called]
                tool_counts = {}
                for t in tool_names:
                    tool_counts[t] = tool_counts.get(t, 0) + 1
                summary = ", ".join(
                    f"{name}: {count}" for name, count in tool_counts.items()
                )
                output.append(f"Tools used: {summary}")
            output.append("")

        # Verdict
        verdict = review.get("verdict", {})
        status_indicators = {
            "BLOCKED": "[BLOCKED]",
            "NEEDS_WORK": "[NEEDS WORK]",
            "CONCERNS": "[CONCERNS]",
            "APPROVED": "[APPROVED]",
        }
        indicator = status_indicators.get(verdict.get("status", ""), "[?]")

        output.append(f"VERDICT: {indicator} {verdict.get('status', 'UNKNOWN')}")
        output.append(f"Reasoning: {verdict.get('reasoning', 'N/A')}")
        output.append("")

        # Section scores
        if review.get("section_scores"):
            output.append("SECTION SCORES:")
            output.append("-" * 70)
            for section, score_info in review["section_scores"].items():
                if isinstance(score_info, dict):
                    score = score_info.get("score", "N/A")
                    criteria = score_info.get("criteria", "")
                    output.append(f"  {section}: {score}/10 ({criteria})")
                else:
                    output.append(f"  {section}: {score_info}/10")
            if review.get("overall_score"):
                output.append(f"\n  Overall: {review['overall_score']}/10")
            output.append("")

        # Critical Issues
        if review.get("critical_issues"):
            output.append("CRITICAL ISSUES:")
            output.append("-" * 70)
            for issue in review["critical_issues"]:
                if isinstance(issue, dict):
                    output.append(f"\n  [X] {issue.get('issue', 'N/A')}")
                    if issue.get("evidence"):
                        output.append(
                            f"      Evidence: \"{issue['evidence']}\""
                        )
                    if issue.get("impact"):
                        output.append(f"      Impact: {issue['impact']}")
                else:
                    output.append(f"\n  [X] {issue}")
            output.append("")

        # Questions by Persona
        if review.get("questions_by_persona"):
            output.append("QUESTIONS FROM THE BOARD:")
            output.append("-" * 70)

            persona_labels = {
                "skeptical_cto": "Skeptical CTO",
                "data_driven_ceo": "Data-Driven CEO",
                "user_advocate": "User Advocate",
                "risk_manager": "Risk Manager",
                "ai_ethics_officer": "AI Ethics Officer",
                "finance_director": "Finance Director",
            }

            for persona_key, questions in review[
                "questions_by_persona"
            ].items():
                if questions:
                    label = persona_labels.get(persona_key, persona_key)
                    output.append(f"\n  {label}:")
                    for q in questions:
                        output.append(f"    - {q}")
            output.append("")

        # Improvements
        if review.get("improvements"):
            output.append("SUGGESTED IMPROVEMENTS:")
            output.append("-" * 70)
            for imp in review["improvements"]:
                if isinstance(imp, dict):
                    output.append(f"\n  >> {imp.get('area', 'General')}")
                    output.append(
                        f"     {imp.get('suggestion', 'N/A')}"
                    )
                else:
                    output.append(f"\n  >> {imp}")
            output.append("")

        # Strengths
        if review.get("strengths"):
            output.append("STRENGTHS:")
            output.append("-" * 70)
            for strength in review["strengths"]:
                output.append(f"  + {strength}")
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

    print("REVIEWING SPEC:")
    print("-" * 70)
    print(spec)
    print()

    # Review the spec using agentic loop
    print("Running agentic review with iterative tool use...")
    print("The agent will call multiple tools to build a thorough review.\n")

    review = board.review_spec(spec)

    # Print formatted review
    print()
    print(board.format_review(review))

    # Save as JSON
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "agentic_review_output.json",
    )
    with open(output_path, "w") as f:
        json.dump(review, f, indent=2)

    print(f"\nFull review saved to: {output_path}")


if __name__ == "__main__":
    main()
