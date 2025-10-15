import re
import json
from langchain_core.runnables import RunnablePassthrough
from modules.llm_gemini import GeminiLLM

gemini = GeminiLLM()

def weather_decision_node():
    def _evaluate(state):
        weather_data = state.get('weather_data')
        # print("\n---Evaluating Weather---")
        # print(weather_data)
        if "forecast" not in weather_data or not weather_data.get("forecast"):
            # print("Deciding...")
            return {"decision": "unknown", "reason": "No weather data available"}
        
        # print("---Weather Checker---")
        weather_forecast = weather_data.get('forecast')
        # print(weather_forecast)
        # print(weather_forecast[0])
        
        prompt = f"""
        The weather forecast of {weather_data.get('city')} is given as follows:
        {weather_forecast}
        
        Is this weather forecast good for planning a trip to {weather_data.get('city')}.
        Give the output in following json format
        decision: "favourable" or "unfavourable"
        reason: (if decision == unfavourable)
        """
        
        # print("---Weather Suitability---")
        weather_response = gemini.generate(prompt)
        
        decision_json = {"decision": "unknown", "reason": "Failed to parse LLM response"}

        # Use a more robust regex to find the JSON block
        match = re.search(r'\{[\s\S]*\}', weather_response)
        if match:
            try:
                # This will now UPDATE the variable if successful
                decision_json = json.loads(match.group(0))
            except json.JSONDecodeError:
                print("Error: Failed to decode JSON from LLM response.")
        
        print(f"---Weather Decision: {decision_json.get('decision')}---")
        # print("Output decision", decision_json)
        return decision_json

    return RunnablePassthrough.assign(decision=_evaluate)
