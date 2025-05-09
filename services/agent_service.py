import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_groq import ChatGroq
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever

load_dotenv()


class AgentService:
    def __init__(self, model_id: str, model_links: Optional[List[str]] = None):
        self.model_id = model_id
        self.provided_links = model_links or []

        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5", model_kwargs={"device": "cpu"}
        )
        self.llm = ChatGroq(
            temperature=0.1,
            model_name="meta-llama/llama-4-scout-17b-16e-instruct",
            groq_api_key=os.getenv("GROQ_API_KEY"),
        )
        self.search_tool = DuckDuckGoSearchResults(output_format="list")

    def _search_web(self) -> List[str]:
        if not self.provided_links:
            try:
                search_results = self.search_tool.run(
                    f"{self.model_id} machine learning model technical details documentation"
                )

                self.provided_links = [result["link"] for result in search_results]

                if not self.provided_links:
                    raise ValueError("No valid links found in search results")

            except Exception as e:
                raise Exception(f"Error in web search: {str(e)}")

        return self.provided_links

    def _create_vectorstore(self, documents) -> FAISS:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        )
        splits = text_splitter.split_documents(documents)

        vectorstore = FAISS.from_documents(splits, self.embeddings)
        return vectorstore

    def _setup_rag_pipeline(self, vectorstore):
        base_retriever = vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 4}
        )

        multi_retriever = MultiQueryRetriever.from_llm(
            retriever=base_retriever, llm=self.llm
        )

        ensemble_retriever = EnsembleRetriever(
            retrievers=[base_retriever, multi_retriever], weights=[0.5, 0.5]
        )

        template = """You are an AI assistant tasked with providing accurate information about machine learning models.
        Use the following retrieved context to answer questions about the model {model_id}.
        
        Retrieved context: {context}
        
        Generate a comprehensive but concise summary that covers:
        1. Model architecture and key technical specifications
        2. Primary use cases and capabilities
        3. Performance characteristics and requirements
        4. Any notable limitations or considerations
        
        Focus on accuracy and cite specific details from the context. If information seems conflicting or uncertain, acknowledge this in your response.
        
        Summary:"""

        prompt = ChatPromptTemplate.from_template(template)

        chain = (
            {"context": ensemble_retriever, "model_id": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return chain

    def run_agent(self) -> str:
        try:
            links = self._search_web()

            loader = WebBaseLoader(links)
            documents = loader.load()

            vectorstore = self._create_vectorstore(documents)

            chain = self._setup_rag_pipeline(vectorstore)
            response = chain.invoke(self.model_id)

            return response

        except Exception as e:
            raise Exception(f"Error in RAG pipeline: {str(e)}")


if __name__ == "__main__":
    agent = AgentService(
        "meta-llama/Llama-3.2-1B",
        [
            "https://huggingface.co/meta-llama/Llama-3.2-1B",
            "https://ollama.com/library/llama3.2",
            "https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/",
        ],
    )
    print(agent.run_agent())
