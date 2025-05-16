import os
from typing import List, Optional, Any
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import (
    WebBaseLoader,
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_groq import ChatGroq
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.schema import Document
from utils.logging import logger

load_dotenv()


class AgentService:
    def __init__(
        self,
        model_id: str,
        model_links: Optional[List[str]] = None,
        doc_paths: Optional[List[str]] = None,
        use_scraping: bool = True,
        use_ddg: bool = False,
    ):
        self.model_id = model_id
        self.provided_links = model_links or []
        self.doc_paths = doc_paths or []
        self.use_scraping = use_scraping
        self.use_ddg = use_ddg

        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5", model_kwargs={"device": "cpu"}
        )

        self.llm = ChatGroq(
            temperature=0.1,
            model_name="meta-llama/llama-4-scout-17b-16e-instruct",
            groq_api_key=os.getenv("GROQ_API_KEY"),
        )
        self.search_tool = (
            DuckDuckGoSearchResults(output_format="list") if use_ddg else None
        )
        logger.info(f"AgentService initialization completed for {self.model_id}")

    def _scrape_webpage(self, url: str) -> str:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for script in soup(["script", "style", "meta", "link"]):
                script.decompose()

            text = soup.get_text(separator=" ", strip=True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = " ".join(lines)

            return text
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {str(e)}")
            return ""

    def _search_web(self) -> List[str]:
        logger.info(f"Starting web search for model: {self.model_id}")
        all_links = set(self.provided_links) if self.provided_links else set()

        if self.use_ddg:
            try:
                logger.debug("Performing DuckDuckGo search")
                search_results = self.search_tool.run(
                    f"{self.model_id} machine learning model technical details documentation"
                )
                search_links = {result["link"] for result in search_results}
                all_links.update(search_links)
                logger.info(f"Found {len(search_links)} links from DuckDuckGo search")
            except Exception as e:
                logger.warning(f"DuckDuckGo search failed: {str(e)}")

        if not all_links:
            if not self.provided_links:
                logger.warning(
                    "No links available - neither provided links nor DuckDuckGo search results"
                )
                raise ValueError("No links available for processing")
            logger.info("Using only provided links")

        return list(all_links)

    def _process_web_content(self, links: List[str]) -> List[Document]:
        documents = []
        for url in links:
            try:
                if self.use_scraping:
                    content = self._scrape_webpage(url)
                    if content:
                        doc = Document(page_content=content, metadata={"source": url})
                        documents.append(doc)
                else:
                    web_loader = WebBaseLoader([url])
                    documents.extend(web_loader.load())
                logger.debug(f"Successfully processed content from {url}")
            except Exception as e:
                logger.error(f"Failed to process content from {url}: {str(e)}")
        return documents

    def _load_local_documents(self) -> List[Any]:
        logger.info(f"Loading local documents from {len(self.doc_paths)} paths")
        documents = []
        for path in self.doc_paths:
            try:
                ext = os.path.splitext(path)[1].lower()
                logger.debug(f"Processing document: {path} with extension {ext}")
                if ext == ".pdf":
                    loader = PyPDFLoader(path)
                elif ext in [".doc", ".docx"]:
                    loader = UnstructuredWordDocumentLoader(path)
                else:
                    logger.warning(f"Unsupported file extension: {ext} for file {path}")
                    continue
                loaded_docs = loader.load()
                documents.extend(loaded_docs)
                logger.debug(
                    f"Successfully loaded {len(loaded_docs)} pages from {path}"
                )
            except Exception as e:
                logger.error(f"Failed to load document {path}: {str(e)}")
        logger.info(f"Total documents loaded: {len(documents)}")
        return documents

    def _create_vectorstore(self, documents) -> FAISS:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        )
        splits = text_splitter.split_documents(documents)

        vectorstore = FAISS.from_documents(splits, self.embeddings)
        logger.info("Vector store creation completed")
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

        logger.info("RAG pipeline setup completed")
        return chain

    def run_agent(self) -> str:
        logger.info(f"Starting agent run for model: {self.model_id}")
        try:
            links = self._search_web()
            documents = []

            if links:
                logger.debug(f"Loading web documents from {len(links)} links")
                documents.extend(self._process_web_content(links))

            local_docs = self._load_local_documents()
            documents.extend(local_docs)

            if not documents:
                logger.error("No documents were successfully loaded")
                raise ValueError("No documents were successfully loaded")

            vectorstore = self._create_vectorstore(documents)
            chain = self._setup_rag_pipeline(vectorstore)

            logger.debug("Executing RAG chain")
            response = chain.invoke(self.model_id)
            logger.info("Agent run completed successfully")

            return response

        except Exception as e:
            logger.error(f"Agent run failed: {str(e)}")
            raise Exception(f"Error in RAG pipeline: {str(e)}")


if __name__ == "__main__":
    logger.info("Starting agent service test run")
    agent = AgentService(
        "meta-llama/Llama-3.2-1B",
        [
            "https://huggingface.co/meta-llama/Llama-3.2-1B",
            "https://ollama.com/library/llama3.2",
            "https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/",
        ],
        [
            "local_docs/model_specs.pdf",
            "local_docs/technical_overview.docx",
        ],
    )
    print(agent.run_agent())
