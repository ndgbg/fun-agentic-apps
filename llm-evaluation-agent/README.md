# 🎯 Open-Source LLM Evaluation Agent

Eval-as-a-service, but local. Autonomous evaluation system that creates rubrics, scores outputs, detects regressions, and tracks hallucinations over time.

## What It Does

- **Define evaluation rubrics** - Agent analyzes your task and generates appropriate rubrics
- **Run agent workflows** - Autonomous evaluation with detailed reasoning
- **Score outputs** - Multi-dimensional scoring with evidence
- **Catch regressions** - Automatic baseline tracking and regression detection
- **Track hallucinations over time** - Continuous monitoring with trend analysis

## Why It's Agentic

This isn't just a scoring script. The agent:

- **Autonomously creates rubrics** - Analyzes task requirements and generates evaluation criteria
- **Reasons about quality** - Provides detailed explanations for each score
- **Adapts baselines** - Learns from evaluation history to detect regressions
- **Identifies patterns** - Tracks hallucination trends and quality degradation
- **Makes decisions** - Determines pass/fail and flags concerning patterns
- **Provides evidence** - Quotes specific examples to support scores

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run evaluation
python agent.py
```

## Core Components

### 1. Rubric Generator

Autonomously creates evaluation rubrics by analyzing tasks:

```python
agent = EvaluationAgent()

rubric = await agent.create_rubric(
    task_description="Answer Python programming questions",
    example_outputs=["example1", "example2"]
)
```

**Generated rubric includes:**
- 4-6 evaluation dimensions (accuracy, relevance, coherence, etc.)
- Weighted criteria (sum to 1.0)
- 5-point scoring guides with clear descriptions
- Task-specific adaptations

### 2. Output Evaluator

Evaluates LLM outputs with detailed reasoning:

```python
result = await agent.evaluate_output(
    rubric_id=rubric.id,
    input_prompt="How do I create a list in Python?",
    output_text="Use square brackets: my_list = [1, 2, 3]",
    model_name="claude-3-5-sonnet",
    ground_truth="Use square brackets"  # optional
)
```

**Each evaluation provides:**
- Score per dimension (1-5)
- Detailed reasoning
- Specific evidence (quotes from output)
- Confidence level (0.0-1.0)
- Overall weighted score
- Pass/fail determination

### 3. Regression Detector

Automatically detects quality regressions:

```python
# Tracks baseline scores
# Detects when scores drop significantly
# Updates baselines with good results
# Provides trend analysis
```

**Features:**
- Moving average baselines
- Configurable regression threshold
- Historical trend analysis
- Per-rubric tracking

### 4. Hallucination Tracker

Monitors hallucinations over time:

```python
analytics = agent.get_analytics()
hallucination_rate = analytics["hallucinations"]["rate"]
trend = analytics["hallucinations"]["trend"]
```

**Tracks:**
- Total hallucination count
- Rate per evaluation
- Trend (increasing/stable/decreasing)
- Specific examples
- Per-model statistics

## Evaluation Dimensions

| Dimension | Description | Use Case |
|-----------|-------------|----------|
| Accuracy | Factual correctness | Q&A, information retrieval |
| Relevance | On-topic responses | Search, recommendations |
| Coherence | Logical flow | Long-form content |
| Completeness | Covers all aspects | Summaries, explanations |
| Safety | No harmful content | User-facing apps |
| Hallucination | No false information | Critical applications |
| Bias | Fair and balanced | Decision support |
| Instruction Following | Follows format/rules | Structured outputs |

## Example Workflow

```python
from agent import EvaluationAgent

agent = EvaluationAgent()

# 1. Create rubric
rubric = await agent.create_rubric(
    "Summarize news articles in 2-3 sentences"
)

# 2. Evaluate outputs
test_cases = [
    {
        "input": "Article text...",
        "output": "Summary...",
        "model": "claude-3-5-sonnet"
    }
]

summary = await agent.run_evaluation_suite(rubric.id, test_cases)

# 3. Check analytics
analytics = agent.get_analytics(rubric.id)
print(f"Pass rate: {summary['pass_rate']}")
print(f"Regressions: {summary['regressions']}")
print(f"Hallucination rate: {analytics['hallucinations']['rate']}")

# 4. Save state
agent.save_state("evaluation_state.json")
```

## Dashboard

Visual monitoring interface:

```bash
open dashboard.html
```

**Features:**
- Real-time metrics
- Quality trend charts
- Dimension breakdowns
- Recent evaluations
- Hallucination tracking
- Export reports

## Evaluation Results

Each evaluation returns:

```python
EvaluationResult(
    overall_score=4.2,           # Weighted average
    passed=True,                 # >= 3.5 threshold
    regression_detected=False,   # Compared to baseline
    hallucinations=[...],        # Detected issues
    scores=[
        Score(
            dimension="accuracy",
            score=4,
            reasoning="The output correctly explains...",
            evidence=["quote from output"],
            confidence=0.85
        )
    ]
)
```

## Regression Detection

Automatic baseline tracking:

```
First evaluation: Sets baseline (4.2)
Second evaluation: 4.5 → Updates baseline (4.3)
Third evaluation: 3.5 → Regression detected! (drop > 0.5)
Fourth evaluation: 4.4 → No regression, updates baseline
```

**Configuration:**
```python
regression_detected = detector.detect_regression(
    result,
    threshold=0.5  # Minimum drop to flag
)
```

## Hallucination Tracking

Continuous monitoring:

```python
{
    "rate": 0.2,              # Per evaluation
    "total_count": 3,         # Across all evals
    "trend": "stable",        # increasing/stable/decreasing
    "examples": [
        "Claimed Python was invented in 1985",
        "Stated lists are immutable"
    ]
}
```

## Analytics

Comprehensive trend analysis:

```python
analytics = agent.get_analytics(rubric_id)

