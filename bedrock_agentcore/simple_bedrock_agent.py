"""
Simple Bedrock Agent - Easy to understand and run

What this agent does:
1. Creates an AI assistant powered by Claude on AWS Bedrock
2. Can answer questions and have conversations
3. (Optional) Can call external functions like getting weather data

How to run:
1. Install: pip install boto3
2. Configure AWS: aws configure (enter your credentials)
3. Run: python simple_bedrock_agent.py
"""

import boto3
import json
import uuid
from typing import Optional

class SimpleAgent:
    """A conversational AI agent using Bedrock"""
    
    def __init__(self, region: str = "us-east-1"):
        """Initialize the agent client"""
        self.region = region
        self.bedrock_agent = boto3.client('bedrock-agent', region_name=region)
        self.bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name=region)
        print(f"✓ Connected to Bedrock in {region}")
    
    def create_simple_agent(self, name: str = "my-assistant") -> str:
        """
        Create a basic conversational agent
        Returns: agent_id
        """
        print(f"\n📝 Creating agent '{name}'...")
        
        try:
            response = self.bedrock_agent.create_agent(
                agentName=name,
                foundationModel="anthropic.claude-3-sonnet-20240229-v1:0",
                instruction="""You are a helpful AI assistant. You can:
                - Answer questions on any topic
                - Help with problem-solving
                - Provide explanations and summaries
                - Have natural conversations
                
                Be friendly, concise, and helpful.""",
                description="A simple conversational AI assistant"
            )
            
            agent_id = response['agent']['agentId']
            print(f"✓ Agent created! ID: {agent_id}")
            return agent_id
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise
    
    def prepare_agent(self, agent_id: str):
        """Prepare agent for use (required before invoking)"""
        print(f"\n⚙️  Preparing agent...")
        try:
            self.bedrock_agent.prepare_agent(agentId=agent_id)
            print("✓ Agent is ready!")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise
    
    def create_alias(self, agent_id: str, alias_name: str = "live") -> str:
        """Create an alias to invoke the agent"""
        print(f"\n🔗 Creating alias '{alias_name}'...")
        try:
            response = self.bedrock_agent.create_agent_alias(
                agentId=agent_id,
                agentAliasName=alias_name,
                description="Live version of the agent"
            )
            alias_id = response['agentAlias']['agentAliasId']
            print(f"✓ Alias created! ID: {alias_id}")
            return alias_id
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise
    
    def chat(self, agent_id: str, alias_id: str, message: str, session_id: Optional[str] = None) -> str:
        """
        Send a message to the agent and get a response
        
        Args:
            agent_id: Your agent ID
            alias_id: Your alias ID
            message: What you want to ask
            session_id: Optional session ID to maintain conversation context
        
        Returns:
            Agent's response as a string
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        try:
            response = self.bedrock_runtime.invoke_agent(
                agentId=agent_id,
                agentAliasId=alias_id,
                sessionId=session_id,
                inputText=message
            )
            
            # Collect the streaming response
            result = ""
            for event in response['completion']:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        result += chunk['bytes'].decode('utf-8')
            
            return result.strip()
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def list_my_agents(self):
        """List all your existing agents"""
        print("\n📋 Your existing agents:")
        try:
            response = self.bedrock_agent.list_agents(maxResults=10)
            agents = response.get('agentSummaries', [])
            
            if not agents:
                print("   No agents found")
                return []
            
            for agent in agents:
                print(f"   • {agent['agentName']} (ID: {agent['agentId']})")
            
            return agents
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return []
    
    def delete_agent(self, agent_id: str):
        """Delete an agent"""
        print(f"\n🗑️  Deleting agent {agent_id}...")
        try:
            self.bedrock_agent.delete_agent(agentId=agent_id)
            print("✓ Agent deleted")
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def demo_create_and_chat():
    """Demo: Create a new agent and chat with it"""
    print("=" * 60)
    print("DEMO: Create and Chat with a Bedrock Agent")
    print("=" * 60)
    
    agent = SimpleAgent(region="us-east-1")
    
    # Step 1: Create the agent
    agent_id = agent.create_simple_agent(name="demo-assistant")
    
    # Step 2: Prepare it
    agent.prepare_agent(agent_id)
    
    # Step 3: Create an alias
    alias_id = agent.create_alias(agent_id, alias_name="live")
    
    # Step 4: Chat with it!
    print("\n" + "=" * 60)
    print("💬 CHATTING WITH YOUR AGENT")
    print("=" * 60)
    
    session_id = str(uuid.uuid4())
    
    questions = [
        "Hello! What can you help me with?",
        "What's the capital of France?",
        "Can you explain what AWS Bedrock is in one sentence?"
    ]
    
    for question in questions:
        print(f"\n👤 You: {question}")
        response = agent.chat(agent_id, alias_id, question, session_id)
        print(f"🤖 Agent: {response}")
    
    print("\n" + "=" * 60)
    print(f"✓ Demo complete!")
    print(f"Agent ID: {agent_id}")
    print(f"Alias ID: {alias_id}")
    print(f"Session ID: {session_id}")
    print("\nTo delete this agent, run:")
    print(f"  agent.delete_agent('{agent_id}')")
    print("=" * 60)


def demo_list_agents():
    """Demo: List all your existing agents"""
    print("=" * 60)
    print("DEMO: List Your Agents")
    print("=" * 60)
    
    agent = SimpleAgent(region="us-east-1")
    agent.list_my_agents()


def interactive_chat(agent_id: str, alias_id: str):
    """Interactive chat session with your agent"""
    print("=" * 60)
    print("💬 INTERACTIVE CHAT")
    print("=" * 60)
    print("Type 'quit' to exit\n")
    
    agent = SimpleAgent(region="us-east-1")
    session_id = str(uuid.uuid4())
    
    while True:
        user_input = input("👤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break
        
        if not user_input:
            continue
        
        response = agent.chat(agent_id, alias_id, user_input, session_id)
        print(f"🤖 Agent: {response}\n")


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║         Simple Bedrock Agent - Quick Start               ║
╚══════════════════════════════════════════════════════════╝

Choose an option:
1. Create a new agent and demo chat
2. List my existing agents
3. Interactive chat (need agent_id and alias_id)

""")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        demo_create_and_chat()
    elif choice == "2":
        demo_list_agents()
    elif choice == "3":
        agent_id = input("Enter agent ID: ").strip()
        alias_id = input("Enter alias ID: ").strip()
        interactive_chat(agent_id, alias_id)
    else:
        print("Invalid choice. Run the script again.")
