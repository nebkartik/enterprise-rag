from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.state import AgentState
from app.agents.nodes.planner import planner_node 
from app.agents.nodes import retrieve_node
from app.agents.nodes import generate_node
import os
import logfire

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

def build_checkpointer():
    """
    LOCAL_MODE=true  → MemorySaver (default, no DB needed)
    LOCAL_MODE=false → PostgresSaver backed by Cloud SQL
                       Falls back to MemorySaver if connection fails.
    """
    local_mode = os.getenv("LOCAL_MODE", "true").lower() == "true"

    if local_mode:
        logfire.info("🧠 Checkpointer: MemorySaver (LOCAL_MODE=true)")
        return MemorySaver()

    try:
        from langgraph.checkpoint.postgres import PostgresSaver
        from app.services.database_service import get_db_pool

        pool = get_db_pool()
        if pool is None:
            logfire.warning("⚠️ Postgres pool unavailable — falling back to MemorySaver")
            return MemorySaver()

        checkpointer = PostgresSaver(pool)
        checkpointer.setup()  # creates checkpoint tables on first run
        logfire.info("✅ Checkpointer: PostgresSaver (persistent memory)")
        return checkpointer

    except Exception as e:
        logfire.error(f"❌ PostgresSaver init failed, using MemorySaver: {e}")
        return MemorySaver()




rag_agent = workflow.compile(checkpointer=build_checkpointer())