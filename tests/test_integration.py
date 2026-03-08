import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.agent_tools import get_moisture_data, get_weather_forecast, calculate_evapotranspiration
from src.rag.vector_store import AgriAgentVectorStore


def run_integration_test():
    print("🚀 Starting Agri-Agent Integration Test (Phase 1 + Phase 2)\n")
    print("=" * 60)
    print("STEP 1: ACQUIRING REAL-TIME SENSOR DATA")
    print("=" * 60)

    # 1. Get Senses
    moisture = get_moisture_data()
    weather = get_weather_forecast()

    if "error" in moisture:
        print(f"❌ Sensor Error: {moisture['error']}")
        return

    m_val = moisture["moisture_percent"]
    print(f"📡 Current Soil Moisture: {m_val}%")
    print(f"☁️  Weather Forecast: {weather['temperature_celsius']}°C, {weather['rain_probability']}% chance of rain")

    # 2. Calculate ET
    et_val = calculate_evapotranspiration(
        weather["temperature_celsius"], weather["humidity_percent"], weather["wind_speed_ms"]
    )
    print(f"💧 {et_val}")

    print("\n" + "=" * 60)
    print("STEP 2: RETRIEVING SCIENTIFIC KNOWLEDGE (RAG)")
    print("=" * 60)

    # 3. Search RAG for context
    store = AgriAgentVectorStore(persist_directory="data/chroma_db")
    query = f"What is the irrigation threshold for cotton when soil moisture is {m_val}%?"
    print(f"🔍 Querying Brain: '{query}'")

    results = store.search(query, n_results=2)

    if results and results.get("documents"):
        for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
            source = meta.get("source", "Unknown Paper")
            print(f"\n📄 KNOWLEDGE {i+1} (Source: {source}):")
            # Show a relevant snippet
            print(f'   "{doc[:300]}..."')
    else:
        print("⚠️ No relevant research found in database.")

    print("\n" + "=" * 60)
    print("STEP 3: MOCK REASONING SUMMARY")
    print("=" * 60)

    # Simple logic to show how the agent WILL think in Phase 3
    if m_val < 20:
        status = "CRITICAL: Soil is too dry."
    elif m_val < 35:
        status = "WARNING: Soil moisture is dropping."
    else:
        status = "OK: Soil moisture is healthy."

    decision = "WAIT" if weather["rain_probability"] > 50 else "IRRIGATE (If needed)"

    print(f"🤖 Agent Status: {status}")
    print(f"📢 Potential Decision: {decision} (Rain forecast: {weather['rain_probability']}%)")
    print("\n✅ Integration Test Passed: Brain and Senses are connected.")


if __name__ == "__main__":
    run_integration_test()
