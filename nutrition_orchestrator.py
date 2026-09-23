"""
Nutrition Agent Orchestrator - Main Entry Point
Coordinates all sub-agents for a unified AI-powered nutrition assistant.
"""
import json
from typing import Dict, List, Optional
from agents.nutrition_knowledge_agent import NutritionKnowledgeAgent
from agents.diet_recommendation_agent import DietRecommendationAgent
from agents.health_advisory_agent import HealthAdvisoryAgent
from agents.food_log_feedback_agent import FoodLogFeedbackAgent
from utils.groq_client import GroqClient
from config.settings import GROQ_MODEL


class NutritionAgentOrchestrator:
    """
    Master orchestrator that coordinates all nutrition sub-agents.
    Routes user queries to the appropriate specialist agent.
    """

    ROUTER_PROMPT = """You are a nutrition assistant router. Classify the user's intent into one of:
1. "nutrition_knowledge" - asking about food nutrition facts, comparing foods, nutrients
2. "diet_recommendation" - requesting meal plans, diet advice, meal suggestions
3. "health_advisory" - asking about health conditions, supplements, preventive health
4. "food_log" - logging meals, tracking intake, checking daily progress
5. "general" - general nutrition conversation, greetings, unclear queries

Return ONLY the category name, nothing else."""

    def __init__(self):
        self.knowledge_agent = NutritionKnowledgeAgent()
        self.diet_agent = DietRecommendationAgent()
        self.health_agent = HealthAdvisoryAgent()
        self.food_log_agent = FoodLogFeedbackAgent()
        self.groq_client = GroqClient()
        self.conversation_history = {}

    def chat(self, user_id: str, message: str, context: Optional[Dict] = None) -> Dict:
        """
        Main chat interface - routes messages to appropriate agent
        
        Args:
            user_id: Unique user identifier
            message: User's message
            context: Optional context (user profile, etc.)
            
        Returns:
            Agent response with metadata
        """
        # Initialize conversation history for user
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        # Add user message to history
        self.conversation_history[user_id].append({
            "role": "user",
            "content": message
        })

        # Route to appropriate agent
        intent = self._classify_intent(message)

        response_data = self._route_to_agent(intent, message, user_id, context or {})

        # Add response to history
        self.conversation_history[user_id].append({
            "role": "assistant",
            "content": response_data.get("response", "")
        })

        return {
            "user_id": user_id,
            "intent": intent,
            "message": message,
            "response": response_data.get("response", ""),
            "data": response_data.get("data", {}),
            "agent_used": response_data.get("agent", "general")
        }

    def _classify_intent(self, message: str) -> str:
        """Classify user intent to route to correct agent"""
        try:
            intent = self.groq_client.simple_query(
                f"User message: '{message}'",
                self.ROUTER_PROMPT
            ).strip().lower()

            valid_intents = ["nutrition_knowledge", "diet_recommendation", "health_advisory", "food_log", "general"]
            return intent if intent in valid_intents else "general"
        except Exception:
            return "general"

    def _route_to_agent(self, intent: str, message: str, user_id: str, context: Dict) -> Dict:
        """Route to the appropriate agent based on intent"""

        if intent == "nutrition_knowledge":
            return self._handle_nutrition_knowledge(message, context)
        elif intent == "diet_recommendation":
            return self._handle_diet_recommendation(message, user_id, context)
        elif intent == "health_advisory":
            return self._handle_health_advisory(message, context)
        elif intent == "food_log":
            return self._handle_food_log(message, user_id, context)
        else:
            return self._handle_general(message, user_id)

    def _handle_nutrition_knowledge(self, message: str, context: Dict) -> Dict:
        """Handle nutrition knowledge queries"""
        # Extract food name from message
        extract_prompt = f"""From this message: "{message}"
Extract the food item being asked about.
Return ONLY the food name, nothing else. If multiple foods, separate with comma."""

        food_name = self.groq_client.simple_query(extract_prompt).strip()

        if "," in food_name:
            # Multiple foods - comparison
            foods = [f.strip() for f in food_name.split(",")]
            data = self.knowledge_agent.compare_foods(foods)
            response = data.get("comparison_analysis", "")
        else:
            data = self.knowledge_agent.get_food_nutrition(food_name)
            response = data.get("ai_summary", "")

        return {"response": response, "data": data, "agent": "NutritionKnowledgeAgent"}

    def _handle_diet_recommendation(self, message: str, user_id: str, context: Dict) -> Dict:
        """Handle diet recommendation requests"""
        user_profile = context.get("user_profile", {
            "name": user_id,
            "age": 30,
            "gender": "not specified",
            "weight_kg": 70,
            "height_cm": 170,
            "activity_level": "moderate",
            "fitness_goals": "maintain weight"
        })

        # Check if it's a weekly plan or daily
        if any(word in message.lower() for word in ["weekly", "week", "7 day", "7-day"]):
            data = self.diet_agent.generate_weekly_meal_plan(user_profile)
            response = data.get("meal_plan", "")
        elif any(word in message.lower() for word in ["condition", "diabetes", "hypertension", "heart"]):
            # Extract condition
            condition_prompt = f"Extract the health condition from: '{message}'. Return ONLY the condition name."
            condition = self.groq_client.simple_query(condition_prompt).strip()
            data = self.diet_agent.get_diet_plan_for_condition(condition)
            response = data.get("specialized_plan", "")
        else:
            data = self.diet_agent.generate_daily_meal_plan(user_profile)
            response = data.get("daily_plan", "")

        return {"response": response, "data": data, "agent": "DietRecommendationAgent"}

    def _handle_health_advisory(self, message: str, context: Dict) -> Dict:
        """Handle health advisory queries"""
        user_profile = context.get("user_profile", {})

        if any(word in message.lower() for word in ["supplement", "vitamin", "mineral"]):
            data = self.health_agent.get_supplement_advice(user_profile)
            response = data.get("supplement_recommendations", "")
        elif any(word in message.lower() for word in ["risk", "prevent", "prevention"]):
            age = user_profile.get("age", 35)
            gender = user_profile.get("gender", "adult")
            data = self.health_agent.get_preventive_nutrition_guide(age, gender)
            response = data.get("preventive_guide", "")
        elif any(word in message.lower() for word in ["gut", "digestive", "bloating", "ibs"]):
            data = self.health_agent.get_gut_health_protocol()
            response = data.get("gut_health_protocol", "")
        elif any(word in message.lower() for word in ["sport", "athlete", "workout", "exercise", "training"]):
            sport = "general fitness"
            data = self.health_agent.get_sports_nutrition_guide(sport, "in_season", user_profile)
            response = data.get("sports_nutrition_guide", "")
        else:
            # General health advisory
            condition_prompt = f"What health condition or topic is asked about: '{message}'? Return concise answer."
            condition = self.groq_client.simple_query(condition_prompt).strip()
            data = self.health_agent.get_chronic_disease_nutrition(condition)
            response = data.get("nutrition_protocol", "")

        return {"response": response, "data": data, "agent": "HealthAdvisoryAgent"}

    def _handle_food_log(self, message: str, user_id: str, context: Dict) -> Dict:
        """Handle food logging and tracking"""
        if any(word in message.lower() for word in ["summary", "today", "daily", "how much", "intake"]):
            data = self.food_log_agent.get_daily_summary(user_id)
            response = data.get("daily_analysis", "No meals logged today yet. Start logging by saying 'I ate [food]'!")
        elif any(word in message.lower() for word in ["weekly", "week", "trend", "progress"]):
            data = self.food_log_agent.get_weekly_analysis(user_id)
            response = data.get("weekly_analysis", "No weekly data available yet.")
        else:
            # Log the meal
            meal_type = "meal"
            for mt in ["breakfast", "lunch", "dinner", "snack"]:
                if mt in message.lower():
                    meal_type = mt
                    break

            data = self.food_log_agent.log_meal_text(user_id, message, meal_type)
            response = f"✅ Logged your {meal_type}!\n\n" + data.get("feedback", "")

        return {"response": response, "data": data, "agent": "FoodLogFeedbackAgent"}

    def _handle_general(self, message: str, user_id: str) -> Dict:
        """Handle general nutrition questions"""
        # Use conversation history for context
        history = self.conversation_history.get(user_id, [])[-6:]  # Last 3 exchanges

        system_prompt = """You are a knowledgeable, friendly AI nutrition assistant. 
You help users with all aspects of nutrition, diet, and healthy eating. 
Provide helpful, evidence-based answers. Be warm and encouraging."""

        response = self.groq_client.chat_completion(
            history,
            system_prompt=system_prompt
        )

        return {"response": response, "data": {}, "agent": "GeneralNutritionAssistant"}

    def get_comprehensive_profile_analysis(self, user_profile: Dict) -> Dict:
        """
        Run all agents to provide comprehensive nutritional analysis
        
        Args:
            user_profile: Complete user profile
            
        Returns:
            Comprehensive multi-agent analysis
        """
        results = {}

        # Diet recommendation
        diet_data = self.diet_agent.generate_daily_meal_plan(user_profile)
        results["personalized_meal_plan"] = diet_data.get("daily_plan", "")

        # Health advisory
        age = user_profile.get("age", 30)
        gender = user_profile.get("gender", "adult")
        conditions = user_profile.get("health_conditions", [])
        risk_factors = conditions + [user_profile.get("activity_level", "")]

        health_data = self.health_agent.get_preventive_nutrition_guide(age, gender, risk_factors)
        results["preventive_health_guide"] = health_data.get("preventive_guide", "")

        # Add user profile analysis
        results["user_profile"] = self.diet_agent.create_user_profile(user_profile)
        results["generated_by_agents"] = [
            "DietRecommendationAgent",
            "HealthAdvisoryAgent"
        ]

        return results
