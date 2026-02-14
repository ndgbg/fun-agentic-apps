#!/usr/bin/env python3
"""
Open-Source LLM Evaluation Agent
Autonomous evaluation system that defines rubrics, scores outputs, and tracks quality over time.
Uses Anthropic's tool_use API for truly agentic behavior - the LLM autonomously decides
what to evaluate and how to adapt its strategy based on findings.
"""

import os
import re
import json
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import anthropic


class EvaluationDimension(Enum):
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    COHERENCE = "coherence"
    COMPLETENESS = "completeness"
    SAFETY = "safety"
    HALLUCINATION = "hallucination"
    BIAS = "bias"
    INSTRUCTION_FOLLOWING = "instruction_following"


@dataclass
class EvaluationCriterion:
    dimension: EvaluationDimension
    description: str
    weight: float
    scoring_guide: Dict[int, str]  # 1-5 scale with descriptions


@dataclass
class Rubric:
    id: str
    name: str
    task_type: str
    criteria: List[EvaluationCriterion]
    created_at: str
    created_by: str = "agent"


@dataclass
class Score:
    dimension: EvaluationDimension
    score: int  # 1-5
    reasoning: str
    evidence: List[str]
    confidence: float


@dataclass
class EvaluationResult:
    id: str
    rubric_id: str
    input_prompt: str
    output_text: str
    model_name: str
    scores: List[Score]
    overall_score: float
    passed: bool
    regression_detected: bool
    hallucinations: List[str]
    timestamp: str
    evaluation_time: float


class RubricGenerator:
    """Autonomously generates evaluation rubrics based on task analysis."""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_rubric(self, task_description: str, example_outputs: List[str] = None) -> Rubric:
        """Analyze task and generate appropriate evaluation rubric."""

        prompt = f"""Analyze this task and create a comprehensive evaluation rubric.

Task: {task_description}

{f"Example outputs: {example_outputs[:2]}" if example_outputs else ""}

Create a rubric with 4-6 evaluation dimensions. For each dimension:
1. Choose from: accuracy, relevance, coherence, completeness, safety, hallucination, bias, instruction_following
2. Provide clear description
3. Assign weight (0.0-1.0, must sum to 1.0)
4. Define 5-point scoring guide

Return JSON:
{{
  "name": "Rubric name",
  "task_type": "classification|generation|qa|summarization|reasoning",
  "criteria": [
    {{
      "dimension": "accuracy",
      "description": "How factually correct is the output",
      "weight": 0.3,
      "scoring_guide": {{
        "1": "Completely inaccurate",
        "2": "Mostly inaccurate",
        "3": "Partially accurate",
        "4": "Mostly accurate",
        "5": "Completely accurate"
      }}
    }}
  ]
}}"""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            rubric_data = json.loads(json_match.group())
        else:
            rubric_data = json.loads(response_text)

        # Convert to Rubric object
        criteria = [
            EvaluationCriterion(
                dimension=EvaluationDimension(c["dimension"]),
                description=c["description"],
                weight=c["weight"],
                scoring_guide={int(k): v for k, v in c["scoring_guide"].items()}
            )
            for c in rubric_data["criteria"]
        ]

        rubric = Rubric(
            id=f"rubric_{datetime.now().timestamp()}",
            name=rubric_data["name"],
            task_type=rubric_data["task_type"],
            criteria=criteria,
            created_at=datetime.now().isoformat()
        )

        return rubric


class OutputEvaluator:
    """Autonomously evaluates LLM outputs against rubrics."""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def evaluate_dimension(self, criterion: EvaluationCriterion, input_prompt: str,
                           output_text: str, ground_truth: str = None) -> Score:
        """Evaluate single dimension with reasoning."""

        scoring_guide_str = "\n".join([f"{k}: {v}" for k, v in criterion.scoring_guide.items()])

        prompt = f"""Evaluate this LLM output on the dimension: {criterion.dimension.value}

Dimension: {criterion.dimension.value}
Description: {criterion.description}

Scoring Guide:
{scoring_guide_str}

Input Prompt: {input_prompt}

Output to Evaluate: {output_text}

{f"Ground Truth: {ground_truth}" if ground_truth else ""}

Provide:
1. Score (1-5)
2. Detailed reasoning
3. Specific evidence (quotes from output)
4. Confidence (0.0-1.0)

Return JSON:
{{
  "score": 4,
  "reasoning": "The output is mostly accurate because...",
  "evidence": ["quote 1", "quote 2"],
  "confidence": 0.85
}}"""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # Extract JSON
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            score_data = json.loads(json_match.group())
        else:
            score_data = json.loads(response_text)

        return Score(
            dimension=criterion.dimension,
            score=score_data["score"],
            reasoning=score_data["reasoning"],
            evidence=score_data.get("evidence", []),
            confidence=score_data.get("confidence", 0.8)
        )


