# 🌍 AI-Powered Personalized Travel Itinerary Planner

An **intelligent multi-agent travel assistant** that automatically plans your entire trip — from flights to weather-based itinerary generation — using **Google Gemini**, **LangGraph**, and **LangSmith** for orchestration and monitoring.  
The app provides **day-wise itineraries**, **real flight details**, and even suggests **alternate destinations** if the weather is unfavorable — all within an interactive **Streamlit dashboard**.

🔗 **Live Demo:** [Demo](https://intelligent-trip-planner-eq0w.onrender.com/) \
🔗 **GitHub Code:** [GitHub](https://github.com/suprabhosaha/Intelligent-Trip-Planner)
---

## 🚀 Features

✅ **Natural Language Trip Planning** — Users can type “Plan a 5-day trip to Paris from Delhi in November.” and the system handles the rest.  
✅ **LLM-driven Itinerary Generation** — Uses **Gemini** via LangGraph to generate day-wise detailed itineraries.  
✅ **Live Flight Search** — Fetches **real flight data** (source → destination & return).  
✅ **Live Weather Forecasting** — Integrates **weather APIs** to evaluate travel conditions.  
✅ **Automatic Alternate Destinations** — Suggests better destinations when unfavorable weather is detected.  
✅ **Interactive Frontend** — Built with **Streamlit**; day-wise itineraries are shown as **expandable divs**.  
✅ **Regeneration Buttons** — Users can click buttons beside alternate suggestions to regenerate a full plan instantly.  
✅ **LangSmith Monitoring** — Monitors every step in the graph execution pipeline.  
✅ **Robust Graph Orchestration** — All agents (flight, weather, itinerary, alternate) are connected using **LangGraph** with looping logic for iterative refinement.

---

## 🧠 System Architecture

```
User Input
│
▼
LangGraph Pipeline
│
├── Flight Node → Fetches flights both ways
├── Hotel Node → Fetches hotel data
├── Weather Node → Fetches destination forecast
├── Weather Decision → Checks if weather is favourable or not
├── Alternate Node → Suggests new destinations if weather is unfavourable
├── Itinerary Node → Generates day-wise plan
└── Summary Node → Generates a summary for the itinerary with additional to-dos
│
▼
Streamlit UI → Expandable divs, alternate buttons, regenerate
```

---

## 🧩 Project Structure

```
intelligent-trip-planner/
│
├── modules/
│   ├── flight_api.py                     # Flight data fetching from SerpAPI
│   ├── weather_api.py                    # Weather forecast data fetching from OpenWeatherAPI
│   ├── llm_gmeini.py                     # Gemini-powered LLM
|   ├── hotel_api.py                      # Hotel data fetching from SerpAPI
│
├── trip_graph/
│   ├── langgraph_flow.py                 # LangGraph pipeline
|   ├── nodes\
|   |    ├── flight_node.py               # Flight fetching Logic
|   |    ├── hotel_node.py                # Hotel fetching Logic
|   |    ├── weather_node.py              # Weather Forecast fetching Logic
|   |    ├── weather_decision_node.py     # Weather Decision Logic
|   |    ├── alternate_node.py            # Alternate Suggestion Logic
|   |    ├── planner_node.py              # Itinerary Logic
|   |    ├── summary_node.py              # Summarizer Logic
│
├── app.py                                # Streamlit UI
├── config.py                             # App configuration settings
├── requirements.txt                      # Python library requirements
└── README.md                             # This file
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/suprabhosaha/Intelligent-Trip-Planner.git
cd Intelligent-Trip-Planner/
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set environment variables

Create a `.env` file:

```
GEMINI_API_KEY=your_gemini_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=AI_Travel_Planner
OPENWEATHER_API_KEY=your_weather_api_key
FLIGHT_API_KEY=your_flight_api_key
```

---

## 💻 Running the Application

```bash
streamlit run app.py
```

Your Streamlit app will open at:
👉 http://localhost:8501

---

## 🖥️ User Interface Walkthrough

### Step 1 — Enter Your Trip Details  
Input:
```
From: Bangalore
To: Jaipur
Start Date: 2025-05-10
End Date: 2025-05-15
```

Click **Plan Trip**.

---

### Step 2 — View Your Day-wise Plan  
The app will generate:
- ✈️ Flight details  
- 🌦️ Weather conditions  
- 🗓️ Day-wise itinerary in collapsible cards  

Example:
```
Day 1: Arrival, Hawa Mahal visit, local dining
Day 2: Jal Mahal and Fort Exploration
...
```

---

### Step 3 — Handle Unfavorable Weather  
If the weather is bad, Gemini automatically suggests:
```
⚠️ Jaipur may have heat.
Try these alternatives:
→ Mysore [Plan Mysore]
→ Kochi [Plan Kochi]
```
Clicking **Plan Mysore** automatically regenerates a new itinerary using LangGraph.

---

### Step 4 — Monitoring with LangSmith  
Each run (including retries, alternates, and regenerations) can be monitored in **LangSmith dashboard**.

Go to:
👉 https://smith.langchain.com/

---

## 🔄 LangGraph Design (Simplified)

```python
graph = StateGraph(State)

graph.add_node("airport", airport_node)
graph.add_node("flight", flight_node)
graph.add_node("weather", weather_node)
graph.add_node("weather_decision", weather_decision_node)
graph.add_node("alternate", alternate_destination_node)
graph.add_node("itinerary", itinerary_node)

graph.add_edge("airport", "flight")
graph.add_edge("flight", "weather")
graph.add_conditional_edges(
    "weather_decision",
    lambda s: "alternate" if not s["weather_ok"] else "itinerary"
)
graph.add_edge("alternate", "weather")  # loop back for new destination
graph.add_edge("itinerary", END)
```

---

## 📊 Monitoring and Debugging

LangSmith tracks:
- Execution time per node  
- Model responses (Gemini)
- Failure traces (e.g., malformed JSON)
- User-triggered regeneration events  

If you see:
```
Failed to parse JSON from model response
```
Click the **Regenerate Plan** button in the Streamlit UI to retry with fallback prompts.

---

## 🛠️ Future Enhancements

- 🌐 Add multilingual support (translate itinerary)
- 🏨 Integrate hotel booking APIs
- 🚗 Add local transport suggestions
- 📍 Include interactive map view in Streamlit
- 🧭 Support voice-based itinerary generation

---

## 👨‍💻 Author

Developed by **Suprabho Saha**
