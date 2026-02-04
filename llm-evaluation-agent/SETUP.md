# Setup Guide

## Prerequisites

- Python 3.8+
- Anthropic API key
- Modern web browser (for dashboard)

## Installation

```bash
# Clone repository
git clone https://github.com/ndgbg/fun-agentic-apps.git
cd fun-agentic-apps/llm-evaluation-agent

# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=your_key_here
```

## Quick Start

### 1. Run Basic Evaluation

```bash
python agent.py
```

This will:
1. Generate a rubric for Python Q&A
2. Evaluate 3 test outputs
3. Detect regressions
4. Track hallucinations
5. Save state to `evaluation_state.json`

### 2. View Dashboard

```bash
open dashboard.html
# or
python -m http.server 8000
# then visit http://localhost:8000/dashboard.html
```

## Usage Examples

### Create Custom Rubric

```python
from agent import EvaluationAgent

agent = EvaluationAgent()

# Agent analyzes task and generates rubric
rubric = await agent.create_rubric(
    task_description="Translate English to Spanish accurately",
    example_outputs=[
        "Hello → Hola",
        "Good morning → Buenos días"
    ]
)

print(f"Created rubric: {rubric.name}")
print(f"Dimensions: {[c.dimension.value for c in rubric.criteria]}")
```

### Evaluate Single Output

```python
result = await agent.evaluate_output(
    rubric_id=rubric.id,
    input_prompt="Translate: How are you?",
    output_text="¿Cómo estás?",
    model_name="claude-3-5-sonnet",
    ground_truth="¿Cómo estás?"  # Optional
)

print(f"Score: {result.overall_score}/5.0")
print(f"Passed: {result.passed}")
print(f"Regression: {result.regression_detected}")

for score in result.scores:
    print(f"{score.dimension.value}: {score.score}/5")
    print(f"  Reasoning: {score.reasoning}")
```

### Run Evaluation Suite

```python
test_cases = [
    {
        "input": "Translate: Good morning",
        "output": "Buenos días",
        "model": "claude-3-5-sonnet",
        "ground_truth": "Buenos días"
    },
    {
        "input": "Translate: Thank you",
        "output": "Gracias",
        "model": "claude-3-5-sonnet"
    }
]

summary = await agent.run_evaluation_suite(rubric.id, test_cases)

print(f"Pass rate: {summary['pass_rate']*100:.1f}%")
print(f"Average score: {summary['avg_score']:.2f}")
print(f"Regressions: {summary['regressions']}")
```

### Check Analytics

```python
analytics = agent.get_analytics(rubric.id)

# Quality trend
trend = analytics["trend"]
print(f"Trend: {trend['trend']}")
print(f"Recent avg: {trend['recent_avg']:.2f}")
print(f"Baseline: {trend['baseline']:.2f}")

# Hallucinations
hall = analytics["hallucinations"]
print(f"Hallucination rate: {hall['rate']:.2f}")
print(f"Trend: {hall['trend']}")
print(f"Examples: {hall['examples']}")
```

### Save and Load State

```python
# Save state
agent.save_state("my_evaluations.json")

# Load state (in new session)
agent = EvaluationAgent()
# State is automatically loaded from evaluation_state.json
# Or manually load:
import json
with open("my_evaluations.json") as f:
    state = json.load(f)
```

## Configuration

### Evaluation Thresholds

```python
# Pass/fail threshold (default: 3.5/5.0)
result.passed = result.overall_score >= 3.5

# Regression threshold (default: 0.5 point drop)
regression = detector.detect_regression(result, threshold=0.5)
```

### Rubric Weights

```python
# Adjust dimension weights (must sum to 1.0)
criteria = [
    EvaluationCriterion(
        dimension=EvaluationDimension.ACCURACY,
        weight=0.5  # 50% of overall score
    ),
    EvaluationCriterion(
        dimension=EvaluationDimension.RELEVANCE,
        weight=0.3  # 30%
    ),
    EvaluationCriterion(
        dimension=EvaluationDimension.COHERENCE,
        weight=0.2  # 20%
    )
]
```

### Model Selection

```python
# Use different model for evaluation
evaluator = OutputEvaluator(api_key)
# Currently uses claude-3-5-sonnet
# Can be modified in agent.py
```

## Integration Examples

### CI/CD Pipeline

```python
#!/usr/bin/env python3
"""
CI/CD evaluation script
"""
import asyncio
from agent import EvaluationAgent

async def ci_evaluation():
    agent = EvaluationAgent()
    
    # Load test cases
    test_cases = load_test_cases("tests/eval_cases.json")
    
    # Run evaluation
    summary = await agent.run_evaluation_suite(
        rubric_id="prod_rubric",
        test_cases=test_cases
    )
    
    # Check thresholds
    if summary["pass_rate"] < 0.9:
        print("❌ Quality threshold not met")
        exit(1)
    
    if summary["regressions"] > 0:
        print("⚠️  Regressions detected")
        exit(1)
    
    print("✅ All checks passed")
    exit(0)

if __name__ == "__main__":
    asyncio.run(ci_evaluation())
```

### Production Monitoring

