import os
from pathlib import Path
from typing import List, Dict, Literal
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import (
    BaseMessage, HumanMessage, SystemMessage, AIMessage, ToolMessage
)
from langchain_core.tools import tool, BaseTool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
from typing_extensions import Annotated, TypedDict
from .manager import SkillManager
from .models import Skill


class AgentState(TypedDict):
    """Agent state with message history."""
    messages: Annotated[List[BaseMessage], add_messages]


class AgentEngine:
    """AI Agent with progressive skill loading."""
    
    BASE_PROMPT = """You are a powerful AI Coding Agent.

You have access to tools that help you accomplish tasks. Think step by step:
1. Analyze the user's request
2. If the task requires specialized knowledge, use `list_skills` to see available skills
3. Use `load_skill` to get detailed instructions for relevant skills
4. Follow the skill instructions to complete the task using appropriate tools
5. After using a tool, analyze the result and decide next steps

Always use tools when needed. Be thorough and systematic.
"""
    
    def __init__(self, skills_dir: str, model_name: str = "deepseek-chat"):
        self.skill_manager = SkillManager(Path(skills_dir))
        self.skill_manager.discover_skills()
        self.custom_tools: List[BaseTool] = []
        
        # Initialize LLM
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required.")
            
        self.llm = ChatDeepSeek(model=model_name, temperature=0)
        self._graph = None
        
    def _create_skill_tools(self) -> List[BaseTool]:
        """Create tools for progressive skill loading."""
        skill_manager = self.skill_manager
        
        @tool
        def list_skills() -> str:
            """List all available skills with their names and descriptions.
            Use this to discover what specialized capabilities are available.
            """
            skills = skill_manager.list_skills()
            if not skills:
                return "No skills available."
            
            result = "Available Skills:\n"
            for s in skills:
                result += f"- {s.name}: {s.description}\n"
            return result
        
        @tool
        def load_skill(skill_name: str) -> str:
            """Load detailed instructions (SOP) for a specific skill.
            Use this when you need guidance on how to perform a specialized task.
            
            Args:
                skill_name: The exact name of the skill to load.
            """
            skill = skill_manager.get_skill(skill_name)
            if not skill:
                available = [s.name for s in skill_manager.list_skills()]
                return f"Skill '{skill_name}' not found. Available: {available}"
            
            return f"""=== SKILL: {skill.name} ===
Version: {skill.version}

{skill.instructions}

=== END SKILL ==="""
        
        return [list_skills, load_skill]
    
    def register_tool(self, tool_func: BaseTool):
        """Register a custom tool for the agent."""
        self.custom_tools.append(tool_func)
        self._graph = None  # Reset graph to rebuild with new tool
        
    def _build_graph(self):
        """Build the LangGraph workflow with modern API."""
        # Combine skill tools + custom tools
        all_tools = self._create_skill_tools() + self.custom_tools
        
        if not all_tools:
            raise ValueError("No tools available.")
        
        llm_with_tools = self.llm.bind_tools(all_tools)
        system_prompt = self.BASE_PROMPT
        
        def agent_node(state: AgentState) -> Dict:
            """Process messages and generate response."""
            messages = state["messages"]
            # Ensure system message is first
            if not messages or not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=system_prompt)] + messages
            response = llm_with_tools.invoke(messages)
            return {"messages": [response]}
        
        def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
            """Route based on whether tool calls exist."""
            last_message = state["messages"][-1]
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                return "tools"
            return END
        
        # Build graph
        builder = StateGraph(AgentState)
        builder.add_node("agent", agent_node)
        builder.add_node("tools", ToolNode(all_tools))
        
        builder.add_edge(START, "agent")
        builder.add_conditional_edges("agent", should_continue, ["tools", END])
        builder.add_edge("tools", "agent")
        
        self._graph = builder.compile()
        
    def run(self, user_input: str, max_iterations: int = 25) -> str:
        """Run the agent with progressive skill loading."""
        if self._graph is None:
            self._build_graph()
            
        print(f"\n{'='*60}")
        print(f"User: {user_input[:100]}{'...' if len(user_input) > 100 else ''}")
        print(f"Available Skills: {[s.name for s in self.skill_manager.list_skills()]}")
        print(f"Custom Tools: {[t.name for t in self.custom_tools]}")
        print(f"{'='*60}")
        
        state: AgentState = {"messages": [HumanMessage(content=user_input)]}
        
        step = 0
        for event in self._graph.stream(state, {"recursion_limit": max_iterations}):
            for node_name, node_output in event.items():
                step += 1
                self._log_step(step, node_name, node_output)
        
        # Extract final AI response
        final_state = event.get("agent", event.get("__end__", {}))
        messages = final_state.get("messages", [])
        
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
                return msg.content
        
        return "Agent completed but produced no final response."
    
    def _log_step(self, step: int, node_name: str, output: Dict):
        """Log execution step."""
        print(f"\n[Step {step}] {node_name}")
        
        messages = output.get("messages", [])
        for msg in messages:
            if isinstance(msg, AIMessage):
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        print(f"  -> Tool Call: {tc['name']}({tc.get('args', {})})")
                elif msg.content:
                    preview = msg.content[:150] + "..." if len(msg.content) > 150 else msg.content
                    print(f"  -> Response: {preview}")
            elif isinstance(msg, ToolMessage):
                preview = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
                print(f"  <- Result: {preview}")
