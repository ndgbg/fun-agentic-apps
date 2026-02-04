#!/usr/bin/env python3
"""
Example usage patterns for LLM Evaluation Agent
"""

import asyncio
from agent import EvaluationAgent, EvaluationDimension

# ============================================================================
# EXAMPLE 1: Basic Evaluation
# ============================================================================

async def example_basic_evaluation():
    """Simple evaluation of a single output."""
    
    print("="*70)
    print("EXAMPLE 1: Basic Evaluation")
    print("="*70)
    
    agent = EvaluationAgent()
    
    # Create rubric
    rubric = await agent.create_rubric(
        "Answer customer support questions helpfully and accurately"
    )
    
    # Evaluate output
    result = await agent.evaluate_output(
        rubric_id=rubric.id,
        input_prompt="How do I reset my password?",
        output_text="To reset your password, click 'Forgot Password' on the login page, enter your email, and follow the link sent to you.",
        model_name="claude-3-5-sonnet"
    )
    
    print(f"\nResult: {result.overall_score:.2f}/5.0")
    print(f"Status: {'✅ PASS' if result.passed else '❌ FAIL'}")

# ============================================================================
# EXAMPLE 2: Batch Evaluation with Ground Truth
# ============================================================================

async def example_batch_evaluation():
    """Evaluate multiple outputs with ground truth."""
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Batch Evaluation")
    print("="*70)
    
    agent = EvaluationAgent()
    
    # Create rubric for translation task
    rubric = await agent.create_rubric(
        "Translate English phrases to Spanish accurately",
        example_outputs=["Hello → Hola", "Thank you → Gracias"]
    )
    
    # Test cases with ground truth
    test_cases = [
        {
            "input": "Translate: Good morning",
            "output": "Buenos días",
            "model": "translator-v1",
            "ground_truth": "Buenos días"
        },
        {
            "input": "Translate: How are you?",
            "output": "¿Cómo estás?",
            "model": "translator-v1",
            "ground_truth": "¿Cómo estás?"
        },
        {
            "input": "Translate: See you later",
            "output": "Hasta luego",
            "model": "translator-v1",
            "ground_truth": "Hasta luego"
        }
    ]
    
    summary = await agent.run_evaluation_suite(rubric.id, test_cases)
    
    print(f"\nSummary:")
    print(f"  Pass Rate: {summary['pass_rate']*100:.1f}%")
    print(f"  Avg Score: {summary['avg_score']:.2f}/5.0")

# ============================================================================
# EXAMPLE 3: Regression Detection
# ============================================================================

async def example_regression_detection():
    """Demonstrate regression detection over time."""
    
    print("\n" + "="*70)
    print("EXAMPLE 3: Regression Detection")
    print("="*70)
    
    agent = EvaluationAgent()
    
    rubric = await agent.create_rubric(
        "Summarize news articles in 2-3 sentences"
    )
    
    # Simulate evaluations over time
    test_outputs = [
        ("Good summary", 4.5),
        ("Good summary", 4.6),
        ("Good summary", 4.4),
        ("Poor summary", 3.2),  # Regression!
        ("Good summary", 4.5)
    ]
    
    print("\nRunning evaluations...")
    for i, (output, expected_score) in enumerate(test_outputs, 1):
        result = await agent.evaluate_output(
            rubric_id=rubric.id,
            input_prompt="Summarize this article...",
            output_text=output,
            model_name="summarizer-v1"
        )
        
        status = "⚠️  REGRESSION" if result.regression_detected else "✅ OK"
        print(f"  Eval {i}: {result.overall_score:.2f}/5.0 - {status}")

# ============================================================================
# EXAMPLE 4: Hallucination Tracking
# ============================================================================

async def example_hallucination_tracking():
    """Track hallucinations across evaluations."""
    
    print("\n" + "="*70)
    print("EXAMPLE 4: Hallucination Tracking")
    print("="*70)
    
    agent = EvaluationAgent()
    
    rubric = await agent.create_rubric(
        "Answer factual questions about history"
    )
    
    # Test cases with varying hallucination levels
    test_cases = [
        {
            "input": "When was Python created?",
            "output": "Python was created in 1991 by Guido van Rossum.",
            "model": "qa-model"
        },
        {
            "input": "Who invented the telephone?",
            "output": "Alexander Graham Bell invented the telephone in 1876.",
            "model": "qa-model"
        },
        {
            "input": "When did World War II end?",
            "output": "World War II ended in 1950.",  # Wrong!
            "model": "qa-model"
        }
    ]
    
    await agent.run_evaluation_suite(rubric.id, test_cases)
    
    # Check hallucination stats
    analytics = agent.get_analytics()
    hall_stats = analytics["hallucinations"]
    
    print(f"\nHallucination Statistics:")
    print(f"  Total Count: {hall_stats['total_count']}")
    print(f"  Rate: {hall_stats['rate']:.2f} per evaluation")
    print(f"  Trend: {hall_stats['trend']}")