```python
#!/usr/bin/env python3
"""
Monitor production outputs
"""
import asyncio
from agent import EvaluationAgent

async def monitor():
    agent = EvaluationAgent()
    
    while True:
        # Get recent production outputs
        outputs = fetch_production_outputs()
        
        for output in outputs:
            result = await agent.evaluate_output(
                rubric_id="prod_rubric",
                input_prompt=output["prompt"],
                output_text=output["response"],
                model_name=output["model"]
            )
            
            # Alert on issues
            if result.regression_detected:
                send_alert(f"Regression detected: {result.overall_score}")
            
            if len(result.hallucinations) > 0:
                send_alert(f"Hallucinations: {result.hallucinations}")
        
        await asyncio.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    asyncio.run(monitor())
```

### Model Comparison

```python
#!/usr/bin/env python3
"""
Compare multiple models
"""
import asyncio
from agent import EvaluationAgent

async def compare_models():
    agent = EvaluationAgent()
    
    models = ["claude-3-5-sonnet", "gpt-4", "llama-3"]
    test_cases = load_test_cases()
    
    results = {}
    
    for model in models:
        print(f"\nEvaluating {model}...")
        
        model_results = []
        for case in test_cases:
            # Get output from model
            output = await get_model_output(model, case["input"])
            
            # Evaluate
            result = await agent.evaluate_output(
                rubric_id="comparison_rubric",
                input_prompt=case["input"],
                output_text=output,
                model_name=model
            )
            model_results.append(result)
        
        # Calculate stats
        avg_score = sum(r.overall_score for r in model_results) / len(model_results)
        pass_rate = sum(1 for r in model_results if r.passed) / len(model_results)
        
        results[model] = {
            "avg_score": avg_score,
            "pass_rate": pass_rate,
            "results": model_results
        }
    
    # Print comparison
    print("\n" + "="*70)
    print("MODEL COMPARISON")
    print("="*70)
    
    for model, stats in results.items():
        print(f"\n{model}:")
        print(f"  Average Score: {stats['avg_score']:.2f}/5.0")
        print(f"  Pass Rate: {stats['pass_rate']*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(compare_models())
```

## Troubleshooting

### API Key Not Set

```
Error: API key not configured
```

Solution:
```bash
export ANTHROPIC_API_KEY=your_key_here
```

### Rate Limiting

```
Error: Rate limit exceeded
```

Solution:
```python
# Add delays between evaluations
await asyncio.sleep(1)  # 1 second delay
```

### JSON Parsing Errors

```
Error: JSON decode error
```

Solution:
- Agent uses regex to extract JSON from LLM responses
- If errors persist, check response format
- May need to adjust temperature (currently 0.1-0.3)

### Memory Issues

```
Error: Out of memory
```

Solution:
```python
# Limit history size
agent.regression_detector.history = agent.regression_detector.history[-100:]
```

## Best Practices

### 1. Rubric Design

- Use 4-6 dimensions (not too many)
- Ensure weights sum to 1.0
- Provide clear scoring guides
- Include task-specific dimensions

### 2. Evaluation Strategy

- Start with small test sets
- Provide ground truth when available
- Run multiple evaluations for consistency
- Track trends over time

### 3. Threshold Setting

- Adjust based on your requirements
- Start conservative (3.5/5.0)
- Monitor false positives/negatives
- Different thresholds for different tasks

### 4. Regression Detection

- Set appropriate threshold (0.5 default)
- Consider task criticality
- Review flagged regressions manually
- Update baselines periodically

### 5. Hallucination Tracking

- Monitor rate over time
- Investigate sudden increases
- Review examples regularly
- Correlate with model changes

## Advanced Configuration

### Custom Dimensions

```python
from enum import Enum

class CustomDimension(Enum):
    CREATIVITY = "creativity"
    CONCISENESS = "conciseness"
    TONE = "tone"

# Use in rubric
criterion = EvaluationCriterion(
    dimension=CustomDimension.CREATIVITY,
    description="Novel and creative responses",
    weight=0.3,
    scoring_guide={...}
)
```

### Weighted Scoring

```python
# Different weights for different dimensions
criteria = [
    EvaluationCriterion(dimension=..., weight=0.4),  # Critical
    EvaluationCriterion(dimension=..., weight=0.3),  # Important
    EvaluationCriterion(dimension=..., weight=0.2),  # Nice-to-have
    EvaluationCriterion(dimension=..., weight=0.1)   # Optional
]
```

### Batch Processing

```python
# Process large batches efficiently
async def batch_evaluate(test_cases, batch_size=10):
    results = []
    
    for i in range(0, len(test_cases), batch_size):
        batch = test_cases[i:i+batch_size]
        
        batch_results = await asyncio.gather(*[
            agent.evaluate_output(...) for case in batch
        ])
        
        results.extend(batch_results)
        await asyncio.sleep(2)  # Rate limiting
    
    return results
```

## Performance Tips

1. **Batch evaluations** - Process multiple outputs together
2. **Cache rubrics** - Reuse rubrics across evaluations
3. **Limit history** - Keep only recent evaluations
4. **Async operations** - Use asyncio for concurrency
5. **Rate limiting** - Add delays to avoid API limits

## Support

- GitHub Issues: [Report bugs](https://github.com/ndgbg/fun-agentic-apps/issues)
- Documentation: [README.md](README.md)
- Examples: [agent.py](agent.py)

## Next Steps

1. Run the basic example: `python agent.py`
2. Open the dashboard: `open dashboard.html`
3. Create your own rubrics
4. Integrate with your workflow
5. Monitor quality over time
