from agno.tools import tool
from agno.knowledge.arxiv import ArxivKnowledgeBase
from agno.vectordb.chroma import ChromaDb


class ArvixTool:
    def __init__(self, model_id: str):
        self.model_id = model_id

    @tool(
        name="get_arvix_information",
        description="Retrieve information from Arvix",
        show_result=True,
    )
    def get_arvix_information(self):
        knowledge_base = ArxivKnowledgeBase(
            queries=[self.model_id],
            vector_db=ChromaDb(
                collection_name="arxiv_documents", persist_directory="./arvix_documents"
            ),
        )

        knowledge_base.load(recreate=False)

        return knowledge_base
        # agent = Agent(
        #     knowledge=knowledge_base,
        #     search_knowledge=True,
        # )

        # agent.print_response(f"Tell me about {self.model_id}", markdown=True)
