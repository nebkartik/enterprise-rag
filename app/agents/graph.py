from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import AgentState
from app.agents.nodes.planner import planner_node 
from app.agents.nodes import retrieve_node
from app.agents.nodes import generate_node

workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("retriever", retrieve_node)
workflow.add_node("responder", generate_node)

def route_planner(state: AgentState):
    if state["current_query"] == "CONVERSATIONAL":
        return "responder"
    return "retriever"

workflow.add_conditional_edges(
    "planner",
    route_planner,
    {
        "retriever": "retriever",
        "responder": "responder"
    }
)

workflow.set_entry_point("planner")
workflow.add_edge("retriever", "responder")
workflow.add_edge("responder", END)

checkpointer = MemorySaver()

rag_agent = workflow.compile(checkpointer=checkpointer)