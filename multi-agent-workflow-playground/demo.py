#!/usr/bin/env python3
"""
Demo: Building and executing a custom workflow
"""

import asyncio
from engine import (
    WorkflowBuilder, WorkflowEngine, 
    AgentRole, Tool, ToolType, Memory, MemoryType
)

async def demo_content_creation_workflow():
    """Demo: Content creation workflow with 4 agents."""
    
    print("🎬 DEMO: Content Creation Workflow")
    print("=" * 70)
    print()
    
    # Initialize builder
    builder = WorkflowBuilder()
    
    # Create workflow
    workflow = builder.create_workflow(
        "Blog Post Creator",
        "Research, outline, write, and review blog posts"
    )
    
    print("📋 Building workflow...")
    
    # 1. Researcher - Gathers information
    researcher = builder.add_agent(
        workflow.id,
        "Research Specialist",
        AgentRole.RESEARCHER,
        "You are a research specialist. Gather comprehensive information about the topic. Focus on key facts, statistics, and insights.",
        tools=[Tool(ToolType.WEB_SEARCH, "web_search")],
        memory=Memory(MemoryType.SHORT_TERM, capacity=10)
    )
    print(f"   ✓ Added {researcher.name}")
    
    # 2. Analyst - Creates outline
    analyst = builder.add_agent(
        workflow.id,
        "Content Strategist",
        AgentRole.ANALYST,
        "You are a content strategist. Analyze the research and create a structured outline with key sections and talking points.",
        memory=Memory(MemoryType.SHORT_TERM, capacity=5)
    )
    print(f"   ✓ Added {analyst.name}")
    
    # 3. Writer - Creates content
    writer = builder.add_agent(
        workflow.id,
        "Content Writer",
        AgentRole.WRITER,
        "You are a skilled content writer. Write engaging, clear content following the outline. Use a conversational but professional tone.",
        memory=Memory(MemoryType.SHORT_TERM, capacity=5)
    )
    print(f"   ✓ Added {writer.name}")
    
    # 4. Critic - Reviews and improves
    critic = builder.add_agent(
        workflow.id,
        "Editor",
        AgentRole.CRITIC,
        "You are an editor. Review the content for clarity, accuracy, and engagement. Provide specific improvements.",
        memory=Memory(MemoryType.SHARED)
    )
    print(f"   ✓ Added {critic.name}")
    
    # Connect agents in sequence
    builder.connect_agents(workflow.id, researcher.id, analyst.id)
    builder.connect_agents(workflow.id, analyst.id, writer.id)
    builder.connect_agents(workflow.id, writer.id, critic.id)
    
    print(f"   ✓ Connected {len(workflow.connections)} agents")
    print()
    
    # Save workflow
    builder.save_workflow(workflow.id, "demo_workflow.json")
    print("💾 Workflow saved to: demo_workflow.json")
    print()
    
    # Show visualization
    print("📊 Workflow Structure:")
    print(builder.export_visualization(workflow.id))
    print()
    
    # Execute workflow
    print("🚀 Executing workflow...")
    print("-" * 70)
    
    engine = WorkflowEngine()
    results = await engine.execute_workflow(
        workflow,
        "Write a blog post about the benefits of multi-agent AI systems"
    )
    
    # Display results
    print()
    print("📈 EXECUTION RESULTS:")
    print("=" * 70)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.agent_name}")
        print(f"   {'─' * 60}")
        print(f"   Input: {result.input[:80]}...")
        print(f"   Output: {result.output[:150]}...")
        print(f"   Tools: {', '.join(result.tools_used) if result.tools_used else 'None'}")
        print(f"   Memory: {'✓' if result.memory_accessed else '✗'}")
        print(f"   Time: {result.execution_time:.2f}s")
        
        if result.error:
            print(f"   ❌ Error: {result.error}")
    
    print("\n" + "=" * 70)
    print(f"✅ Workflow completed: {len(results)} agents executed")
    print()
    
    return workflow, results

