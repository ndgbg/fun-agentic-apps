#!/usr/bin/env python3
"""
Open-Source LLM Evaluation Agent
Autonomous evaluation system that defines rubrics, scores outputs, and tracks quality over time.
"""

import os
import json
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
    
    async def generate_rubric(self, task_description: str, example_outputs: List[str] = None) -> Rubric:
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
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        # Extract JSON from response
        import re
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
    
    async def evaluate(self, rubric: Rubric, input_prompt: str, output_text: str, 
                      model_name: str, ground_truth: str = None) -> EvaluationResult:
        """Evaluate output against rubric with detailed reasoning."""
        
        import time
        start_time = time.time()
        
        scores = []
        hallucinations = []
        
        for criterion in rubric.criteria:
            score = await self._evaluate_dimension(
                criterion, input_prompt, output_text, ground_truth
            )
            scores.append(score)
            
            # Track hallucinations
            if criterion.dimension == EvaluationDimension.HALLUCINATION and score.score <= 2:
                hallucinations.extend(score.evidence)
        
        # Calculate overall score
        overall_score = sum(s.score * c.weight for s, c in zip(scores, rubric.criteria))
        
        # Determine pass/fail (threshold: 3.5/5.0)
        passed = overall_score >= 3.5
        
        result = EvaluationResult(
            id=f"eval_{datetime.now().timestamp()}",
            rubric_id=rubric.id,
            input_prompt=input_prompt,
            output_text=output_text,
            model_name=model_name,
            scores=scores,
            overall_score=overall_score,
            passed=passed,
            regression_detected=False,  # Set by RegressionDetector
            hallucinations=hallucinations,
            timestamp=datetime.now().isoformat(),
            evaluation_time=time.time() - start_time
        )
        
        return result
    
    async def _evaluate_dimension(self, criterion: EvaluationCriterion, 
                                  input_prompt: str, output_text: str,
                                  ground_truth: str = None) -> Score:
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
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        # Extract JSON
        import re
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
    
    def detect_regression(self, result: EvaluationResult, threshold: float = 0.5) -> bool:
        """Detect if current result is a regression from baseline."""
        
        if result.rubric_id not in self.baselines:
            # First evaluation, set baseline
            self.update_baseline(result.rubric_id, result.overall_score)
            return False
        
        baseline = self.baselines[result.rubric_id]
        regression = (baseline - result.overall_score) > threshold
        
        if not regression:
            # Update baseline with good result
            self.update_baseline(result.rubric_id, result.overall_score)
        
        return regression
    
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
    
    def __init__(self):
        self.hallucination_log = []
    
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
    """Main agent that orchestrates evaluation workflow."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.rubric_generator = RubricGenerator(self.api_key)
        self.evaluator = OutputEvaluator(self.api_key)
        self.regression_detector = RegressionDetector()
        self.hallucination_tracker = HallucinationTracker()
        self.rubrics = {}
    
    async def create_rubric(self, task_description: str, 
                           example_outputs: List[str] = None) -> Rubric:
        """Autonomously create evaluation rubric for a task."""
        
        print(f"🤖 Analyzing task and generating rubric...")
        rubric = await self.rubric_generator.generate_rubric(task_description, example_outputs)
        self.rubrics[rubric.id] = rubric
        
        print(f"✅ Created rubric: {rubric.name}")
        print(f"   Dimensions: {len(rubric.criteria)}")
        for c in rubric.criteria:
            print(f"   - {c.dimension.value} (weight: {c.weight})")
        
        return rubric
    
    async def evaluate_output(self, rubric_id: str, input_prompt: str, 
                             output_text: str, model_name: str,
                             ground_truth: str = None) -> EvaluationResult:
        """Evaluate an LLM output."""
        
        if rubric_id not in self.rubrics:
            raise ValueError(f"Rubric {rubric_id} not found")
        
        rubric = self.rubrics[rubric_id]
        
        print(f"\n📊 Evaluating output from {model_name}...")
        result = await self.evaluator.evaluate(
            rubric, input_prompt, output_text, model_name, ground_truth
        )
        
        # Detect regression
        result.regression_detected = self.regression_detector.detect_regression(result)
        self.regression_detector.add_to_history(result)
        
        # Track hallucinations
        self.hallucination_tracker.track(result)
        
        # Display results
        print(f"\n{'='*70}")
        print(f"EVALUATION RESULTS")
        print(f"{'='*70}")
        print(f"Overall Score: {result.overall_score:.2f}/5.0 {'✅ PASS' if result.passed else '❌ FAIL'}")
        print(f"Regression: {'⚠️  YES' if result.regression_detected else '✅ NO'}")
        print(f"Hallucinations: {len(result.hallucinations)}")
        print(f"\nDimension Scores:")
        
        for score in result.scores:
            print(f"\n  {score.dimension.value.upper()}: {score.score}/5")
            print(f"  Reasoning: {score.reasoning[:100]}...")
            if score.evidence:
                print(f"  Evidence: {score.evidence[0][:80]}...")
        
        return result
    
    async def run_evaluation_suite(self, rubric_id: str, 
                                   test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
        """Run multiple evaluations and aggregate results."""
        
        print(f"\n🚀 Running evaluation suite with {len(test_cases)} test cases...")
        
        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] Evaluating...")
            result = await self.evaluate_output(
                rubric_id,
                test_case["input"],
                test_case["output"],
                test_case.get("model", "unknown"),
                test_case.get("ground_truth")
            )
            results.append(result)
            await asyncio.sleep(0.5)  # Rate limiting
        
        # Aggregate results
        passed = sum(1 for r in results if r.passed)
        regressions = sum(1 for r in results if r.regression_detected)
        avg_score = sum(r.overall_score for r in results) / len(results)
        
        summary = {
            "total": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "pass_rate": passed / len(results),
            "regressions": regressions,
            "avg_score": avg_score,
            "results": results
        }
        
        print(f"\n{'='*70}")
        print(f"SUITE SUMMARY")
        print(f"{'='*70}")
        print(f"Total: {summary['total']}")
        print(f"Passed: {summary['passed']} ({summary['pass_rate']*100:.1f}%)")
        print(f"Failed: {summary['failed']}")
        print(f"Regressions: {summary['regressions']}")
        print(f"Average Score: {summary['avg_score']:.2f}/5.0")
        
        return summary
    
    def get_analytics(self, rubric_id: str = None) -> Dict[str, Any]:
        """Get analytics and trends."""
        
        analytics = {
            "timestamp": datetime.now().isoformat(),
            "total_evaluations": len(self.regression_detector.history),
            "rubrics": len(self.rubrics)
        }
        
        if rubric_id:
            analytics["trend"] = self.regression_detector.get_trend(rubric_id)
        
        analytics["hallucinations"] = self.hallucination_tracker.get_hallucination_rate()
        
        return analytics
    
    def save_state(self, filepath: str = "evaluation_state.json"):
        """Save agent state for persistence."""
        
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
        
        print(f"\n💾 State saved to {filepath}")

async def main():
    """Demo the evaluation agent."""
    
    print("🎯 OPEN-SOURCE LLM EVALUATION AGENT")
    print("="*70)
    
    agent = EvaluationAgent()
    
    # 1. Create rubric for Q&A task
    print("\n📋 STEP 1: Create Evaluation Rubric")
    print("-"*70)
    
    rubric = await agent.create_rubric(
        task_description="Answer questions about Python programming accurately and helpfully",
        example_outputs=[
            "To create a list in Python, use square brackets: my_list = [1, 2, 3]",
            "Python uses indentation to define code blocks, typically 4 spaces"
        ]
    )
    
    # 2. Evaluate some outputs
    print("\n\n📊 STEP 2: Evaluate LLM Outputs")
    print("-"*70)
    
    test_cases = [
        {
            "input": "How do I create a dictionary in Python?",
            "output": "To create a dictionary in Python, use curly braces with key-value pairs: my_dict = {'key': 'value', 'name': 'John'}. You can also use dict() constructor.",
            "model": "claude-3-5-sonnet",
            "ground_truth": "Use curly braces with key:value pairs"
        },
        {
            "input": "What is a list comprehension?",
            "output": "A list comprehension is a concise way to create lists. Syntax: [expression for item in iterable if condition]. Example: squares = [x**2 for x in range(10)]",
            "model": "claude-3-5-sonnet"
        },
        {
            "input": "How do I handle exceptions?",
            "output": "Python was invented in 1991 by Guido van Rossum. It's named after Monty Python.",
            "model": "claude-3-5-sonnet"
        }
    ]
    
    summary = await agent.run_evaluation_suite(rubric.id, test_cases)
    
    # 3. Check for regressions and hallucinations
    print("\n\n📈 STEP 3: Analytics & Trends")
    print("-"*70)
    
    analytics = agent.get_analytics(rubric.id)
    
    print(f"\nTrend Analysis:")
    trend = analytics["trend"]
    print(f"  Status: {trend['trend'].upper()}")
    print(f"  Recent Avg: {trend.get('recent_avg', 0):.2f}")
    print(f"  Baseline: {trend.get('baseline', 0):.2f}")
    
    print(f"\nHallucination Analysis:")
    hall = analytics["hallucinations"]
    print(f"  Rate: {hall['rate']:.2f} per evaluation")
    print(f"  Total Count: {hall['total_count']}")
    print(f"  Trend: {hall['trend'].upper()}")
    
    # 4. Save state
    agent.save_state()
    
    print("\n" + "="*70)
    print("✅ Evaluation complete!")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
