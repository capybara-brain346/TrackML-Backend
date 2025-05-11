import os
import google.generativeai as genai
from google import genai
import numpy as np
from typing import List, Dict
from models.models import ModelEntry, session
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()


class SemanticSearchService:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.embeddings = "models/text-embedding-004"

    def _get_embedding(self, text: str) -> List[float]:
        response = self.client.models.embed_content(
            model=self.embeddings,
            contents=text,
        )
        return response.embedding

    def _get_model_embedding(self, model: ModelEntry) -> List[float]:
        model_text = f"{model.name} {model.description} {model.model_type} {' '.join(model.tags)}"
        return self._get_embedding(model_text)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        query_embedding = self._get_embedding(query)

        models = session.query(ModelEntry).all()
        if not models:
            return []

        model_embeddings = []
        for model in models:
            model_embedding = self._get_model_embedding(model)
            model_embeddings.append(model_embedding)

        similarities = cosine_similarity([query_embedding], model_embeddings)[0]

        model_scores = list(zip(models, similarities))
        model_scores.sort(key=lambda x: x[1], reverse=True)

        results = []
        for model, score in model_scores[:top_k]:
            model_dict = model.to_dict()
            model_dict["relevance_score"] = float(score)
            results.append(model_dict)

        return results
