# AI Product Review Board 🎭

**Your toughest stakeholder — automated.**

An agentic AI that intelligently reviews product specs using LLM reasoning.

## What Makes It Agentic

✅ **Understands context** - Not just pattern matching  
✅ **Reasons about implications** - Thinks through consequences  
✅ **Asks follow-up questions** - Adapts to your spec  
✅ **Suggests improvements** - Concrete, specific fixes  
✅ **Provides evidence** - Quotes from your spec  

## What It Does

Reviews product specs and:
- Flags critical issues with evidence
- Asks brutal questions from 6 personas
- Suggests specific improvements
- Answers follow-up questions

### The Board

- 😤 **Skeptical CTO** - Technical feasibility and scale
- 📊 **Data-Driven CEO** - Metrics and business impact
- 👥 **User Advocate** - User needs and validation
- 🛡️ **Risk Manager** - Safety and compliance
- 🤖 **AI Ethics Officer** - Bias and responsible AI
- 💰 **Finance Director** - Costs and ROI

## Quick Start

```bash
# Set API key
export ANTHROPIC_API_KEY=your_key

# Install
pip install -r requirements.txt

# Run
python agentic_review_board.py
```

## Example Output

```
🎭 AGENTIC AI PRODUCT REVIEW BOARD
======================================================================

VERDICT: 🚫 BLOCKED
Reasoning: Critical gaps in safety, metrics, and user validation

🚨 CRITICAL ISSUES:

❌ No user consent mechanism for AI-generated content
   Evidence: "The AI will post automatically"
   Impact: Users may not want AI posting without review

💬 QUESTIONS FROM THE BOARD:

😤 Skeptical CTO
  • What happens when the AI generates inappropriate content?
  • How do you prevent amplifying harmful patterns?

📊 Data-Driven CEO
  • What's the baseline engagement rate?
  • What's the cost vs. expected revenue impact?

💡 SUGGESTED IMPROVEMENTS:

📌 Add User Control
   Implement approval workflow for AI-generated posts

📌 Define Success Metrics
   Specify: engagement rate target, adoption rate, quality score
```

## Usage

### Review a Spec

```python
from agentic_review_board import AgenticReviewBoard

board = AgenticReviewBoard()
review = board.review_spec(your_spec_text)
print(board.format_review(review))
```

### Ask Follow-Up Questions

```python
answer = board.ask_followup(
    your_spec_text,
    review,
    "What metrics should we track?"
)
```

### Get Improvement Suggestions

```python
improvements = board.suggest_improvements(
    your_spec_text,
    focus_area="success metrics"
)
```

## Why It's Useful

**Before:** Specs go to stakeholders → wait days → vague feedback  
**After:** Instant intelligent review → specific issues → concrete fixes

**Psychological safety:** Easier to hear tough feedback from AI than people.

**Consistency:** Same standards every time.

**Speed:** 5 seconds vs. days of waiting.

## Integration Ideas

- Slack bot for spec reviews
- GitHub Action for PR reviews
- Notion integration
- CLI tool: `review-spec my-prd.md`

## License

MIT

---

*"Finally, a stakeholder who's always available and never in back-to-back meetings."*
