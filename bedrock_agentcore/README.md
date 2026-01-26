# AWS Bedrock AgentCore Tutorial

Learn how to build and deploy AI agents using **AWS Bedrock AgentCore** - a fully managed agentic platform for building, deploying, and operating highly capable agents securely at scale.

## What is AWS Bedrock AgentCore?

[AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) is an enterprise-grade platform that provides the infrastructure and services needed to build production-ready AI agents. Unlike basic chatbots, AgentCore enables agents that can:

- **Take actions** across your tools, APIs, and data sources
- **Run securely** with identity management and session isolation
- **Scale automatically** with serverless infrastructure
- **Work with any framework** (LangGraph, CrewAI, LlamaIndex, etc.)
- **Use any model** (Claude, GPT, Gemini, Llama, etc.)

Think of it as the complete operating system for AI agents - handling runtime, memory, security, observability, and more so you can focus on building agent logic.

ore Platform Components

AgentCore provides several integrated services:

### 🚀 Runtime
Serverless execution environment for agents with fast cold starts, extended runtimes for async tasks, and true session isolation. Works with any framework (LangGraph, CrewAI, LlamaIndex) and any model.

### 🧠 Memory
mory that persists across sessions. Agents can learn from experiences and share memory stores.

### 🔌 Gateway
Converts your APIs, Lambda functions, and services into Model Context Protocol (MCP)-compatible tools. Connects to Salesforce, Slack, JIRA, Zoom, and more.

### 🔐 Identity
Secure authentication and access manageh existing identity providers (Cognito, Okta, Azure AD, Auth0).

### 💻 Code Interpreter
Isolated sandbox for agents to execute Python, JavaScript, and TypeScript code safely.

### 🌐 Browser
Cloud-based browser runtime for agents to interact with web applications, fill forms, and extract information.

### 📊 Observability
Unid tracing, debugging, and monitoring with OpenTelemetry-compatible format. Visualize agent execution paths and debug bottlenecks.

### ✅ Evaluations
Automated testing and quality assessment for agents. Measure task execution, edge case handling, and output reliability.

### 📋 Policy
Define business ranguage or Cedar policy language. Control which tools agents can access and under what conditions.

## This Tutorial: Getting Started with Bedrock Agents

This prototype focuses on **Bedr exploring the full AgentCore capabilities.

### What You'll Build

A conversational AI agent powered by Claude that can:
- Answer questions and have multi-turn conversations
- (Optional) Callxternal functions via Lambda action groups
- Maintain context within sessions
- Be deployed and managed through AWS

### Prerequisites

- AWS account with Bedrock access
- Python 3.9+
- Basic familiarity with AWS CLI

## Quick Start

### Step 1: Set Up Your Environment

```bash
# Install the AWS SDK
pip install boto3

# Configure your AWS credentials
aws configure
```

You'll need:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (use `us-east-1` or `us-west-2` for Bedrock)

###ur First Agent

Run the interactive script:

```bash
python simple_bedrock_agent.py
```

Choose **option 1** to create and test a new agent. The script will:

1. **Create the agent** with Claude 3 Sonnet as the foundation model
2. **Prepare it** (compiles the agent configuration)
3. **Create an alias** so you can invoke it
4. **Test it** with sample questions

You'll see output like:
```
✓ Agent created! ID: ABC123XYZ
✓ Agent is ready!
✓ Alias created! ID: TSTALIASID

👤 You: What's the capital of France?
🤖 Agent: The capital of France is Paris...
```

**Save your agent ID and alias ID** - you'll need them to chat with your agent later.

### Step 3: Interactive Chat

Run the script again and choose **option 3**:

```bash
python simple_bedrock_agent.py
# Choose option 3
# Enter your agent_id and alias_id
```

Now you can have real conversations:
```
👤 You: Tell me about quantum computing
🤖 Agent: Quantum computing is a type of computing that uses...

👤 You: How is it different from classical computing?
🤖 Agent: The key difference is that classical computers use bits...
```

### Step 4: Use It in Your Code