# ============================================================================
# EXAMPLE 5: Model Comparison
# ============================================================================

async def example_model_comparison():
    """Compare multiple models on same task."""
    
    print("\n" + "="*70)
    print("EXAMPLE 5: Model Comparison")
    print("="*70)
    
    agent = EvaluationAgent()
    
    rubric = await agent.create_rubric(
        "Write creative product descriptions"
    )
    
    # Same input, different models
    input_prompt = "Write a product description for wireless headphones"
    
    models_and_outputs = [
        ("model-a", "Premium wireless headphones with noise cancellation..."),
        ("model-b", "Experience crystal-clear audio with our headphones..."),
        ("model-c", "Headphones. They work. Buy them.")
    ]
    
    results = {}
    
    for model, output in models_and_outputs:
        result = await agent.evaluate_output(
            rubric_id=rubric.id,
            input_prompt=input_prompt,
            output_text=output,
            model_name=model
        )
        results[model] = result.overall_score
    
    print("\nModel Comparison:")
    for model, score in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"  {model}: {score:.2f}/5.0")

# ============================================================================
# EXAMPLE 6: Custom Rubric
# ============================================================================

async def example_custom_rubric():
    """Create and use a custom rubric."""
    
    print("\n" + "="*70)
    print("EXAMPLE 6: Custom Rubric")
    print("="*70)
    
    from agent import Rubric, EvaluationCriterion
    
    agent = EvaluationAgent()
    
    # Create custom rubric manually
    rubric = Rubric(
        id="custom_rubric_1",
        name="Code Review Rubric",
        task_type="code_review",
        criteria=[
            EvaluationCriterion(
                dimension=EvaluationDimension.ACCURACY,
                description="Correctness of code suggestions",
                weight=0.4,
                scoring_guide={
                    1: "Incorrect suggestions",
                    2: "Mostly incorrect",
                    3: "Partially correct",
                    4: "Mostly correct",
                    5: "Completely correct"
                }
            ),
            EvaluationCriterion(
                dimension=EvaluationDimension.COMPLETENESS,
                description="Coverage of all issues",
                weight=0.3,
                scoring_guide={
                    1: "Misses critical issues",
                    2: "Incomplete coverage",
                    3: "Covers main issues",
                    4: "Comprehensive",
                    5: "Exhaustive"
                }
            ),
            EvaluationCriterion(
                dimension=EvaluationDimension.COHERENCE,
                description="Clear explanations",
                weight=0.3,
                scoring_guide={
                    1: "Confusing",
                    2: "Unclear",
                    3: "Understandable",
                    4: "Clear",
                    5: "Crystal clear"
                }
            )
        ],
        created_at="2026-02-03T16:00:00"
    )
    
    agent.rubrics[rubric.id] = rubric
    
    # Use custom rubric
    result = await agent.evaluate_output(
        rubric_id=rubric.id,
        input_prompt="Review this Python code...",
        output_text="The code looks good but consider using list comprehension...",
        model_name="code-reviewer"
    )
    
    print(f"\nCustom Rubric Result: {result.overall_score:.2f}/5.0")

# ============================================================================
# EXAMPLE 7: Trend Analysis
# ============================================================================

async def example_trend_analysis():
    """Analyze quality trends over time."""
    
    print("\n" + "="*70)
    print("EXAMPLE 7: Trend Analysis")
    print("="*70)
    
    agent = EvaluationAgent()
    
    rubric = await agent.create_rubric(
        "Generate marketing copy"
    )
    
    # Simulate evaluations over time
    for i in range(10):
        result = await agent.evaluate_output(
            rubric_id=rubric.id,
            input_prompt="Write marketing copy for a new app",
            output_text=f"Sample marketing copy version {i}",
            model_name="copywriter-v1"
        )
    
    # Get trend analysis
    analytics = agent.get_analytics(rubric.id)
    trend = analytics["trend"]
    
    print(f"\nTrend Analysis:")
    print(f"  Status: {trend['trend'].upper()}")
    print(f"  Recent Avg: {trend.get('recent_avg', 0):.2f}")
    print(f"  Baseline: {trend.get('baseline', 0):.2f}")
    print(f"  Scores: {[f'{s:.1f}' for s in trend.get('scores', [])]}")

