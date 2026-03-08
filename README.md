# 🌿 Agri-Agent: Agentic Precision Irrigation

Agri-Agent is an AI-powered precision irrigation system designed to optimize water usage in agriculture. It leverages real-time soil moisture sensors, weather forecasts, and scientific research (via RAG) to make intelligent irrigation decisions.

## 🚀 Features
- **Real-Time Monitoring**: Live dashboard tracking soil moisture, temperature, humidity, and rain probability.
- **AI Reasoning Engine**: A LangGraph-powered agent that analyzes sensor data and weather forecasts to decide when to irrigate.
- **RAG Knowledge Base**: Uses Retrieval-Augmented Generation to incorporate scientific research papers into its decision-making process.
- **IoT Gateway**: Seamless integration with ESP32/Arduino hardware via a FastAPI gateway.
- **Safety Critic**: Built-in safety logic to prevent irrigation when high rain probability is detected.

## 🛠️ Tech Stack
- **Dashboard**: [Streamlit](https://streamlit.io/)
- **AI Orchestration**: [LangGraph](https://python.langchain.com/docs/langgraph) / [LangChain](https://python.langchain.com/)
- **API Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Models**: Llama-3.2 (via local inference or API)

## 📋 Prerequisites
- Python 3.9+
- [OpenWeatherMap API Key](https://openweathermap.org/api) (for weather data)
- (Optional) Hardware: Arduino Mega / ESP32 with capacitive soil moisture sensors.

## 🔌 Setup & Installation
1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd Agri-Agent
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   OPENWEATHERMAP_API_KEY=your_api_key_here
   APP_LAT=17.3850
   APP_LON=78.4867
   ```

## 🏃 Running the Application
1. **Start the IoT Gateway**:
   ```bash
   venv\Scripts\python -m uvicorn src.api.gateway:app --port 8000
   ```

2. **Launch the Dashboard**:
   ```bash
   venv\Scripts\streamlit run src/ui/dashboard.py
   ```

## 🏗️ Architecture
- `src/agent/`: Core reasoning engine and LangGraph definition.
- `src/api/`: FastAPI gateway for hardware communication.
- `src/rag/`: Document ingestion and vector store management.
- `src/tools/`: Integration tools for sensors, weather, and more.
- `src/ui/`: Streamlit dashboard implementation.

---
*Developed for Phase 4 Prototype: Agentic Precision Agriculture.*
