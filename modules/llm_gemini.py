from google import genai
from google.genai import types

from config import GEMINI_API_KEY

class GeminiLLM:
    """A wrapper class for the Google Gemini API."""

    def __init__(self, model_name="gemini-2.5-flash-lite"):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found. Ensure it's set in your environment or config.")
        
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = model_name

    def generate(self, prompt: str, use_google_search: bool = False) -> str:
        """
        Generates a response from the Gemini model.

        Args:
            prompt (str): The input prompt for the model.
            use_google_search (bool): If True, enables Google Search for grounding.

        Returns:
            str: The generated text response, or an error message.
        """
        # Define the tool for Google Search grounding if requested
        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config = types.GenerateContentConfig(tools=[grounding_tool])

        try:
            # Generate content with a single, clean API call
            response = self.client.models.generate_content(model=self.model, contents=prompt, config=config)
            
            # Safely return the generated text
            return response.text.strip()

        except Exception as e:
            # Handle any other exceptions during the API call
            print(f"An error occurred during content generation: {e}")
            return f"Error: Could not generate a response. Details: {e}"