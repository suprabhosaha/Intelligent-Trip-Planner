# 🌍 AI-Powered Personalized Travel Itinerary Planner

An **intelligent multi-agent travel assistant** that automatically plans your entire trip — from flights to weather-based itinerary generation — using **Google Gemini**, **LangGraph**, and **LangSmith** for orchestration and monitoring.  
The app provides **day-wise itineraries**, **real flight details**, and even suggests **alternate destinations** if the weather is unfavorable — all within an interactive **Streamlit dashboard**.

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
├── Airport Node → Calls Gemini to get IATA codes
├── Flight Node → Fetches flights both ways
├── Weather Node → Fetches destination forecast
├── Weather Decision → Checks if weather is good
├── Alternate Node → Suggests new destinations if bad
└── Itinerary Node → Generates day-wise plan
│
▼
Streamlit UI → Expandable divs, alternate buttons, regenerate
```

---

## 🧩 Project Structure

```
travel_itinerary_ai/
│
├── app.py                            # Streamlit UI
├── langgraph_flow.py                 # LangGraph pipeline & nodes
│
├── modules/
│   ├── flight_api.py                 # Flight fetching logic
│   ├── weather_api.py                # Weather forecast logic
│   ├── airport_lookup.py             # Gemini-powered airport code finder
│
├── utils/
│   ├── langsmith_init.py             # LangSmith integration
│
├── requirements.txt
└── README.md                         # This file
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<yourusername>/travel-itinerary-ai.git
cd travel-itinerary-ai
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
WEATHER_API_KEY=your_weather_api_key
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
From: Delhi
To: Paris
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
Day 1: Arrival, Eiffel Tower visit, local dining
Day 2: Louvre Museum, River Seine Cruise
...
```

---

### Step 3 — Handle Unfavorable Weather  
If the weather is bad, Gemini automatically suggests:
```
⚠️ Paris may have storms.
Try these alternatives:
→ Rome [Plan Rome]
→ Barcelona [Plan Barcelona]
```
Clicking **Plan Rome** automatically regenerates a new itinerary using LangGraph.

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
IIT Bhilai | AI & Machine Learning | Web Development  
Passionate about creating intelligent, user-friendly digital solutions.
