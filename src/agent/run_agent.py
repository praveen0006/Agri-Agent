import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agent.agent_engine import create_agri_agent_graph
from langchain_core.messages import HumanMessage


def main():
    print("--- Starting Agri-Agent Autonomous Workflow ---\n")

    # 1. Compile the Graph
    agent_app = create_agri_agent_graph()

    # 2. Initial State
    initial_input = {
        "messages": [HumanMessage(content="Is irrigation required for my cotton field right now?")],
        "sensor_data": {},
        "weather_forecast": {},
        "retrieved_knowledge": [],
        "et_data": "",
        "decision": {},
        "human_approved": False,
    }

    # 3. Run the Graph
    print("Executing LangGraph nodes...")
    # result = agent_app.invoke(initial_input)
    # To see the stream of progress:
    result = None
    for output in agent_app.stream(initial_input):
        # The output of stream is a dict with node name as key
        # we update result with the last state
        result = output

    # In LangGraph stream, if we want the final state, we can just look at the last value
    # But invoke() is cleaner for simple testing
    result = agent_app.invoke(initial_input)

    print("\n" + "=" * 60)
    print("AGENT FINAL DECISION")
    print("=" * 60)
    print(f"Action: {result['decision']['action']}")
    print(f"Reason: {result['decision']['reason']}")
    print("=" * 60)

    if result["decision"]["action"] == "IRRIGATE":
        print("\n[SYSTEM] Awaiting human approval to trigger the pump relay...")
    else:
        print("\n[SYSTEM] No action required based on current sensor and research data.")


if __name__ == "__main__":
    main()
