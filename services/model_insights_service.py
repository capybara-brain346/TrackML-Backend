import os
from typing import Dict, Any, List
from google import genai
from dotenv import load_dotenv
from models.models import ModelEntry, session

load_dotenv()


class ModelInsightsService:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = "gemini-2.0-flash"

    def generate_model_insights(
        self, model_data: Dict[str, Any], custom_prompt: str = None
    ) -> Dict[str, Any]:
        insights = {}

        if custom_prompt:
            context = self._prepare_context(model_data)
            custom_prompt_with_context = f"""
            Given this ML model context:
            {context}
            
            User Question/Prompt:
            {custom_prompt}
            
            Provide a detailed, specific, and actionable response focusing on the user's query.
            """
            insights["custom_analysis"] = self._generate_content(
                custom_prompt_with_context
            )
            return insights

        tech_prompt = f"""
        Based on this ML model context:
        {self._prepare_context(model_data)}
        
        Provide a comprehensive technical analysis covering:
        1. Architecture evaluation:
           - Core architectural components
           - Strengths and potential bottlenecks
           - Scalability considerations
        2. Performance optimization:
           - Resource utilization
           - Training and inference optimization opportunities
           - Hardware requirements and recommendations
        3. Implementation insights:
           - Best practices for deployment
           - Integration challenges and solutions
           - Monitoring and maintenance strategies
        
        Format as clear bullet points with specific, actionable insights.
        """
        insights["technical_analysis"] = self._generate_content(tech_prompt)

        use_case_prompt = f"""
        Based on this ML model context:
        {self._prepare_context(model_data)}
        
        Provide detailed insights on:
        1. Primary use cases:
           - Core applications with specific examples
           - Target problems and scenarios
           - Expected performance metrics
        2. Industry applications:
           - Sector-specific implementations
           - Real-world success scenarios
           - Industry-specific considerations
        3. Innovation potential:
           - Novel applications
           - Cross-domain opportunities
           - Future scaling possibilities
        
        Format as clear bullet points with practical, implementable suggestions.
        """
        insights["use_cases"] = self._generate_content(use_case_prompt)

        rec_prompt = f"""
        Based on this ML model context:
        {self._prepare_context(model_data)}
        
        Provide detailed recommendations covering:
        1. Implementation strategy:
           - Step-by-step deployment guide
           - Common pitfalls and solutions
           - Integration best practices
        2. Performance optimization:
           - Resource optimization techniques
           - Scaling strategies
           - Cost-efficiency improvements
        3. Monitoring and maintenance:
           - Key metrics to track
           - Performance indicators
           - Maintenance schedule and checklist
        
        Format as clear bullet points with specific, actionable steps.
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
            f"Workspace: {model_data.get('workspace_name', 'N/A')}",
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
        self, models_data: List[Dict[str, Any]], custom_prompt: str = None
    ) -> Dict[str, Any]:
        contexts = []
        for model in models_data:
            model_entry = session.query(ModelEntry).filter_by(id=model["id"]).first()
            if model_entry and model_entry.workspace:
                model["workspace_name"] = model_entry.workspace.name
            contexts.append(str(model))

        combined_context = "\n\n".join(contexts)

        if custom_prompt:
            prompt = f"""
            Based on these ML models:
            {combined_context}
            
            User Question/Prompt:
            {custom_prompt}
            
            Provide a detailed, specific, and actionable response focusing on the user's query while comparing the models.
            """
        else:
            prompt = f"""
            Based on these ML models:
            {combined_context}
            
            Provide:
            1. Comparative analysis of their strengths and weaknesses
            2. Potential complementary use cases
            3. Integration opportunities
            4. Recommendations for which model to use in different scenarios
            
            Format as bullet points, focus on practical insights and clear distinctions between the models.
            """

        try:
            response = self.client.models.generate_content(
                model=self.model, contents=prompt
            )
            return {"comparative_analysis": response.text}
        except Exception as e:
            print(f"Error in comparative analysis: {e}")
            return {"error": "Failed to generate comparative analysis"}
