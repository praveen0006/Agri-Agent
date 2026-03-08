import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.agent_engine import reasoning_node

def test_phase8_logic():
    print("🧪 Verifying Phase 8 Vision-Aware Reasoning Logic\n")
    
    # Mock base state
    base_state = {
        "sensor_data": {"moisture_percent": 15}, # Low moisture
        "weather_forecast": {"rain_probability": 0, "temp_c": 25},
        "retrieved_knowledge": ["Field capacity is 25% and wilting point is 12%."]
    }
    
    # Test case 1: Seedling (No multiplier)
    print("--- CASE 1: Germination & Seedling (Standard Demand) ---")
    state_seedling = base_state.copy()
    state_seedling["growth_stage"] = "Stage 2: Germination & Seedling"
    result_seedling = reasoning_node(state_seedling)
    print(f"Decision: {result_seedling['decision']['action']}")
    print(f"Reason: {result_seedling['decision']['reason']}\n")
    
    # Test case 2: Flowering (High demand, should trigger IRRIGATE earlier)
    print("--- CASE 2: Flowering & Boll Development (+20% Demand) ---")
    state_flowering = base_state.copy()
    state_flowering["growth_stage"] = "Stage 4: Flowering & Early Boll Development"
    # 15% moisture is > 12%(WP) but < 12*1.2 (14.4) for seedling.
    # Actually 15% is above 14.4% too. Let's try 14% moisture.
    state_flowering["sensor_data"]["moisture_percent"] = 14 
    result_flowering = reasoning_node(state_flowering)
    print(f"Decision: {result_flowering['decision']['action']}")
    print(f"Reason: {result_flowering['decision']['reason']}\n")

    # Test case 3: Maturity (Low demand, should WAIT longer)
    print("--- CASE 3: Late Season (-20% Demand) ---")
    state_late = base_state.copy()
    state_late["growth_stage"] = "Stage 6: Late Season (Boll Opening)"
    state_late["sensor_data"]["moisture_percent"] = 11 # Below usual 12% WP
    result_late = reasoning_node(state_late)
    print(f"Decision: {result_late['decision']['action']}")
    print(f"Reason: {result_late['decision']['reason']}\n")

if __name__ == "__main__":
    test_phase8_logic()
