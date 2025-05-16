import os
from google import genai
import numpy as np
from typing import List, Dict
from models.models import ModelEntry, session
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from utils.logging import logger

load_dotenv()


class SemanticSearchService:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.embeddings = "models/text-embedding-004"
        logger.info("SemanticSearchService initialized successfully")

    def _get_embedding(self, text: str) -> List[float]:
        if not text or not isinstance(text, str):
            logger.warning(f"Invalid text input for embedding: {text}")
            return []
        try:
            response = self.client.models.embed_content(
                model=self.embeddings,
                contents=text,
            )
            logger.debug("Embedding generated successfully")
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return []

    def _get_model_embedding(self, model: ModelEntry) -> List[float]:
        model_text = f"{model.name} {model.notes or ''} {model.model_type or ''} {model.developer or ''} {model.license or ''} {model.version or ''} {' '.join(model.tags or [])} {' '.join(model.source_links or [])}"
        return self._get_embedding(model_text)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        query_embedding = self._get_embedding(query)
        logger.debug(f"Query embedding generated with length: {len(query_embedding)}")

        models = session.query(ModelEntry).all()
        if not models:
            logger.warning("No models found in database")
            return []

        model_embeddings = []
        successful_models = []
        for model in models:
            logger.debug(f"Processing model: {model.name}")
            model_embedding = self._get_model_embedding(model)
            if model_embedding:
                model_embeddings.append(model_embedding)
                successful_models.append(model)
            else:
                logger.warning(f"Failed to generate embedding for model: {model.name}")

        if not model_embeddings:
            logger.warning("No valid model embeddings were generated")
            return []

        similarities = cosine_similarity([query_embedding], model_embeddings)[0]

        model_scores = list(zip(successful_models, similarities))
        model_scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for model, score in model_scores[:top_k]:
            model_dict = model.to_dict()
            model_dict["relevance_score"] = float(score)
            results.append(model_dict)

        logger.info(f"Search completed. Returning {len(results)} results")
        return results