# Overall stats
analytics["total_evaluations"]  # 15
analytics["rubrics"]            # 3

# Quality trend
analytics["trend"]["status"]     # improving/stable/declining
analytics["trend"]["recent_avg"] # 4.3
analytics["trend"]["baseline"]   # 4.1

# Hallucinations
analytics["hallucinations"]["rate"]  # 0.2
analytics["hallucinations"]["trend"] # stable
```

## State Persistence

Save and load evaluation history:

```python
# Save
agent.save_state("evaluation_state.json")

# State includes:
# - All rubrics
# - Baselines
# - Evaluation history
# - Hallucination log
```

## Use Cases

### Model Comparison
```python
# Evaluate same inputs across models
for model in ["claude-3-5-sonnet", "gpt-4", "llama-3"]:
    result = await agent.evaluate_output(
        rubric_id, prompt, output, model
    )
```

### CI/CD Integration
```python
# Run evaluation suite in CI
summary = await agent.run_evaluation_suite(rubric_id, test_cases)
if summary["pass_rate"] < 0.9:
    raise Exception("Quality threshold not met")
```

### Continuous Monitoring
```python
# Track production outputs
while True:
    output = get_production_output()
    result = await agent.evaluate_output(...)
    
    if result.regression_detected:
        alert_team()
```

### A/B Testing
```python
# Compare prompt variations
results_a = await evaluate_prompt_a()
results_b = await evaluate_prompt_b()

if results_b["avg_score"] > results_a["avg_score"]:
    deploy_prompt_b()
```

## Advanced Features

### Custom Rubrics

```python
from agent import Rubric, EvaluationCriterion, EvaluationDimension

rubric = Rubric(
    id="custom_1",
    name="Custom Rubric",
    task_type="generation",
    criteria=[
        EvaluationCriterion(
            dimension=EvaluationDimension.ACCURACY,
            description="Factual correctness",
            weight=0.4,
            scoring_guide={
                1: "Completely wrong",
                2: "Mostly wrong",
                3: "Partially correct",
                4: "Mostly correct",
                5: "Completely correct"
            }
        )
    ]
)
```

### Batch Evaluation

```python
# Evaluate multiple outputs efficiently
results = []
for test_case in test_cases:
    result = await agent.evaluate_output(...)
    results.append(result)
    await asyncio.sleep(0.5)  # Rate limiting
```

### Trend Analysis

```python
# Analyze quality over time
trend = agent.regression_detector.get_trend(
    rubric_id,
    dimension=EvaluationDimension.HALLUCINATION,
    last_n=20
)

print(f"Trend: {trend['trend']}")
print(f"Recent avg: {trend['recent_avg']}")
print(f"Scores: {trend['scores']}")
```

## Architecture

```
EvaluationAgent
├── RubricGenerator
│   └── Analyzes tasks → Generates rubrics
├── OutputEvaluator
│   └── Scores outputs → Provides reasoning
├── RegressionDetector
│   └── Tracks baselines → Detects drops
└── HallucinationTracker
    └── Monitors issues → Analyzes trends
```

## Technical Details

**Models**: Claude 3.5 Sonnet (for evaluation)  
**Scoring**: 1-5 scale with weighted dimensions  
**Threshold**: 3.5/5.0 for pass/fail  
**Regression**: 0.5 point drop from baseline  
**Storage**: JSON state files  

## Best Practices

1. **Start with generated rubrics** - Let the agent analyze your task
2. **Provide ground truth** - When available, for more accurate evaluation
3. **Monitor trends** - Don't just look at individual scores
4. **Set appropriate thresholds** - Adjust based on your quality requirements
5. **Track hallucinations** - Critical for production systems
6. **Save state regularly** - Preserve evaluation history

## Limitations

- Requires API key (uses Claude for evaluation)
- Evaluation speed depends on API rate limits
- Subjective dimensions may vary
- Best for English language outputs

## Future Enhancements

The architecture supports:
- Multi-model evaluation (use different models as evaluators)
- Custom dimension definitions
- Automated retraining triggers
- Integration with monitoring systems
- Comparative analysis across models

## License

MIT

---

Built with Claude 3.5 Sonnet. Part of the [Fun Agentic Apps](https://github.com/ndgbg/fun-agentic-apps) collection.