class RegressionDetector:
    """Detects quality regressions by comparing against historical baselines."""

    def __init__(self):
        self.baselines = {}  # rubric_id -> baseline_score
        self.history = []  # List of all evaluations

    def update_baseline(self, rubric_id: str, score: float):
        """Update baseline score for a rubric."""
        if rubric_id not in self.baselines:
            self.baselines[rubric_id] = score
        else:
            # Moving average
            self.baselines[rubric_id] = 0.7 * self.baselines[rubric_id] + 0.3 * score

    def detect_regression(self, rubric_id: str, overall_score: float, threshold: float = 0.5) -> Dict[str, Any]:
        """Detect if current score is a regression from baseline."""

        if rubric_id not in self.baselines:
            # First evaluation, set baseline
            self.update_baseline(rubric_id, overall_score)
            return {
                "regression_detected": False,
                "baseline": overall_score,
                "current_score": overall_score,
                "message": "First evaluation for this rubric. Baseline established."
            }

        baseline = self.baselines[rubric_id]
        regression = (baseline - overall_score) > threshold

        if not regression:
            # Update baseline with good result
            self.update_baseline(rubric_id, overall_score)

        return {
            "regression_detected": regression,
            "baseline": baseline,
            "current_score": overall_score,
            "delta": overall_score - baseline,
            "message": f"Regression detected! Score dropped {baseline - overall_score:.2f} from baseline."
            if regression else "No regression detected."
        }

    def add_to_history(self, result: EvaluationResult):
        """Track evaluation in history."""
        self.history.append(result)

    def get_trend(self, rubric_id: str, dimension: EvaluationDimension = None,
                  last_n: int = 10) -> Dict[str, Any]:
        """Analyze trend for a rubric/dimension."""

        relevant = [r for r in self.history[-last_n:] if r.rubric_id == rubric_id]

        if not relevant:
            return {"trend": "no_data", "scores": []}

        if dimension:
            scores = [
                next((s.score for s in r.scores if s.dimension == dimension), None)
                for r in relevant
            ]
            scores = [s for s in scores if s is not None]
        else:
            scores = [r.overall_score for r in relevant]

        if len(scores) < 2:
            return {"trend": "insufficient_data", "scores": scores}

        # Simple trend detection
        recent_avg = sum(scores[-3:]) / len(scores[-3:])
        older_avg = sum(scores[:-3]) / len(scores[:-3]) if len(scores) > 3 else scores[0]

        if recent_avg > older_avg + 0.3:
            trend = "improving"
        elif recent_avg < older_avg - 0.3:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "scores": scores,
            "recent_avg": recent_avg,
            "older_avg": older_avg,
            "baseline": self.baselines.get(rubric_id)
        }


