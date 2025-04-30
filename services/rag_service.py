import os
from typing import Dict, Any, List
from google import genai
from dotenv import load_dotenv

load_dotenv()


class RAGService:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = "gemini-2.0-flash"

    def generate_model_insights(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        insights = {}

        tech_prompt = f"""
        Based on this ML model information:
        {model_data}
        
        Provide a technical analysis focusing on:
        1. Architecture strengths and potential limitations
        2. Computational requirements and optimization opportunities
        3. Integration considerations and deployment recommendations
        
        Format as bullet points, be specific and concise.
        """
        insights["technical_analysis"] = self._generate_content(tech_prompt)

        use_case_prompt = f"""
        Given this ML model's characteristics:
        {model_data}
        
        Suggest:
        1. Primary use cases
        2. Industry applications
        3. Potential innovative applications
        
        Format as bullet points, be specific and practical.
        """
        insights["use_cases"] = self._generate_content(use_case_prompt)

        rec_prompt = f"""
        Based on this model's profile:
        {model_data}
        
        Provide:
        1. Best practices for implementation
        2. Monitoring recommendations
        3. Performance optimization tips
        
        Format as bullet points, focus on actionable advice.
        """
        insights["recommendations"] = self._generate_content(rec_prompt)

        return insights

    def _prepare_context(self, model_data: Dict[str, Any]) -> str:
        context_parts = [
            f"Model Name: {model_data.get('name', 'N/A')}",
            f"Developer: {model_data.get('developer', 'N/A')}",
            f"Type: {model_data.get('model_type', 'N/A')}",
            f"Parameters: {model_data.get('parameters', 'N/A')}",
            f"Tags: {', '.join(model_data.get('tags', []))}",
            f"Notes: {model_data.get('notes', 'N/A')}",
        ]

        return "\n".join(context_parts)

    def _generate_content(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Error generating content: {e}")
            return "Error generating insights"

    def analyze_multiple_models(
        self, models_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        contexts = [model for model in models_data]
        combined_context = "\n\n".join(contexts)

        comparative_prompt = f"""
        Based on these ML models:
        {combined_context}
        
        Provide:
        1. Comparative analysis of their strengths and weaknesses
        2. Potential complementary use cases
        3. Integration opportunities
        
        Format as bullet points, focus on practical insights.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model, contents=comparative_prompt
            )
            return {"comparative_analysis": response.text}
        except Exception as e:
            print(f"Error in comparative analysis: {e}")
            return {"error": "Failed to generate comparative analysis"}
