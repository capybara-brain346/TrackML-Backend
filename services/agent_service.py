import os
from dotenv import load_dotenv
from agno.agent import Agent, RunResponse
from agno.models.ollama import Ollama
from agno.tools.crawl4ai import Crawl4aiTools
from agno.models.groq import Groq
# from services.huggingface_tool import get_huggingface_information

load_dotenv()


class AgentService:
    def __init__(self, model_id: str, model_links: list):
        self.model_id = model_id
        self.links = model_links
        self.agent = Agent(
            model=Groq(
                id="meta-llama/llama-4-scout-17b-16e-instruct",
                api_key=os.getenv("GROQ_API_KEY"),
            ),
            # model=Ollama(id="llama3.2:3b"),
            tools=[Crawl4aiTools(max_length=None)],
            markdown=False,
        )

    def run_agent(self):
        run: RunResponse = self.agent.run(
            f"You are an AI agent with access to the Crew4AI web search tool.\n\nTask: Use the tool to search for reliable and relevant information about the following machine learning model:\n\nModel Name: {self.model_id}\nProvided Links: {self.links}\n\nInstructions:\n1. Use the web search tool to retrieve detailed and credible information.\n2. Cross-reference the provided links if necessary.\n3. Summarize the model’s key attributes, including its purpose, architecture, capabilities, and known applications.\n\nOutput: Return a concise and informative summary suitable for someone evaluating the model’s utility."
        )

        return run.content


if __name__ == "__main__":
    agent = AgentService(
        "meta-llama/Llama-3.2-1B",
        [
            "https://huggingface.co/meta-llama/Llama-3.2-1B",
            "https://ollama.com/library/llama3.2",
            "https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/",
        ],
    )
    agent.run_agent()
