"""Load models to use them as a narrator and a common-sense oracle in the PAYADOR pipeline."""
import google.generativeai as genai


class GeminiModel():
    def __init__ (self, api_key_file:str) -> None:
        """"Initialize the Gemini model using an API key."""
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_DANGEROUS",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
        genai.configure(api_key=get_api_key(api_key_file))
        self.model = genai.GenerativeModel("gemini-pro")

    def prompt_model(self,prompt: str) -> str:
        """Prompt the Gemini model."""
        return self.model.generate_content(prompt, safety_settings=self.safety_settings).text

def get_api_key(path: str) -> str:
    """Load an API key from path."""
    key = ""
    with open(path) as f:
        key = f.readline()
    return key