# ============================================================================
# EXAMPLE 8: CI/CD Integration
# ============================================================================

async def example_cicd_integration():
    """Example CI/CD quality gate."""
    
    print("\n" + "="*70)
    print("EXAMPLE 8: CI/CD Integration")
    print("="*70)
    
    agent = EvaluationAgent()
    
    rubric = await agent.create_rubric(
        "Generate API documentation"
    )
    
    # Load test cases (simulated)
    test_cases = [
        {
            "input": "Document the /users endpoint",
            "output": "GET /users - Returns list of users...",
            "model": "doc-generator-v2"
        },
        {
            "input": "Document the /posts endpoint",
            "output": "POST /posts - Creates a new post...",
            "model": "doc-generator-v2"
        }
    ]
    
    summary = await agent.run_evaluation_suite(rubric.id, test_cases)
    
    # Quality gates
    PASS_RATE_THRESHOLD = 0.9
    REGRESSION_THRESHOLD = 0
    
    print(f"\nQuality Gates:")
    print(f"  Pass Rate: {summary['pass_rate']*100:.1f}% (threshold: {PASS_RATE_THRESHOLD*100:.0f}%)")
    print(f"  Regressions: {summary['regressions']} (threshold: {REGRESSION_THRESHOLD})")
    
    if summary['pass_rate'] >= PASS_RATE_THRESHOLD and summary['regressions'] <= REGRESSION_THRESHOLD:
        print("\n✅ All quality gates passed - Deploy approved")
        return 0
    else:
        print("\n❌ Quality gates failed - Deploy blocked")
        return 1

# ============================================================================
# EXAMPLE 9: Dimension-Specific Analysis
# ============================================================================

async def example_dimension_analysis():
    """Analyze specific evaluation dimensions."""
    
    print("\n" + "="*70)
    print("EXAMPLE 9: Dimension-Specific Analysis")
    print("="*70)
    
    agent = EvaluationAgent()
    
    rubric = await agent.create_rubric(
        "Answer technical questions"
    )
    
    # Run evaluations
    for i in range(5):
        await agent.evaluate_output(
            rubric_id=rubric.id,
            input_prompt="Explain how async/await works",
            output_text=f"Async/await explanation version {i}",
            model_name="tech-qa"
        )
    
    # Analyze specific dimension
    trend = agent.regression_detector.get_trend(
        rubric.id,
        dimension=EvaluationDimension.ACCURACY,
        last_n=5
    )
    
    print(f"\nAccuracy Dimension Analysis:")
    print(f"  Trend: {trend['trend']}")
    print(f"  Scores: {trend['scores']}")

# ============================================================================
# EXAMPLE 10: Save and Load State
# ============================================================================

async def example_state_persistence():
    """Demonstrate state persistence."""
    
    print("\n" + "="*70)
    print("EXAMPLE 10: State Persistence")
    print("="*70)
    
    # Create agent and run evaluations
    agent = EvaluationAgent()
    
    rubric = await agent.create_rubric("Test task")
    
    await agent.evaluate_output(
        rubric_id=rubric.id,
        input_prompt="Test input",
        output_text="Test output",
        model_name="test-model"
    )
    
    # Save state
    agent.save_state("test_state.json")
    print("\n✅ State saved to test_state.json")
    
    # Load state (in new session)
    print("📂 State can be loaded in new session")
    print("   Contains: rubrics, baselines, history, hallucination log")

# ============================================================================
# Main
# ============================================================================

async def main():
    """Run all examples."""
    
    print("\n" + "="*70)
    print("LLM EVALUATION AGENT - USAGE EXAMPLES")
    print("="*70)
    print("\nNote: Set ANTHROPIC_API_KEY to run with real evaluations")
    print("      Examples will show structure without API key")
    print()
    
    # Run examples (comment out to run specific ones)
    # await example_basic_evaluation()
    # await example_batch_evaluation()
    # await example_regression_detection()
    # await example_hallucination_tracking()
    # await example_model_comparison()
    # await example_custom_rubric()
    # await example_trend_analysis()
    # await example_cicd_integration()
    # await example_dimension_analysis()
    # await example_state_persistence()
    
    print("\n" + "="*70)
    print("Examples complete!")
    print("Uncomment specific examples in main() to run them")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
