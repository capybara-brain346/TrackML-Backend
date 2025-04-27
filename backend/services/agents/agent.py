from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
from agno.models.ollama import Ollama
from agno.tools.crawl4ai import Crawl4aiTools

# from backend.services.agents.tools.huggingface_tool import get_huggingface_information
from backend.services.agents.tools.arvix_tool import ArvixTool

import os
from dotenv import load_dotenv
import requests
from agno.tools import tool

load_dotenv()


@tool(
    name="get_huggingface_information",
    description="Retrieve information from huggingface",
    show_result=True,
)
def get_huggingface_information(model_id: str) -> str:
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

        return str(data)

    except Exception as e:
        print(f"Error extracting model info: {e}")
        return None


class TrackMLAgent:
    def __init__(self, model_id: str, links: list):
        self.model_id = model_id
        self.links = links
        self.agent = Agent(
            # model=Groq(
            #     id="meta-llama/llama-4-scout-17b-16e-instruct",
            #     api_key=os.getenv("GROQ_API_KEY"),
            # ),
            model=Ollama(id="llama3.2:3b"),
            tools=[Crawl4aiTools(max_length=None), get_huggingface_information],
            markdown=True,
        )

    def run_agent(self):
        run: RunResponse = self.agent.run(
            f"Use all the tools you have to retrieve information about the given ML model and summarize it consisely.\nGiven model name: {self.model_id}\nLinks containing information about the model: {self.links}"
        )
        print(run.content)


if __name__ == "__main__":
    agent = TrackMLAgent(
        "meta-llama/Llama-3.2-1B",
        [
            "https://huggingface.co/meta-llama/Llama-3.2-1B",
            "https://ollama.com/library/llama3.2",
            "https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/",
        ],
    )
    agent.run_agent()
