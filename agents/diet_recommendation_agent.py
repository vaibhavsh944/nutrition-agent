"""
Diet Recommendation Agent
Generates personalized meal plans based on user profile, goals, and preferences.
"""
import json
from typing import Dict, List, Optional
from utils.groq_client import GroqClient
from config.settings import DIET_RECOMMENDATION_AGENT, DIETARY_PREFERENCES, HEALTH_CONDITIONS


class DietRecommendationAgent:
    """
    Agent that creates personalized diet plans and meal recommendations
    based on individual user profiles, health conditions, and goals.
    """

    SYSTEM_PROMPT = """You are an expert registered dietitian (RD) and nutrition coach with 15+ years 
of clinical experience. You specialize in personalized nutrition planning, medical nutrition therapy, 
and sports dietetics. Create practical, culturally sensitive, and scientifically-backed meal plans. 
Always consider food safety, realistic preparation times, and budget constraints. 
Format meal plans clearly with specific foods, portions, and preparation tips.
Provide calorie counts and macronutrient breakdowns for all recommendations."""

    def __init__(self):
        self.name = DIET_RECOMMENDATION_AGENT
        self.groq_client = GroqClient()
        self.user_profiles = {}  # Store user profiles

    def create_user_profile(self, user_data: Dict) -> Dict:
        """
        Create or update a user profile for personalization
        
        Args:
            user_data: Dict containing user information
            
        Returns:
            Validated and enriched user profile
        """
        profile = {
            "name": user_data.get("name", "User"),
            "age": user_data.get("age", 30),
            "gender": user_data.get("gender", "not specified"),
            "weight_kg": user_data.get("weight_kg", 70),
            "height_cm": user_data.get("height_cm", 170),
            "activity_level": user_data.get("activity_level", "moderate"),
            "health_conditions": user_data.get("health_conditions", []),
            "allergies": user_data.get("allergies", []),
            "dietary_preferences": user_data.get("dietary_preferences", []),
            "cultural_preferences": user_data.get("cultural_preferences", ""),
            "fitness_goals": user_data.get("fitness_goals", "maintain weight"),
            "budget": user_data.get("budget", "moderate"),
            "cooking_skill": user_data.get("cooking_skill", "intermediate"),
            "meals_per_day": user_data.get("meals_per_day", 3)
        }

        # Calculate BMI and TDEE
        bmi = profile["weight_kg"] / ((profile["height_cm"] / 100) ** 2)
        profile["bmi"] = round(bmi, 1)
        profile["bmi_category"] = self._get_bmi_category(bmi)

        # Calculate Total Daily Energy Expenditure (TDEE)
        tdee = self._calculate_tdee(profile)
        profile["tdee_calories"] = tdee

        # Adjust for goal
        if "lose weight" in profile["fitness_goals"].lower() or "weight loss" in profile["fitness_goals"].lower():
            profile["target_calories"] = max(1200, tdee - 500)
        elif "gain weight" in profile["fitness_goals"].lower() or "muscle" in profile["fitness_goals"].lower():
            profile["target_calories"] = tdee + 300
        else:
            profile["target_calories"] = tdee

        user_id = profile["name"].lower().replace(" ", "_")
        self.user_profiles[user_id] = profile
        return profile

    def generate_weekly_meal_plan(self, user_profile: Dict) -> Dict:
        """
        Generate a complete 7-day personalized meal plan
        
        Args:
            user_profile: User profile dict with health info
            
        Returns:
            Complete weekly meal plan with nutrition details
        """
        profile = self.create_user_profile(user_profile)

        prompt = f"""Create a detailed 7-day meal plan for:

**User Profile:**
- Name: {profile['name']}
- Age: {profile['age']}, Gender: {profile['gender']}
- Weight: {profile['weight_kg']}kg, Height: {profile['height_cm']}cm
- BMI: {profile['bmi']} ({profile['bmi_category']})
- Activity Level: {profile['activity_level']}
- Target Calories: {profile['target_calories']} kcal/day
- Health Conditions: {', '.join(profile['health_conditions']) if profile['health_conditions'] else 'None'}
- Allergies: {', '.join(profile['allergies']) if profile['allergies'] else 'None'}
- Dietary Preferences: {', '.join(profile['dietary_preferences']) if profile['dietary_preferences'] else 'None specified'}
- Cultural Preferences: {profile['cultural_preferences'] or 'No restriction'}
- Fitness Goal: {profile['fitness_goals']}
- Budget: {profile['budget']}
- Cooking Skill: {profile['cooking_skill']}

**Requirements:**
1. 7 complete days (Monday–Sunday)
2. {profile['meals_per_day']} meals per day + optional snacks
3. Each meal: food items, portion sizes, and calorie count
4. Daily totals: calories, protein (g), carbs (g), fat (g), fiber (g)
5. Variety across days — no repeating same meal twice
6. Include quick prep tips (under 30 mins where possible)
7. Grocery list for the week at the end

Format each day clearly with meal names and specific quantities."""

        meal_plan_text = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "user_profile": profile,
            "meal_plan": meal_plan_text,
            "weekly_calories": profile["target_calories"] * 7,
            "notes": self._get_dietary_notes(profile)
        }

    def generate_daily_meal_plan(self, user_profile: Dict, date: str = "today") -> Dict:
        """
        Generate a single day meal plan
        
        Args:
            user_profile: User profile
            date: Target date or day name
            
        Returns:
            Single day meal plan
        """
        profile = self.create_user_profile(user_profile)

        prompt = f"""Create a detailed single-day meal plan for {date}:

User: {profile['age']}yr {profile['gender']}, {profile['activity_level']} activity
Target: {profile['target_calories']} kcal
Conditions: {profile['health_conditions'] or 'None'}
Preferences: {profile['dietary_preferences'] or 'None'}
Allergies: {profile['allergies'] or 'None'}
Goal: {profile['fitness_goals']}

Include:
- Breakfast (with time suggestion)
- Morning Snack (if appropriate)
- Lunch
- Afternoon Snack
- Dinner
- Evening Snack (if appropriate)

For EACH meal specify:
✓ Exact food items and portions (grams/cups/pieces)
✓ Calorie count
✓ Protein/Carb/Fat breakdown
✓ Prep time
✓ Simple preparation method

End with daily totals and a hydration reminder."""

        daily_plan = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "date": date,
            "user_profile": profile,
            "daily_plan": daily_plan,
            "target_calories": profile["target_calories"]
        }

    def recommend_meal(
        self,
        meal_type: str,
        user_profile: Dict,
        available_ingredients: Optional[List[str]] = None
    ) -> Dict:
        """
        Recommend a specific meal based on available ingredients and preferences
        
        Args:
            meal_type: breakfast/lunch/dinner/snack
            user_profile: User profile
            available_ingredients: Optional list of available ingredients
            
        Returns:
            Meal recommendation with recipe
        """
        profile = self.create_user_profile(user_profile)

        ingredients_text = ""
        if available_ingredients:
            ingredients_text = f"\nAvailable ingredients: {', '.join(available_ingredients)}"

        prompt = f"""Recommend a {meal_type} meal for:
- Age: {profile['age']}, Goal: {profile['fitness_goals']}
- Conditions: {profile['health_conditions'] or 'None'}
- Preferences: {profile['dietary_preferences'] or 'None'}
- Allergies: {profile['allergies'] or 'None'}
- Target meal calories: ~{profile['target_calories'] // profile['meals_per_day']} kcal
{ingredients_text}

Provide:
1. Recipe name
2. Ingredients with exact quantities
3. Step-by-step preparation (5 steps max)
4. Nutrition facts (calories, protein, carbs, fat, fiber)
5. Why this meal is beneficial for their profile
6. Possible variations or substitutions"""

        recommendation = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "meal_type": meal_type,
            "recommendation": recommendation,
            "estimated_calories": profile["target_calories"] // profile["meals_per_day"]
        }

    def get_diet_plan_for_condition(self, condition: str, user_age: int = 40, user_gender: str = "adult") -> Dict:
        """
        Get specialized diet plan for a specific health condition
        
        Args:
            condition: Health condition (e.g., diabetes, hypertension)
            user_age: User's age
            user_gender: User's gender
            
        Returns:
            Condition-specific diet plan
        """
        condition_prompts = {
            "diabetes": "Type 2 Diabetes management with low glycemic index focus",
            "hypertension": "DASH diet for blood pressure management",
            "heart_disease": "Heart-healthy Mediterranean diet approach",
            "obesity": "Calorie-controlled, high-fiber, low-fat plan",
            "kidney_disease": "Low potassium, low phosphorus, controlled protein",
            "celiac_disease": "Strict gluten-free diet plan",
            "lactose_intolerance": "Dairy-free calcium-rich alternatives",
            "anemia": "Iron-rich foods with vitamin C for absorption",
            "osteoporosis": "Calcium and vitamin D rich foods",
            "thyroid_disorder": "Thyroid-friendly diet avoiding goitrogens"
        }

        condition_context = condition_prompts.get(
            condition.lower().replace(" ", "_"),
            f"Health-optimized diet for {condition}"
        )

        prompt = f"""Create a specialized 7-day diet plan for a {user_age}-year-old {user_gender} with {condition}.
        
Focus: {condition_context}

Include:
1. Foods to EAT (with specific examples and portions)
2. Foods to STRICTLY AVOID and why
3. Foods to LIMIT (with safe quantities)
4. 7-day sample meal plan (breakfast, lunch, dinner, snacks)
5. Key nutritional targets (specific numbers)
6. Supplement recommendations if needed
7. Lifestyle tips that complement the diet
8. Warning signs to watch for
9. When to consult a doctor about diet changes

Make it practical and easy to follow for someone managing this condition daily."""

        diet_plan = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "condition": condition,
            "diet_focus": condition_context,
            "specialized_plan": diet_plan
        }

    def generate_family_meal_plan(self, family_members: List[Dict]) -> Dict:
        """
        Generate a meal plan that accommodates entire family's needs
        
        Args:
            family_members: List of family member profiles
            
        Returns:
            Family-friendly meal plan
        """
        members_summary = []
        for member in family_members:
            summary = f"{member.get('name', 'Member')}: {member.get('age')}yr, "
            summary += f"Conditions: {member.get('health_conditions', 'None')}, "
            summary += f"Preferences: {member.get('dietary_preferences', 'None')}"
            members_summary.append(summary)

        prompt = f"""Create a 7-day family meal plan accommodating all members:

Family Members:
{chr(10).join(f'- {m}' for m in members_summary)}

Requirements:
1. Meals that work for everyone (identify modifications for specific members)
2. Kid-friendly options if children are included
3. Budget-conscious and practical
4. Batch cooking suggestions for busy days
5. Weekly grocery list
6. Note any individual modifications needed (e.g., 'diabetic member: skip rice, use cauliflower rice')
7. Include calorie ranges per meal

Focus on simple, wholesome family meals that everyone can enjoy."""

        family_plan = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "family_members": family_members,
            "family_meal_plan": family_plan
        }

    def _calculate_tdee(self, profile: Dict) -> int:
        """Calculate Total Daily Energy Expenditure using Mifflin-St Jeor equation"""
        weight = profile["weight_kg"]
        height = profile["height_cm"]
        age = profile["age"]
        gender = profile["gender"].lower()

        # BMR using Mifflin-St Jeor
        if gender in ["male", "m"]:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161

        # Activity multipliers
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }

        multiplier = activity_multipliers.get(
            profile["activity_level"].lower().replace(" ", "_"), 1.55
        )

        return round(bmr * multiplier)

    def _get_bmi_category(self, bmi: float) -> str:
        """Return BMI category string"""
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    def _get_dietary_notes(self, profile: Dict) -> List[str]:
        """Generate important dietary notes based on profile"""
        notes = []

        if profile["bmi"] > 30:
            notes.append("Focus on portion control and reducing refined carbohydrates")
        if profile["bmi"] < 18.5:
            notes.append("Increase caloric intake with nutrient-dense foods")
        if "diabetes" in profile["health_conditions"]:
            notes.append("Monitor blood sugar; choose low glycemic index foods")
        if "hypertension" in profile["health_conditions"]:
            notes.append("Limit sodium to <1500mg/day; follow DASH principles")
        if profile["activity_level"] in ["active", "very_active"]:
            notes.append("Ensure adequate protein (1.6-2.2g/kg body weight) for recovery")
        if profile["age"] > 60:
            notes.append("Prioritize calcium, vitamin D, and B12 for healthy aging")

        return notes
