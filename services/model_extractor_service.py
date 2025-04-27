import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from google import genai
from huggingface_hub import HfApi

load_dotenv()


class ModelExtractor:
    def __init__(self):
        self.hf_api = HfApi()
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    def extract_from_huggingface(self, model_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(
                "https://huggingface.co/api/models",
                params={
                    "search": model_id,
                    "limit": 1,
                    "full": "True",
                    "config": "True",
                },
                headers={"Authorization": "Bearer " + os.getenv("HF_ACCESS_TOKEN")},
            )
            response_json = response.json()

            if not response_json:
                return None

            model_info = response_json[0]
            data = {
                "success": True,
                "name": model_info.get("id"),
                "developer": model_info.get("author"),
                "model_type": model_info.get("config", {}).get("model_type"),
                "architectures": model_info.get("config", {}).get("architectures"),
                "tags": model_info.get("tags"),
                "source_links": [
                    f"https://huggingface.co/{model_id}",
                ],
            }

            notes = self._analyze_with_gemini(data)
            data["notes"] = notes

            return data

        except Exception as e:
            print(f"Error extracting model info: {e}")
            return None

    def _determine_model_type(self, tags: list) -> str:
        type_mapping = {
            "text-generation": "LLM",
            "image-classification": "Vision",
            "audio": "Audio",
            "multimodal": "MultiModal",
        }

        for tag in tags:
            for key, value in type_mapping.items():
                if key in tag:
                    return value
        return "Other"

    def _analyze_with_gemini(self, model_card: str) -> str:
        prompt = """
        Analyze this model card and provide a concise summary focusing on:
        - Key capabilities
        - Performance metrics
        - Limitations
        - Use cases
        Format as a bullet-point list.
        
        Model Card:
        {model_card}
        """

        response = self.client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt.format(model_card=model_card)
        )
        return response.text

    def extract_from_github(self, repo_url: str) -> Optional[Dict[str, Any]]:
        pass
