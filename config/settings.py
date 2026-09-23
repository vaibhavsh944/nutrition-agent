"""
Configuration settings for the Nutrition Agent System
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys — set these in your .env file (see .env.example)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
USDA_API_KEY = os.getenv("USDA_API_KEY", "")

# Model Configuration
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-large-v3-turbo")

# GROQ API Base URL
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# USDA FoodData Central API
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"

# Agent Names
NUTRITION_KNOWLEDGE_AGENT = "NutritionKnowledgeAgent"
DIET_RECOMMENDATION_AGENT = "DietRecommendationAgent"
HEALTH_ADVISORY_AGENT = "HealthAdvisoryAgent"
FOOD_LOG_AGENT = "FoodLogFeedbackAgent"

# Meal categories
MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]

# Common health conditions for diet planning
HEALTH_CONDITIONS = [
    "diabetes", "hypertension", "heart_disease", "obesity",
    "celiac_disease", "lactose_intolerance", "kidney_disease",
    "thyroid_disorder", "anemia", "osteoporosis"
]

# Dietary preferences
DIETARY_PREFERENCES = [
    "vegetarian", "vegan", "gluten_free", "dairy_free",
    "keto", "paleo", "mediterranean", "low_carb", "low_fat",
    "high_protein", "kosher", "halal"
]

# Nutrient daily recommended values (DRI)
DAILY_RECOMMENDED_INTAKE = {
    "calories": 2000,
    "protein": 50,        # grams
    "carbohydrates": 275,  # grams
    "fat": 78,            # grams
    "fiber": 28,          # grams
    "sugar": 50,          # grams
    "sodium": 2300,       # mg
    "potassium": 4700,    # mg
    "calcium": 1000,      # mg
    "iron": 18,           # mg
    "vitamin_c": 90,      # mg
    "vitamin_d": 20,      # mcg
    "vitamin_b12": 2.4,   # mcg
    "folate": 400,        # mcg
    "magnesium": 420,     # mg
    "zinc": 11,           # mg
}
