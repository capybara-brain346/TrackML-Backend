import os
import requests
from agno.tools import tool


@tool(
    name="get_huggingface_information",
    description="Retrieve information from huggingface",
    show_result=True,
)
def get_huggingface_information(model_id: str):
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

        return data

    except Exception as e:
        print(f"Error extracting model info: {e}")
        return None