async def demo_parallel_workflow():
    """Demo: Parallel agent execution."""
    
    print("\n🎬 DEMO: Parallel Analysis Workflow")
    print("=" * 70)
    print()
    
    builder = WorkflowBuilder()
    
    workflow = builder.create_workflow(
        "Multi-Perspective Analysis",
        "Analyze a topic from multiple perspectives simultaneously"
    )
    
    # Coordinator starts the workflow
    coordinator = builder.add_agent(
        workflow.id,
        "Coordinator",
        AgentRole.COORDINATOR,
        "You coordinate the analysis. Break down the topic into key aspects to analyze.",
        memory=Memory(MemoryType.SHARED)
    )
    
    # Multiple analysts work in parallel (simulated sequence for demo)
    analyst1 = builder.add_agent(
        workflow.id,
        "Technical Analyst",
        AgentRole.ANALYST,
        "You analyze technical feasibility and implementation challenges.",
        memory=Memory(MemoryType.SHORT_TERM, capacity=5)
    )
    
    analyst2 = builder.add_agent(
        workflow.id,
        "Business Analyst",
        AgentRole.ANALYST,
        "You analyze business value, ROI, and market opportunities.",
        memory=Memory(MemoryType.SHORT_TERM, capacity=5)
    )
    
    # Writer synthesizes all perspectives
    writer = builder.add_agent(
        workflow.id,
        "Synthesis Writer",
        AgentRole.WRITER,
        "You synthesize multiple perspectives into a cohesive analysis.",
        memory=Memory(MemoryType.SHARED)
    )
    
    # Connect in sequence (parallel would require engine enhancement)
    builder.connect_agents(workflow.id, coordinator.id, analyst1.id)
    builder.connect_agents(workflow.id, analyst1.id, analyst2.id)
    builder.connect_agents(workflow.id, analyst2.id, writer.id)
    
    print("📊 Workflow Structure:")
    print(builder.export_visualization(workflow.id))
    print()
    
    print("💡 Note: True parallel execution requires engine enhancement.")
    print("   Current implementation executes sequentially.")
    print()
    
    return workflow

async def demo_conditional_workflow():
    """Demo: Conditional routing based on agent output."""
    
    print("\n🎬 DEMO: Conditional Workflow")
    print("=" * 70)
    print()
    
    builder = WorkflowBuilder()
    
    workflow = builder.create_workflow(
        "Quality-Gated Content",
        "Content creation with quality gates"
    )
    
    writer = builder.add_agent(
        workflow.id,
        "Writer",
        AgentRole.WRITER,
        "You write content. Be concise and clear.",
        memory=Memory(MemoryType.SHORT_TERM, capacity=3)
    )
    
    critic = builder.add_agent(
        workflow.id,
        "Quality Checker",
        AgentRole.CRITIC,
        "You check quality. If good, approve. If needs work, suggest improvements.",
        memory=Memory(MemoryType.SHORT_TERM, capacity=3)
    )
    
    # In a full implementation, this would route back to writer if quality check fails
    builder.connect_agents(workflow.id, writer.id, critic.id, condition="success")
    
    print("📊 Workflow Structure:")
    print(builder.export_visualization(workflow.id))
    print()
    
    print("💡 Note: Conditional routing is supported in the engine.")
    print("   Conditions: 'success', 'error', or custom logic.")
    print()
    
    return workflow

async def main():
    """Run all demos."""
    
    print("\n" + "=" * 70)
    print("  MULTI-AGENT WORKFLOW PLAYGROUND - DEMOS")
    print("=" * 70)
    print()
    
    # Demo 1: Full content creation workflow
    await demo_content_creation_workflow()
    
    # Demo 2: Parallel workflow (conceptual)
    await demo_parallel_workflow()
    
    # Demo 3: Conditional workflow
    await demo_conditional_workflow()
    
    print("\n" + "=" * 70)
    print("✨ All demos completed!")
    print()
    print("Next steps:")
    print("  1. Open index.html for visual builder")
    print("  2. Set ANTHROPIC_API_KEY for real execution")
    print("  3. Build your own workflows!")
    print("=" * 70)
    print()

if __name__ == "__main__":
    asyncio.run(main())
