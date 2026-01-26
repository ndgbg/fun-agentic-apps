# Bedrock Agent - Quick Start

## What Does This Agent Do?

An AI assistant powered by Claude on AWS Bedrock that can:
- Answer questions on any topic
- Have conversations with context memory
- Help solve problems and provide explanations
- (Optional) Call custom functions via Lambda action groups

Think of it as ChatGPT on your AWS account with full customization.

## How to Run It

### Step 1: Prerequisites

```bash
# Install AWS SDK
pip install boto3

# Configure AWS credentials (you'll need AWS Access Key ID and Secret)
aws configure
```

When running `aws configure`, enter:
- AWS Access Key ID: `[your key]`
- AWS Secret Access Key: `[your secret]`
- Default region: `us-east-1` (or your preferred region)
- Default output format: `json`

### Step 2: Run the Simple Version

```bash
python simple_bedrock_agent.py
```

This will show you a menu:
1. **Create a new agent and demo chat** - Creates an agent and tests it
2. **List my existing agents** - Shows agents you've already created
3. **Interactive chat** - Chat with an existing agent

### Step 3: Choose Option 1 (First Time)

The script will:
1. Create an AI agent (takes ~30 seconds)
2. Prepare it for use
3. Create an alias (like a version number)
4. Ask it 3 demo questions
5. Show you the agent ID and alias ID

**Save these IDs!** You'll need them to chat with your agent later.

## Example Output

```
✓ Connected to Bedrock in us-east-1

📝 Creating agent 'demo-assistant'...
✓ Agent created! ID: ABC123XYZ

⚙️  Preparing agent...
✓ Agent is ready!

🔗 Creating alias 'live'...
✓ Alias created! ID: DEF456UVW

💬 CHATTING WITH YOUR AGENT

👤 You: Hello! What can you help me with?
🤖 Agent: Hi! I'm here to help you with a variety of tasks...

👤 You: What's the capital of France?
🤖 Agent: The capital of France is Paris...
```

## Interactive Chat Mode

Once you have an agent ID and alias ID:

```bash
python simple_bedrock_agent.py
# Choose option 3
# Enter your agent_id: ABC123XYZ
# Enter your alias_id: DEF456UVW
```

Now you can chat freely:
```
👤 You: Tell me a joke
🤖 Agent: Why did the programmer quit his job? Because he didn't get arrays!

👤 You: Explain quantum computing simply
🤖 Agent: Quantum computing uses quantum bits (qubits) that can be...
```

## Using in Your Own Code

```python
from simple_bedrock_agent import SimpleAgent

# Initialize
agent = SimpleAgent(region="us-east-1")

# Create agent (one time)
agent_id = agent.create_simple_agent(name="my-bot")
agent.prepare_agent(agent_id)
alias_id = agent.create_alias(agent_id)

# Chat with it
response = agent.chat(
    agent_id=agent_id,
    alias_id=alias_id,
    message="What's 2+2?"
)
print(response)  # "2+2 equals 4"
```

## Cost Estimate

- **Agent creation**: Free
- **Chat messages**: ~$0.003 per 1000 input tokens, ~$0.015 per 1000 output tokens
- **Typical conversation**: $0.01 - $0.05

A 10-message conversation costs about $0.02.

## Troubleshooting

### "NoCredentialsError"
Run `aws configure` and enter your AWS credentials.

### "AccessDeniedException"
Your AWS account needs Bedrock permissions. Contact your AWS admin or add these policies:
- `AmazonBedrockFullAccess`

### "ResourceNotFoundException: Foundation model not found"
Your region might not support Claude. Try `us-east-1` or `us-west-2`.

### "Agent not ready"
Wait 30-60 seconds after creating an agent before chatting with it.

## Advanced Features

### Adding Action Groups (Lambda Functions)

Action groups let your agent call external APIs. See `bedrock_lambda_function.py` for an example Lambda handler.

To add an action group:
```python
from simple_bedrock_agent import SimpleAgent

agent = SimpleAgent()
# Create agent first, then add action group with OpenAPI schema
```

### IAM Permissions Required

Your AWS user/role needs:
- `bedrock:CreateAgent`
- `bedrock:PrepareAgent`
- `bedrock:CreateAgentAlias`
- `bedrock:InvokeAgent`
- `bedrock:ListAgents`
- `bedrock:DeleteAgent`

For action groups, also add:
- `lambda:CreateFunction`
- `lambda:InvokeFunction`

## Next Steps

1. Customize the agent instruction in `simple_bedrock_agent.py`
2. Add action groups for custom function calling
3. Add knowledge bases for RAG (document Q&A)
4. Deploy to production with a web interface

## Clean Up

To avoid charges, delete agents you're not using:

```python
from simple_bedrock_agent import SimpleAgent

agent = SimpleAgent()
agent.delete_agent("your-agent-id")
```

Or use AWS Console:
1. Go to AWS Bedrock
2. Click "Agents"
3. Select your agent
4. Click "Delete"
