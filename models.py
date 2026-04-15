"""Load models to use them in the PAYADOR pipeline."""
from google import genai
from google.genai import types
import requests
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

load_dotenv()

def get_llm(model_name: str = "gemini-2.5-flash") -> object:

    google_models = ["gemini-2.5-flash"]

    model = None

    if model_name in google_models:
        model = GeminiModel(API_key="GOOGLE_API_KEY", model_name=model_name)

    return model

class GeminiModel():
    def __init__ (self, API_key:str, model_name:str = "gemini-2.5-flash") -> None:
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

        self.client = genai.Client(api_key=os.getenv(API_key))
        self.model_name = model_name
        self.temperature = 0.7

    # def build_decision_config(self):
    #     kwargs = {"temperature": self.temperature,"response_mime_type": "text/plain"}
    #     if hasattr(genai.types, "ThinkingConfig"):
    #         kwargs["thinking_config"] = genai.types.ThinkingConfig(thinking_level="MEDIUM")
    #     return genai.types.GenerateContentConfig(**kwargs)

    def build_decision_config(self):
        # Define the categories you want to suppress
        categories = [
            types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            types.HarmCategory.HARM_CATEGORY_HARASSMENT,
            types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        ]

        # Create the list of SafetySetting objects
        safety_settings = [
            types.SafetySetting(
                category=cat,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            ) for cat in categories
        ]

        kwargs = {
            "temperature": self.temperature,
            "response_mime_type": "text/plain",
            "safety_settings": safety_settings
        }

        # Include thinking config if supported
        if hasattr(types, "ThinkingConfig"):
            kwargs["thinking_config"] = types.ThinkingConfig(include_thoughts=True)

        return types.GenerateContentConfig(**kwargs)



    def prompt_model(self,system_msg: str, user_msg:str) -> str:
        """Prompt the Gemini model."""

        response = self.client.models.generate_content(
              model=self.model_name,
              contents=[system_msg + "\n\n" + user_msg],
              config=self.build_decision_config(),
          )

        return response.text



        # return self.model.generate_content(system_msg + "\n\n" + user_msg, safety_settings=self.safety_settings).text


class MovedObject(BaseModel):
    """Represents an object moved during world update."""
    name: str = Field(..., description="Name of the object being moved")
    destination: str = Field(..., description="Destination location, character name, or 'Inventory'")


class WorldUpdatePrediction(BaseModel):
    """Structured prediction of world state changes from LLM output."""
    moved_items: list[MovedObject] = Field(default_factory=list, description="List of objects that were moved")
    unblocked_locations: list[str] = Field(default_factory=list, description="List of previously blocked passages that are now accessible")
    player_movement: str | None = Field(default=None, description="New location if player moved, None otherwise")
    narration: str = Field(..., description="Narration describing the world changes")

    @field_validator('player_movement')
    @classmethod
    def validate_player_movement(cls, v: str | None) -> str | None:
        """Ensure player_movement is not an empty string."""
        if v == "":
            return None
        return v

    @field_validator('narration')
    @classmethod
    def validate_narration(cls, v: str) -> str:
        """Ensure narration is not empty."""
        if not v or not v.strip():
            raise ValueError("Narration cannot be empty")
        return v.strip()