class HallucinationTracker:
    """Tracks and analyzes hallucinations over time."""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.hallucination_log = []

    def detect_hallucinations(self, input_prompt: str, output_text: str,
                              ground_truth: str = None) -> Dict[str, Any]:
        """Detect hallucinations in an LLM output."""

        prompt = f"""Analyze the following LLM output for hallucinations (fabricated, unsupported, or false information).

Input Prompt: {input_prompt}

LLM Output: {output_text}

{f"Ground Truth: {ground_truth}" if ground_truth else ""}

Identify any hallucinations: statements that are fabricated, not supported by the input, or factually incorrect.

Return JSON:
{{
  "hallucinations_found": true,
  "count": 2,
  "hallucinations": [
    {{
      "text": "the hallucinated statement",
      "reason": "why this is a hallucination",
      "severity": "high|medium|low"
    }}
  ],
  "overall_assessment": "Brief summary of hallucination analysis"
}}"""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1500,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = json.loads(response_text)

        return result

    def track(self, result: EvaluationResult):
        """Track hallucinations from evaluation result."""

        if result.hallucinations:
            self.hallucination_log.append({
                "timestamp": result.timestamp,
                "model": result.model_name,
                "count": len(result.hallucinations),
                "examples": result.hallucinations,
                "overall_score": result.overall_score
            })

    def get_hallucination_rate(self, model_name: str = None,
                               time_window: int = 10) -> Dict[str, Any]:
        """Calculate hallucination rate over time."""

        recent = self.hallucination_log[-time_window:]

        if model_name:
            recent = [h for h in recent if h["model"] == model_name]

        if not recent:
            return {"rate": 0.0, "total_count": 0, "examples": []}

        total_count = sum(h["count"] for h in recent)
        avg_per_eval = total_count / len(recent)

        # Get most common hallucination patterns
        all_examples = []
        for h in recent:
            all_examples.extend(h["examples"])

        return {
            "rate": avg_per_eval,
            "total_count": total_count,
            "evaluations": len(recent),
            "examples": all_examples[:5],  # Top 5
            "trend": "increasing" if len(recent) > 1 and recent[-1]["count"] > recent[0]["count"] else "stable"
        }


