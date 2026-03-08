from typing import Annotated, TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    The state of the Agri-Agent reasoning loop.
    """

    messages: Annotated[List[BaseMessage], operator.add]
    sensor_data: Dict[str, Any]
    weather_forecast: Dict[str, Any]
    retrieved_knowledge: List[str]
    et_data: str
    decision: Dict[str, Any]
    human_approved: bool


def data_acquisition_node(state: AgentState):
    """
    Node to fetch real-time sensor and weather data.
    Skip fetching if data is already provided in the initial state (via Dashboard).
    """
    if state.get("sensor_data") and state.get("weather_forecast"):
        print("[STEP 1] Using pre-acquired data from dashboard.")
        return {}

    from src.tools.agent_tools import get_moisture_data, get_weather_forecast

    print("\n[STEP 1] Acquiring Sensor Data...")
    moisture = get_moisture_data()
    weather = get_weather_forecast()

    return {"sensor_data": {"moisture_percent": moisture}, "weather_forecast": weather}


_cached_store = None

def rag_retrieval_node(state: AgentState):
    """
    Node to retrieve relevant agricultural research based on sensor data.
    """
    global _cached_store
    from src.rag.vector_store import AgriAgentVectorStore

    print("--- RAG RETRIEVAL ---")
    if _cached_store is None:
        _cached_store = AgriAgentVectorStore(persist_directory="data/chroma_db")

    sensor_data = state.get("sensor_data", {})
    # Handle both nested and flat moisture data formats
    moisture_val = sensor_data.get("moisture_percent")
    if moisture_val is None:
        moisture_val = 50 

    query = f"Cotton irrigation requirements and moisture thresholds at {moisture_val}% moisture."
    results = _cached_store.search(query, n_results=3)
    docs = results.get("documents", [[]])[0]

    return {"retrieved_knowledge": docs}


def reasoning_node(state: AgentState):
    """
    Expert System Reasoning Node: Analyzes Senses + RAG Knowledge + Weather.
    Optimized for low-end hardware (Zero-latency, High-precision).
    """
    import re

    print("--- AGENT REASONING (WEATHER-AWARE EXPERT SYSTEM) ---")

    sensor_data = state.get("sensor_data", {})
    moisture = sensor_data.get("moisture_percent")
    if moisture is None:
        moisture = 20.0  # Default fallback

    forecast = state.get("weather_forecast", {})
    knowledge = state.get("retrieved_knowledge", [])

    prompt = f"""
    [CROP SYSTEM ANALYSIS]
    CURRENT MOISTURE: {moisture}%
    WEATHER FORECAST: {forecast.get('rain_probability', 0)}% chance of rain, {forecast.get('temperature_celsius', 25)}°C.
    RESEARCH DATA: {knowledge}

    [INSTRUCTIONS]
    1. Evaluate if irrigation is needed based on field capacity and wilting point.
    2. Consider the weather forecast.
    3. State if irrigation is 'REQUIRED' or 'NOT REQUIRED' and why.
    """

    knowledge_text = " ".join(state["retrieved_knowledge"])

    # --- DYNAMIC KNOWLEDGE EXTRACTION ---
    fc_match = re.search(r"field capacity.*?(\d+)%", knowledge_text, re.IGNORECASE)
    wp_match = re.search(r"wilting point.*?(\d+)%", knowledge_text, re.IGNORECASE)

    fc = int(fc_match.group(1)) if fc_match else 25
    wp = int(wp_match.group(1)) if wp_match else 12

    # --- WEATHER-AWARE DECISION LOGIC ---
    rain_prob = forecast.get("rain_probability", 0)
    temp = forecast.get("temperature_celsius", 25)

    if rain_prob > 40:
        action = "WAIT"
        reason = f"Pre-emptive Wait: High rain probability ({rain_prob}%) detected. Saving water for natural precipitation."
    elif moisture <= wp:
        action = "IRRIGATE"
        reason = f"CRITICAL: Soil moisture ({moisture}%) reached the Wilting Point ({wp}%)."
    elif moisture < (fc * 0.8) and temp > 30:
        action = "IRRIGATE"
        reason = f"HIGH DEMAND: High temperature ({temp}°C) and moisture below 80% capacity ({moisture}% < {int(fc * 0.8)}%)."
    elif moisture < (fc * 0.7):
        action = "IRRIGATE"
        reason = f"STRESS ALERT: Moisture ({moisture}%) is below 70% of Field Capacity ({int(fc)}%)."
    else:
        action = "WAIT"
        reason = f"HEALTHY: Moisture ({moisture}%) is sufficient."

    print(f"   Agent Decision: {action} because {reason}")
    return {"decision": {"action": action, "reason": reason}}


def safety_critic_node(state: AgentState):
    """
    Node to verify the decision against hard-coded safety rules (e.g., rain forecast).
    """
    print("--- SAFETY CRITIC ---")
    decision = state["decision"]
    rain_prob = state["weather_forecast"].get("rain_probability", 0)

    if decision["action"] == "IRRIGATE" and rain_prob > 40:
        print("   REJECTED: High rain probability detected. Overriding irrigation decision.")
        return {
            "decision": {
                "action": "WAIT",
                "reason": f"Decision overridden by Safety Critic: {rain_prob}% rain forecast suggests waiting for natural precipitation.",
            }
        }

    return {}


def human_approval_node(state: AgentState):
    """
    Node to handle human-in-the-loop approval for critical actions.
    """
    print("--- HUMAN APPROVAL ---")
    # In a real LangGraph app, we use 'interrupt' here.
    # For this script, we'll simulate a passthrough.
    return {"human_approved": True}


# --- GRAPH CONSTRUCTION ---


def create_agri_agent_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("acquire_data", data_acquisition_node)
    workflow.add_node("retrieve_knowledge", rag_retrieval_node)
    workflow.add_node("reason", reasoning_node)
    workflow.add_node("safety_check", safety_critic_node)
    workflow.add_node("human_in_the_loop", human_approval_node)

    # Define Edges
    workflow.set_entry_point("acquire_data")
    workflow.add_edge("acquire_data", "retrieve_knowledge")
    workflow.add_edge("retrieve_knowledge", "reason")
    workflow.add_edge("reason", "safety_check")
    workflow.add_edge("safety_check", "human_in_the_loop")
    workflow.add_edge("human_in_the_loop", END)

    return workflow.compile()


if __name__ == "__main__":
    app = create_agri_agent_graph()
    print("Agri-Agent Graph successfully defined.")
