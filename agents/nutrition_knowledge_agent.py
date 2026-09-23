"""
Nutrition Knowledge Agent
Fetches, retrieves, and summarizes nutritional data from USDA and other sources.
Uses RAG (Retrieval-Augmented Generation) to provide accurate food nutrition info.
"""
from typing import Dict, List, Optional
from utils.usda_client import USDAClient
from utils.groq_client import GroqClient
from config.settings import NUTRITION_KNOWLEDGE_AGENT


class NutritionKnowledgeAgent:
    """
    Agent responsible for fetching and summarizing nutritional knowledge.
    Combines USDA database retrieval with LLM-powered explanations.
    """

    SYSTEM_PROMPT = """You are a certified nutritionist and food scientist with deep knowledge 
of nutritional biochemistry, food composition, and dietary science. Your role is to provide 
accurate, evidence-based nutritional information. When given food data from the USDA database, 
synthesize it into clear, actionable insights. Always cite that data comes from USDA FoodData Central.
Be precise about nutrient values and explain their health significance."""

    def __init__(self):
        self.name = NUTRITION_KNOWLEDGE_AGENT
        self.usda_client = USDAClient()
        self.groq_client = GroqClient()
        self.knowledge_cache = {}  # Simple in-memory cache

    def get_food_nutrition(self, food_name: str) -> Dict:
        """
        Retrieve comprehensive nutritional data for a food item
        
        Args:
            food_name: Name of the food to look up
            
        Returns:
            Dict with nutritional data and AI summary
        """
        # Check cache first
        cache_key = food_name.lower().strip()
        if cache_key in self.knowledge_cache:
            return self.knowledge_cache[cache_key]

        # Fetch from USDA
        foods = self.usda_client.search_food(food_name, page_size=3)
        
        if not foods:
            return {
                "food": food_name,
                "status": "not_found",
                "message": f"No nutritional data found for '{food_name}' in USDA database",
                "nutrients": {}
            }

        primary_food = foods[0]
        
        # Generate AI summary
        prompt = f"""Based on this USDA nutritional data for '{food_name}':

Food: {primary_food['description']}
Category: {primary_food['category']}
Nutrients (per 100g): {primary_food['nutrients']}

Provide:
1. A brief nutritional profile summary (2-3 sentences)
2. Key health benefits
3. Any important warnings (high sodium, sugar, allergens if evident)
4. Best meal timing recommendation
5. Serving size suggestion

Keep it concise and practical."""

        ai_summary = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)
        
        result = {
            "food": food_name,
            "usda_description": primary_food["description"],
            "category": primary_food["category"],
            "nutrients": primary_food["nutrients"],
            "alternatives": [f["description"] for f in foods[1:]],
            "ai_summary": ai_summary,
            "data_source": "USDA FoodData Central"
        }
        
        # Cache the result
        self.knowledge_cache[cache_key] = result
        return result

    def compare_foods(self, food_list: List[str]) -> Dict:
        """
        Compare nutritional profiles of multiple foods
        
        Args:
            food_list: List of food names to compare
            
        Returns:
            Comparison dict with AI analysis
        """
        food_data = {}
        for food in food_list:
            foods = self.usda_client.search_food(food, page_size=1)
            if foods:
                food_data[food] = foods[0]

        if not food_data:
            return {"error": "No food data found for comparison"}

        # Build comparison prompt
        comparison_text = ""
        for food_name, data in food_data.items():
            comparison_text += f"\n{food_name}:\n"
            for nutrient, values in data.get("nutrients", {}).items():
                comparison_text += f"  {nutrient}: {values['value']} {values['unit']}\n"

        prompt = f"""Compare these foods nutritionally:
{comparison_text}

Provide:
1. Which is highest/lowest in key nutrients (protein, calories, fiber)
2. Which is better for weight loss
3. Which is better for muscle building
4. Which is best for heart health
5. Overall recommendation based on nutritional balance"""

        comparison_analysis = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "foods": food_data,
            "comparison_analysis": comparison_analysis
        }

    def get_nutrient_sources(self, nutrient: str) -> Dict:
        """
        Find best food sources for a specific nutrient
        
        Args:
            nutrient: Nutrient name (e.g., 'iron', 'vitamin c', 'protein')
            
        Returns:
            Dict with food sources and recommendations
        """
        # Search USDA for foods rich in the nutrient
        search_queries = {
            "protein": ["chicken breast", "eggs", "lentils", "greek yogurt"],
            "iron": ["spinach", "beef liver", "lentils", "tofu"],
            "calcium": ["milk", "cheese", "yogurt", "kale"],
            "vitamin_c": ["oranges", "bell peppers", "broccoli", "strawberries"],
            "fiber": ["oats", "black beans", "avocado", "quinoa"],
            "vitamin_d": ["salmon", "tuna", "egg yolk", "mushrooms"],
            "potassium": ["banana", "sweet potato", "spinach", "avocado"],
            "omega_3": ["salmon", "walnuts", "flaxseeds", "chia seeds"],
            "magnesium": ["almonds", "dark chocolate", "spinach", "pumpkin seeds"],
            "zinc": ["oysters", "beef", "pumpkin seeds", "chickpeas"]
        }

        # Find matching nutrient
        nutrient_lower = nutrient.lower().replace(" ", "_")
        foods_to_search = search_queries.get(nutrient_lower, [nutrient])

        foods_data = []
        for food in foods_to_search[:4]:
            result = self.usda_client.search_food(food, page_size=1)
            if result:
                foods_data.append({
                    "name": food,
                    "usda_data": result[0]
                })

        prompt = f"""What are the best dietary sources of {nutrient}?
        
Available USDA data: {[f['name'] for f in foods_data]}

Provide:
1. Top 8-10 food sources ranked by {nutrient} content
2. Recommended daily intake for adults
3. Signs of deficiency
4. Tips for better absorption
5. Foods that enhance vs block absorption"""

        sources_info = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "nutrient": nutrient,
            "top_sources": sources_info,
            "usda_foods": foods_data
        }

    def analyze_meal_nutrition(self, meal_items: List[Dict]) -> Dict:
        """
        Analyze nutritional content of a complete meal
        
        Args:
            meal_items: List of dicts with 'food' and 'amount_g' keys
            
        Returns:
            Complete meal nutrition analysis
        """
        total_nutrients = {}
        meal_details = []

        for item in meal_items:
            food_name = item.get("food", "")
            amount_g = item.get("amount_g", 100)

            foods = self.usda_client.search_food(food_name, page_size=1)
            if foods:
                food = foods[0]
                # Scale nutrients by amount
                scaled_nutrients = {}
                for nutrient, values in food.get("nutrients", {}).items():
                    scaled_value = (values["value"] * amount_g) / 100
                    scaled_nutrients[nutrient] = {
                        "value": round(scaled_value, 2),
                        "unit": values["unit"]
                    }
                    # Sum totals
                    if nutrient not in total_nutrients:
                        total_nutrients[nutrient] = {"value": 0, "unit": values["unit"]}
                    total_nutrients[nutrient]["value"] += scaled_value

                meal_details.append({
                    "food": food_name,
                    "amount_g": amount_g,
                    "nutrients": scaled_nutrients
                })

        # Round total nutrients
        for nutrient in total_nutrients:
            total_nutrients[nutrient]["value"] = round(total_nutrients[nutrient]["value"], 2)

        prompt = f"""Analyze this meal's nutrition:
Total nutrients: {total_nutrients}
Meal components: {[f"{item['food']} ({item['amount_g']}g)" for item in meal_details]}

Provide:
1. Overall nutritional assessment (balanced/unbalanced)
2. Macro breakdown percentage (protein/carb/fat)
3. Key strengths of this meal
4. Nutritional gaps or concerns
5. Simple modifications to improve the meal"""

        meal_analysis = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "meal_items": meal_details,
            "total_nutrients": total_nutrients,
            "meal_analysis": meal_analysis
        }

    def get_food_substitutes(self, food: str, reason: str = "general") -> Dict:
        """
        Suggest healthy substitutes for a food item
        
        Args:
            food: Food to substitute
            reason: Reason for substitution (allergy, diet, preference)
            
        Returns:
            Dict with substitution suggestions
        """
        prompt = f"""Suggest healthy substitutes for '{food}' because of: {reason}

Provide 5 alternatives with:
1. Substitute name
2. Why it's a good replacement
3. Nutritional comparison
4. How to use it as a replacement
5. Any adjustments needed in recipes"""

        substitutes = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "original_food": food,
            "substitution_reason": reason,
            "substitutes": substitutes
        }