class EvaluationAgent:
    """Main agent that orchestrates evaluation workflow using Anthropic's tool_use API.

    The LLM autonomously decides how to evaluate: generating rubrics, evaluating specific
    dimensions, checking for regressions, analyzing trends, and tracking hallucinations,
    adapting its strategy based on findings.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.rubric_generator = RubricGenerator(self.api_key)
        self.evaluator = OutputEvaluator(self.api_key)
        self.regression_detector = RegressionDetector()
        self.hallucination_tracker = HallucinationTracker(self.api_key)
        self.rubrics = {}
        self.last_evaluation_result = None

        self.system_prompt = (
            "You are an LLM evaluation agent. You autonomously evaluate LLM outputs for quality, "
            "detect regressions, and track hallucinations. You have tools to generate rubrics, "
            "evaluate individual dimensions, check regressions, detect hallucinations, and analyze "
            "trends. When evaluating, first check if a suitable rubric exists. Evaluate each "
            "dimension separately so you can identify specific weaknesses. After evaluating, "
            "always check for regression and hallucinations. Report findings comprehensively."
        )

    def _get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return Anthropic tool schemas for all available evaluation tools."""
        return [
            {
                "name": "generate_rubric",
                "description": (
                    "Create an evaluation rubric for a given task. The rubric defines dimensions "
                    "(accuracy, relevance, coherence, etc.), weights, and scoring guides. "
                    "Use this when no suitable rubric exists for the task being evaluated."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_description": {
                            "type": "string",
                            "description": "Description of the task to create a rubric for"
                        },
                        "example_outputs": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional example outputs to help calibrate the rubric"
                        }
                    },
                    "required": ["task_description"]
                }
            },
            {
                "name": "evaluate_dimension",
                "description": (
                    "Evaluate an LLM output on a single dimension from a rubric. Returns a score "
                    "(1-5), reasoning, evidence, and confidence. Call this once per dimension to "
                    "get granular scores."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "rubric_id": {
                            "type": "string",
                            "description": "ID of the rubric to evaluate against"
                        },
                        "dimension": {
                            "type": "string",
                            "description": "The dimension to evaluate (e.g., accuracy, relevance, coherence)",
                            "enum": [d.value for d in EvaluationDimension]
                        },
                        "input_prompt": {
                            "type": "string",
                            "description": "The original input prompt given to the LLM"
                        },
                        "output_text": {
                            "type": "string",
                            "description": "The LLM output text to evaluate"
                        },
                        "ground_truth": {
                            "type": "string",
                            "description": "Optional ground truth to compare against"
                        }
                    },
                    "required": ["rubric_id", "dimension", "input_prompt", "output_text"]
                }
            },
            {
                "name": "check_regression",
                "description": (
                    "Check if an overall score represents a regression from the historical "
                    "baseline for a rubric. Returns whether regression was detected and the "
                    "delta from baseline."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "rubric_id": {
                            "type": "string",
                            "description": "ID of the rubric to check regression for"
                        },
                        "overall_score": {
                            "type": "number",
                            "description": "The overall weighted score to check against baseline"
                        }
                    },
                    "required": ["rubric_id", "overall_score"]
                }
            },
            {
                "name": "detect_hallucinations",
                "description": (
                    "Analyze an LLM output for hallucinations - fabricated, unsupported, or "
                    "false information. Returns a list of identified hallucinations with "
                    "severity ratings."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "input_prompt": {
                            "type": "string",
                            "description": "The original input prompt"
                        },
                        "output_text": {
                            "type": "string",
                            "description": "The LLM output to check for hallucinations"
                        },
                        "ground_truth": {
                            "type": "string",
                            "description": "Optional ground truth to check against"
                        }
                    },
                    "required": ["input_prompt", "output_text"]
                }
            },
            {
                "name": "get_trend",
                "description": (
                    "Get the scoring trend for a rubric, optionally filtered by dimension. "
                    "Shows whether scores are improving, declining, or stable over recent evaluations."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "rubric_id": {
                            "type": "string",
                            "description": "ID of the rubric to get trends for"
                        },
                        "dimension": {
                            "type": "string",
                            "description": "Optional specific dimension to track",
                            "enum": [d.value for d in EvaluationDimension]
                        },
                        "last_n": {
                            "type": "integer",
                            "description": "Number of recent evaluations to consider (default 10)"
                        }
                    },
                    "required": ["rubric_id"]
                }
            },
            {
                "name": "get_hallucination_rate",
                "description": (
                    "Get hallucination statistics including rate per evaluation, total count, "
                    "and trend over a window of recent evaluations."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "model_name": {
                            "type": "string",
                            "description": "Optional model name to filter statistics for"
                        },
                        "window": {
                            "type": "integer",
                            "description": "Number of recent evaluations to consider (default 10)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "list_rubrics",
                "description": (
                    "List all available rubrics with their IDs, names, task types, and "
                    "dimensions. Use this to check if a suitable rubric already exists "
                    "before generating a new one."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "save_state",
                "description": (
                    "Persist the current agent state (rubrics, baselines, history, hallucination "
                    "log) to disk as JSON. Call this after completing evaluations to preserve results."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    def _execute_tool(self, name: str, tool_input: Dict[str, Any]) -> Any:
        """Dispatch tool calls to existing components and return results."""

        if name == "generate_rubric":
            rubric = self.rubric_generator.generate_rubric(
                task_description=tool_input["task_description"],
                example_outputs=tool_input.get("example_outputs")
            )
            self.rubrics[rubric.id] = rubric
            return {
                "rubric_id": rubric.id,
                "name": rubric.name,
                "task_type": rubric.task_type,
                "dimensions": [
                    {
                        "dimension": c.dimension.value,
                        "description": c.description,
                        "weight": c.weight
                    }
                    for c in rubric.criteria
                ],
                "created_at": rubric.created_at
            }

        elif name == "evaluate_dimension":
            rubric_id = tool_input["rubric_id"]
            if rubric_id not in self.rubrics:
                return {"error": f"Rubric '{rubric_id}' not found. Use list_rubrics to see available rubrics."}

            rubric = self.rubrics[rubric_id]
            dimension_value = tool_input["dimension"]

            # Find the matching criterion in the rubric
            criterion = None
            for c in rubric.criteria:
                if c.dimension.value == dimension_value:
                    criterion = c
                    break

            if criterion is None:
                available = [c.dimension.value for c in rubric.criteria]
                return {
                    "error": f"Dimension '{dimension_value}' not found in rubric '{rubric_id}'. "
                             f"Available dimensions: {available}"
                }

            score = self.evaluator.evaluate_dimension(
                criterion=criterion,
                input_prompt=tool_input["input_prompt"],
                output_text=tool_input["output_text"],
                ground_truth=tool_input.get("ground_truth")
            )

            return {
                "dimension": score.dimension.value,
                "score": score.score,
                "reasoning": score.reasoning,
                "evidence": score.evidence,
                "confidence": score.confidence,
                "weight": criterion.weight
            }

        elif name == "check_regression":
            result = self.regression_detector.detect_regression(
                rubric_id=tool_input["rubric_id"],
                overall_score=tool_input["overall_score"]
            )
            return result

        elif name == "detect_hallucinations":
            result = self.hallucination_tracker.detect_hallucinations(
                input_prompt=tool_input["input_prompt"],
                output_text=tool_input["output_text"],
                ground_truth=tool_input.get("ground_truth")
            )
            return result

        elif name == "get_trend":
            dimension = None
            if "dimension" in tool_input and tool_input["dimension"]:
                dimension = EvaluationDimension(tool_input["dimension"])
            result = self.regression_detector.get_trend(
                rubric_id=tool_input["rubric_id"],
                dimension=dimension,
                last_n=tool_input.get("last_n", 10)
            )
            return result

        elif name == "get_hallucination_rate":
            result = self.hallucination_tracker.get_hallucination_rate(
                model_name=tool_input.get("model_name"),
                time_window=tool_input.get("window", 10)
            )
            return result

        elif name == "list_rubrics":
            if not self.rubrics:
                return {"rubrics": [], "message": "No rubrics available. Use generate_rubric to create one."}
            rubric_list = []
            for rid, r in self.rubrics.items():
                rubric_list.append({
                    "id": r.id,
                    "name": r.name,
                    "task_type": r.task_type,
                    "dimensions": [c.dimension.value for c in r.criteria],
                    "created_at": r.created_at
                })
            return {"rubrics": rubric_list}

        elif name == "save_state":
            filepath = "evaluation_state.json"
            state = {
                "rubrics": {
                    rid: {
                        "id": r.id,
                        "name": r.name,
                        "task_type": r.task_type,
                        "criteria": [
                            {
                                "dimension": c.dimension.value,
                                "description": c.description,
                                "weight": c.weight,
                                "scoring_guide": c.scoring_guide
                            }
                            for c in r.criteria
                        ],
                        "created_at": r.created_at
                    }
                    for rid, r in self.rubrics.items()
                },
                "baselines": self.regression_detector.baselines,
                "history": [
                    {
                        "id": r.id,
                        "rubric_id": r.rubric_id,
                        "model_name": r.model_name,
                        "overall_score": r.overall_score,
                        "passed": r.passed,
                        "regression_detected": r.regression_detected,
                        "hallucinations": r.hallucinations,
                        "timestamp": r.timestamp
                    }
                    for r in self.regression_detector.history
                ],
                "hallucination_log": self.hallucination_tracker.hallucination_log
            }

            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)

            return {"saved": True, "filepath": filepath, "rubrics_count": len(self.rubrics),
                    "history_count": len(self.regression_detector.history)}

        else:
            return {"error": f"Unknown tool: {name}"}

    async def run(self, request: str, max_iterations: int = 20) -> str:
        """Run the agentic loop: the LLM autonomously decides which tools to call and when to stop.

        Args:
            request: The user's evaluation request in natural language.
            max_iterations: Maximum number of LLM round-trips to prevent runaway loops.

        Returns:
            The final text response from the agent summarizing its findings.
        """
        messages = [{"role": "user", "content": request}]

        for i in range(max_iterations):
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=self.system_prompt,
                tools=self._get_tool_definitions(),
                messages=messages
            )

            # Append the assistant's response to the conversation
            messages.append({"role": "assistant", "content": response.content})

            # If the model is done (no more tool calls), extract final text and return
            if response.stop_reason == "end_turn":
                final_text = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_text += block.text
                return final_text

            # Process tool calls
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"  [Tool Call] {block.name}({json.dumps(block.input, default=str)[:120]}...)")
                        try:
                            result = self._execute_tool(block.name, block.input)
                        except Exception as e:
                            result = {"error": str(e)}
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, default=str)
                        })
                messages.append({"role": "user", "content": tool_results})

        # If we exhausted iterations, return what we have
        return "Evaluation reached maximum iterations. Partial results may be available in the tool call history."

    async def evaluate_output(self, rubric_id: str, input_prompt: str,
                              output_text: str, model_name: str,
                              ground_truth: str = None) -> str:
        """Evaluate an LLM output by delegating to the agentic loop."""

        ground_truth_clause = f'\nGround Truth: {ground_truth}' if ground_truth else ''

        request = (
            f"Evaluate the following LLM output. Use rubric '{rubric_id}' which already exists.\n\n"
            f"Model: {model_name}\n"
            f"Input Prompt: {input_prompt}\n"
            f"LLM Output: {output_text}"
            f"{ground_truth_clause}\n\n"
            f"Evaluate each dimension in the rubric separately. Then check for regression and "
            f"hallucinations. Provide a comprehensive report with scores, reasoning, and any "
            f"issues found."
        )

        return await self.run(request)

    async def run_evaluation_suite(self, rubric_id: str,
                                   test_cases: List[Dict[str, str]]) -> List[str]:
        """Run multiple evaluations by calling self.run() for each test case."""

        print(f"\nRunning evaluation suite with {len(test_cases)} test cases...")

        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*70}")
            print(f"[{i}/{len(test_cases)}] Evaluating test case...")
            print(f"{'='*70}")

            result = await self.evaluate_output(
                rubric_id=rubric_id,
                input_prompt=test_case["input"],
                output_text=test_case["output"],
                model_name=test_case.get("model", "unknown"),
                ground_truth=test_case.get("ground_truth")
            )
            results.append(result)
            print(f"\n{result}")

        return results


