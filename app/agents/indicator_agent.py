from typing import Annotated, TypedDict, List, Dict, Any, Sequence, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from ..tools.indicator_tools import query_indicator_semantics, query_indicator_value
from ..db import SessionLocal
from ..models import database as models
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Define the state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    indicators: List[str]
    sop_id: Optional[int]
    current_task_index: int
    report: str
    next_node: str

# Tools
tools = [query_indicator_semantics, query_indicator_value]
tool_node = ToolNode(tools)

# Model
model = ChatOpenAI(model="gpt-4o", streaming=True)
model_with_tools = model.bind_tools(tools)

# Nodes
def initialize_context(state: AgentState):
    return {"indicators": [], "sop_id": None, "current_task_index": 0, "report": ""}

def indicator_recognition(state: AgentState):
    last_message = state["messages"][-1].content
    # Use LLM to extract indicators from query
    prompt = f"Extract indicator names from this query: '{last_message}'. Return a JSON list of names."
    response = model.invoke([HumanMessage(content=prompt)])
    try:
        indicators = json.loads(response.content)
    except:
        indicators = []
    
    if not indicators:
        return {"next_node": END}
    return {"indicators": indicators, "next_node": "sop_recall"}

def sop_recall(state: AgentState):
    db = SessionLocal()
    try:
        # Simplified SOP recall: match indicator name to SOP description or tasks
        indicators = state["indicators"]
        sop = db.query(models.SOP).filter(models.SOP.description.like(f"%{indicators[0]}%")).first()
        if sop:
            return {"sop_id": sop.id, "next_node": "sop_agent"}
        else:
            return {"next_node": "general_agent"}
    finally:
        db.close()

def general_agent(state: AgentState):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

def sop_agent(state: AgentState):
    db = SessionLocal()
    try:
        sop = db.query(models.SOP).filter(models.SOP.id == state["sop_id"]).first()
        tasks = sop.tasks
        current_idx = state["current_task_index"]
        
        if current_idx >= len(tasks):
            return {"next_node": END}
        
        task = tasks[current_idx]
        prompt = f"Execute task: {task.name}. Details: {task.detail}. Context: {state['indicators']}"
        # In a real SOP agent, we might loop through tools. Here we just let LLM handle the task.
        response = model_with_tools.invoke(state["messages"] + [HumanMessage(content=prompt)])
        
        return {
            "messages": [response],
            "current_task_index": current_idx + 1,
            "next_node": "sop_agent" if current_idx + 1 < len(tasks) else END
        }
    finally:
        db.close()

# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("initialize", initialize_context)
workflow.add_node("recognition", indicator_recognition)
workflow.add_node("sop_recall", sop_recall)
workflow.add_node("general_agent", general_agent)
workflow.add_node("sop_agent", sop_agent)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("initialize")
workflow.add_edge("initialize", "recognition")

def route_after_recognition(state):
    return state["next_node"]

workflow.add_conditional_edges("recognition", route_after_recognition, {
    "sop_recall": "sop_recall",
    END: END
})

def route_after_sop_recall(state):
    return state["next_node"]

workflow.add_conditional_edges("sop_recall", route_after_sop_recall, {
    "sop_agent": "sop_agent",
    "general_agent": "general_agent"
})

def route_agent(state):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

workflow.add_conditional_edges("general_agent", route_agent)
workflow.add_conditional_edges("sop_agent", route_agent)
workflow.add_edge("tools", "general_agent") # For simplicity, both return to general for now

# Compile
app_graph = workflow.compile()