```python
from simple_bedrock_agent import SimpleAgent

# Initialize the agent client
agent = SimpleAgent(region="us-east-1")

# Create an agent (one-time setup)
agent_id = agent.create_simple_agent(name="my-assistant")
agent.prepare_agent(agent_id)
alias_id = agent.create_alias(agent_id)

# Chat with it
response = agent.chat(
    agent_id=agent_id,
    alias_id=alias_id,
    message= simple terms"
)
print(response)
```

## Advanced: Adding Action Groups

Action groups let your agent call functions and take actions.

### 1. Create a Lambda Function

Deploy `bedrock_lambda_function.py`:

```bash
# Package it
zip lambda_function.zip bedrock_lambda_function.py

# Deploy it
aws lambda create-function \
  --function-name bedrock-agent-actions \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-role \
  --handler bedrock_lambda_function.lambda_handler \
  --zip-file fileb://lambda_funion.zip
```

### 2. Connect It to Your Agent

The Lambda function includes an OpenAPI schema describing available functions. Connect it:

```python
agent.create_agent_action_group(
    agent_id=agent_id,
    action_group_name="weather-actions",
    lambda_arn="arn:aws:lambda:us-east-1:123456789012:function:bedrock-agent-actions"
)
```

ill:
1. Understand the request
2. Call your Lambda function with `location="Seattle"`
3. Get the result
4. Format a natural response

## Real-World Use Cases

**Customer Support Agent**
- Answers FAQs from knowledge base
- Looks up order status via API
- Creates support tickets

**Data Analysis Agent**
- Queries databases with natural language
- Generates reports and visualizations
- Explains insights in plain English

**DevOps Agent**
- Checks system health
- Deploys applications
- Troubleshoots issues

**Manufacturing Agent** (like Amazon Devices)
- Converts business requirements into instructions
- Optimizes robotic vision models
- Reduces engineering time from days to hours

## Cost Breakdown

- **Agent creation**: Free
- **Model invocation**: ~$3 per million input tokens, ~$15 per million output tokens (Claude 3 Sonnet)
- **Typical conversation**: $0.01 - $0.05
- **Lambda calls**: $0.20 per million requests + compute time

A production agent handling 1000 conversations/day costs roughly $20-30/month.

## Files in This Project

- **README.md** - This tutorial
- **QUICK_START.md** - Quick reference guide with troubleshooting
- **simple_bedrock_agent.py** - Complete agent implementation with CLI
- **bedrock_lambda_function.py** - Example Lambda handler for action groups
- **requirements_bedrock.txt** - Python dependencies

## Next Steps

### Explore Full AgentCore Platform

Once you're comfortable with basic agents, explore the full AgentCore capabilities:

1. **AgentCore Runtime** - Deploy agents with any framework (LangGraph, CrewAI)
2. **AgentCore Memory** - Add persistent memory across sessions
3. **AgentCore Gateway** - Connect to MCP tools and enterprise APIs
4. **AgentCore Identity** - Integrate with your identity provider
5. **AgentCore Observability** - Monitor and debug in production
6. **AgentCore Policy** - Define business rules and boundaries

### Extend This Prototype

- Add knowledge bases for RAG capabilities
- Implement guardrails for content filtering
- Create a web interface
ation
- Add code interpreter capabilities

## Resources

- [AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)
- [AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html)
- [Bedrock Agents Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [AgentCore FAQs](https://aws.amazon.com/bedrock/agentcore/faqs/)
- [Claude Model Documentation](https://docs.anthropic.com/claude/docs)

## Troubleshooting

See [QUICK_START.md](QUICK_START.md) for common issues and solutions.

## Contributing

This is a learning prototype. Feel free to extend it with:
- More action group examples
- Knowledge base integration
- Multi-agent workflows
- AgentCore Runtime integration
- MCP tool connections

---

Built with ❤️ using AWS Bedrock AgentCore and Claude 3

*Content rephrased for compliance with licensing restrictions. See [AWS documentation](https://docs.aws.amazon.com/bedrock-agentcore/) for official details.*