async def main():
    """Demo the agentic evaluation agent."""

    print("LLM EVALUATION AGENT (Agentic)")
    print("=" * 70)

    agent = EvaluationAgent()

    # Step 1: Let the agent autonomously create a rubric
    print("\nSTEP 1: Generate Evaluation Rubric")
    print("-" * 70)

    rubric_request = (
        "I need to evaluate LLM outputs for a Python programming Q&A task. "
        "The model should answer questions about Python accurately and helpfully. "
        "Please generate a suitable evaluation rubric. "
        "Here are example outputs for calibration:\n"
        "- 'To create a list in Python, use square brackets: my_list = [1, 2, 3]'\n"
        "- 'Python uses indentation to define code blocks, typically 4 spaces'"
    )

    rubric_response = await agent.run(rubric_request)
    print(f"\n{rubric_response}")

    # Retrieve the generated rubric ID
    if not agent.rubrics:
        print("No rubric was generated. Exiting.")
        return

    rubric_id = list(agent.rubrics.keys())[0]
    print(f"\nUsing rubric: {rubric_id}")

    # Step 2: Evaluate LLM outputs
    print(f"\n\nSTEP 2: Evaluate LLM Outputs")
    print("-" * 70)

    test_cases = [
        {
            "input": "How do I create a dictionary in Python?",
            "output": (
                "To create a dictionary in Python, use curly braces with key-value pairs: "
                "my_dict = {'key': 'value', 'name': 'John'}. You can also use dict() constructor."
            ),
            "model": "claude-sonnet-4-5",
            "ground_truth": "Use curly braces with key:value pairs"
        },
        {
            "input": "What is a list comprehension?",
            "output": (
                "A list comprehension is a concise way to create lists. "
                "Syntax: [expression for item in iterable if condition]. "
                "Example: squares = [x**2 for x in range(10)]"
            ),
            "model": "claude-sonnet-4-5"
        },
        {
            "input": "How do I handle exceptions?",
            "output": (
                "Python was invented in 1991 by Guido van Rossum. "
                "It's named after Monty Python."
            ),
            "model": "claude-sonnet-4-5"
        }
    ]

    results = await agent.run_evaluation_suite(rubric_id, test_cases)

    # Step 3: Ask the agent for trend analysis and save state
    print(f"\n\nSTEP 3: Analytics, Trends & Save State")
    print("-" * 70)

    analytics_request = (
        f"Provide a comprehensive analytics summary. Check the scoring trend for rubric "
        f"'{rubric_id}', get the hallucination rate, and then save the state to disk. "
        f"Summarize all findings."
    )

    analytics_response = await agent.run(analytics_request)
    print(f"\n{analytics_response}")

    print("\n" + "=" * 70)
    print("Evaluation complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
