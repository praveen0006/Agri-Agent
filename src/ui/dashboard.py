import streamlit as st
import sys
import os
import requests
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.tools.agent_tools import get_moisture_data, get_weather_forecast, get_camera_frame
from src.rag.ingest_papers import ingest_single_paper
from src.agent.agent_engine import create_agri_agent_graph
from langchain_core.messages import HumanMessage

# --- CONFIG ---
st.set_page_config(
    page_title="Agri-Agent: Precision Irrigation",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Look
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .reasoning-box {
        background-color: #e8f5e9;
        padding: 20px;
        border-left: 5px solid #2e7d32;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- APP LOGIC ---


def run_agent_workflow():
    """Executes the LangGraph agent and returns the final state."""
    app = create_agri_agent_graph()
    
    # Simple data fetch for decision
    moisture_data = get_moisture_data()
    weather_data = get_weather_forecast()

    initial_input = {
        "messages": [HumanMessage(content="Analyze my field condition.")],
        "sensor_data": moisture_data,
        "weather_forecast": weather_data,
        "retrieved_knowledge": [],
        "et_data": "",
        "decision": {},
        "human_approved": False
    }
    result = app.invoke(initial_input)
    return result


# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2613/2613862.png", width=100)
    st.title("Agri-Agent Gateway")
    st.write("System Status: **ONLINE**")
    st.write(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")

    st.divider()
    st.header("Connection Details")
    st.info("Arduino Mega: COM4 (Active)")
    st.info("API Status: OpenWeatherMap OK")

    if st.button("Refresh All Data"):
        st.rerun()

    st.divider()
    st.header("📚 Knowledge Base")
    uploaded_file = st.file_uploader("Upload Research PDF", type="pdf")
    if uploaded_file is not None:
        save_path = os.path.join("data", "papers", uploaded_file.name)
        if not os.path.exists(save_path):
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            with st.spinner(f"Ingesting {uploaded_file.name}..."):
                num_chunks = ingest_single_paper(save_path)
                st.success(f"Added {uploaded_file.name} ({num_chunks} chunks)")
        else:
            st.info(f"{uploaded_file.name} is already in the database.")

# --- MAIN DASHBOARD ---
st.title("🌿 Agri-Agent: Agentic Precision Irrigation")
st.markdown("### Real-Time Monitoring & AI Reasoning")

# Fetch fresh data
with st.spinner("Fetching latest field data..."):
    moisture_data = get_moisture_data()
    weather_data = get_weather_forecast()

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    m_val = moisture_data.get("moisture_percent") if moisture_data.get("moisture_percent") is not None else 0
    st.metric("Soil Moisture", f"{m_val}%", delta="-2% vs 1h ago", delta_color="inverse")
with col2:
    t_val = weather_data.get("temperature_celsius", 25)
    st.metric("Temperature", f"{t_val}°C")
with col3:
    h_val = weather_data.get("humidity_percent", 50)
    st.metric("Humidity", f"{h_val}%")
with col4:
    r_val = weather_data.get("rain_probability", 0)
    st.metric("Rain Prob.", f"{r_val}%", delta="High rain alert" if r_val > 40 else None)

st.divider()

# Brain Section
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("🧠 AI Reasoning & Research")

    if st.button("Run AI Decision Brain"):
        with st.spinner("Agent is analyzing sensors and RAG research papers..."):
            result = run_agent_workflow()

            # Display decision
            action = result["decision"]["action"]
            reason = result["decision"]["reason"]

            color = "#ffcdd2" if action == "IRRIGATE" else "#c8e6c9"
            border = "#d32f2f" if action == "IRRIGATE" else "#2e7d32"

            st.markdown(
                f"""
                <div style="background-color: {color}; padding: 20px; border-left: 5px solid {border}; border-radius: 5px;">
                    <h4 style="margin-top:0">AGENT DECISION: {action}</h4>
                    <p>{reason}</p>
                </div>
            """,
                unsafe_allow_html=True,
            )

            with st.expander("Show Detailed Agent Thoughts"):
                st.write("**Sensor Context:**", result["sensor_data"])
                st.write("**Weather Context:**", result["weather_forecast"])
                st.write("**RAG Knowledge Snippets:**")
                for doc in result["retrieved_knowledge"]:
                    st.info(doc[:300] + "...")

with col_right:
    st.subheader("📷 Field IP Camera Feed")
    # Real Camera Flow
    camera_url = os.getenv("IP_CAMERA_URL", "http://192.168.0.124:8080/video")
    st.write(get_camera_frame())

st.divider()

# --- RAG EXPLOROR (PHASE 7) ---
st.subheader("🔍 RAG Knowledge Explorer")
st.markdown("Search across all uploaded research papers to see exactly what the AI knows.")

search_query = st.text_input("Enter a query (e.g., 'cotton soil moisture thresholds')")
if st.button("Search Knowledge Base"):
    if search_query:
        from src.rag.vector_store import AgriAgentVectorStore

        store = AgriAgentVectorStore(persist_directory="data/chroma_db")
        with st.spinner("Searching scientific database..."):
            results = store.search(search_query, n_results=5)

            if results and results.get("documents") and results["documents"][0]:
                for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
                    with st.expander(
                        f"Result {i+1}: {meta.get('source', 'Unknown')} (Chunk {meta.get('chunk_index', 'N/A')})"
                    ):
                        st.markdown(doc)
            else:
                st.warning("No relevant results found for that query.")
    else:
        st.error("Please enter a search query.")

st.divider()

# Controls
st.subheader("🚜 Manual Override & Pump Controls")
c1, c2, c3 = st.columns(3)

with c1:
    duration = st.slider("Duration (seconds)", 1, 60, 10)
    if st.button("Manual Trigger Pump (Human Approval Required)"):
        st.warning("Sending manual activation request to ESP32...")
        # Actually trigger the tool
        from src.tools.agent_tools import trigger_pump

        resp = trigger_pump(duration)
        st.success(f"Response: {resp}")

with c2:
    st.write("")
    st.write("")
    st.button("Stop All Operations", type="primary")

st.markdown("---")
st.caption("Developed by Agri-Agent System Architecture (Phase 4 Prototype)")
