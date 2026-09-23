"""
Main Application Entry Point for Nutrition Agent
Interactive CLI interface for the AI-powered Nutrition Assistant
"""
import json
import sys
import os

# Ensure the nutrition-agent directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nutrition_orchestrator import NutritionAgentOrchestrator
from agents.nutrition_knowledge_agent import NutritionKnowledgeAgent
from agents.diet_recommendation_agent import DietRecommendationAgent
from agents.health_advisory_agent import HealthAdvisoryAgent
from agents.food_log_feedback_agent import FoodLogFeedbackAgent
from dashboard.nutrition_dashboard import (
    display_daily_dashboard,
    display_weekly_dashboard,
    display_meal_plan_dashboard,
    display_nutrition_info,
    generate_html_dashboard
)


def print_banner():
    """Print application banner"""
    print("\n" + "=" * 70)
    print("""
    ████████╗ ██████╗ ██╗   ██╗███████╗
       ██╔══╝██╔═══██╗██║   ██║██╔════╝
       ██║   ██║   ██║██║   ██║███████╗
       ██║   ██║   ██║██║   ██║╚════██║
       ██║   ╚██████╔╝╚██████╔╝███████║
       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
    🤖 AI-Powered Nutrition Agent | IBM Hackathon 2025
    """)
    print("=" * 70)
    print("Multi-Agent System: Knowledge | Diet | Health | Tracking")
    print("Powered by: GROQ (openai/gpt-oss-20b) + USDA FoodData Central")
    print("=" * 70 + "\n")


def demo_all_agents():
    """Run a comprehensive demo of all agents"""
    print_banner()
    print("🚀 Starting Nutrition Agent Demo...\n")

    orchestrator = NutritionAgentOrchestrator()

    # Sample user profile
    user_profile = {
        "name": "Priya Sharma",
        "age": 32,
        "gender": "female",
        "weight_kg": 65,
        "height_cm": 162,
        "activity_level": "moderate",
        "health_conditions": ["diabetes"],
        "allergies": ["peanuts"],
        "dietary_preferences": ["vegetarian"],
        "cultural_preferences": "Indian",
        "fitness_goals": "lose weight",
        "budget": "moderate",
        "cooking_skill": "intermediate",
        "meals_per_day": 3
    }

    user_id = "priya_sharma"

    print("=" * 70)
    print("🧠 AGENT 1: NUTRITION KNOWLEDGE AGENT (RAG + USDA)")
    print("=" * 70)
    print("Query: What are the nutritional facts for quinoa?\n")
    knowledge_agent = NutritionKnowledgeAgent()
    food_data = knowledge_agent.get_food_nutrition("quinoa")
    print(display_nutrition_info(food_data))

    print("\n" + "=" * 70)
    print("🥗 AGENT 2: DIET RECOMMENDATION AGENT")
    print("=" * 70)
    print("Generating personalized daily meal plan...\n")
    diet_agent = DietRecommendationAgent()
    meal_plan = diet_agent.generate_daily_meal_plan(user_profile)
    print(f"👤 User: {meal_plan['user_profile']['name']}")
    print(f"🔥 Target Calories: {meal_plan['user_profile']['target_calories']} kcal")
    print(f"📊 BMI: {meal_plan['user_profile']['bmi']} ({meal_plan['user_profile']['bmi_category']})")
    print("\n📋 PERSONALIZED MEAL PLAN:")
    print("-" * 70)
    print(meal_plan["daily_plan"][:800] + "..." if len(meal_plan["daily_plan"]) > 800 else meal_plan["daily_plan"])

    print("\n" + "=" * 70)
    print("🏥 AGENT 3: HEALTH ADVISORY AGENT")
    print("=" * 70)
    print("Getting diabetes-specific nutrition protocol...\n")
    health_agent = HealthAdvisoryAgent()
    health_advice = health_agent.get_chronic_disease_nutrition("diabetes", "moderate")
    print("📋 DIABETES NUTRITION PROTOCOL (excerpt):")
    print("-" * 70)
    protocol = health_advice.get("nutrition_protocol", "")
    print(protocol[:600] + "..." if len(protocol) > 600 else protocol)

    print("\n" + "=" * 70)
    print("📊 AGENT 4: FOOD LOG & FEEDBACK AGENT")
    print("=" * 70)
    print("Logging meals for the day...\n")
    log_agent = FoodLogFeedbackAgent()

    # Log some meals
    meals_to_log = [
        ("I had oatmeal with banana and milk for breakfast", "breakfast"),
        ("Lunch was lentil soup with brown rice and spinach salad", "lunch"),
        ("Snacked on an apple and walnuts", "snack"),
    ]

    for meal_text, meal_type in meals_to_log:
        print(f"📝 Logging {meal_type}: {meal_text}")
        log_result = log_agent.log_meal_text(user_id, meal_text, meal_type)
        cal = log_result.get("total_nutrients", {}).get("calories", 0)
        print(f"   ✅ Logged! Estimated: {cal:.0f} calories")
        print(f"   💬 Feedback: {log_result.get('feedback', '')[:100]}...")
        print()

    # Show daily summary
    print("\n📊 DAILY NUTRITION SUMMARY:")
    daily_summary = log_agent.get_daily_summary(user_id)
    print(display_daily_dashboard(daily_summary))

    # Generate HTML dashboard
    html_content = generate_html_dashboard(daily_summary)
    html_path = "nutrition_dashboard.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n🌐 HTML Dashboard saved to: {html_path}")

    print("\n" + "=" * 70)
    print("🤖 ORCHESTRATOR: INTELLIGENT CHAT")
    print("=" * 70)
    print("Testing multi-turn conversation routing...\n")

    test_queries = [
        "What are the health benefits of salmon?",
        "I just ate a bowl of pasta with tomato sauce for lunch",
        "What supplements should I take for diabetes management?",
    ]

    for query in test_queries:
        print(f"👤 User: {query}")
        response = orchestrator.chat(user_id, query, {"user_profile": user_profile})
        print(f"🤖 Agent ({response['agent_used']}): {response['response'][:200]}...")
        print()

    print("\n✅ Nutrition Agent Demo Complete!")
    print("All 4 agents successfully demonstrated.")
    print("=" * 70)


def interactive_chat():
    """Run interactive chat session"""
    print_banner()
    print("💬 Interactive Nutrition Chat")
    print("Type 'quit' to exit, 'demo' to run full demo, 'help' for commands\n")

    orchestrator = NutritionAgentOrchestrator()
    user_id = input("Enter your name (or press Enter for 'guest'): ").strip() or "guest"

    # Quick profile setup
    print(f"\nHi {user_id}! Let me set up a basic profile.")
    age = input("Age (or press Enter to skip): ").strip()
    goal = input("Primary goal (weight loss/muscle gain/maintain/health): ").strip() or "maintain"

    user_profile = {
        "name": user_id,
        "age": int(age) if age.isdigit() else 30,
        "gender": "not specified",
        "weight_kg": 70,
        "height_cm": 170,
        "activity_level": "moderate",
        "fitness_goals": goal
    }

    print(f"\n✅ Profile created! I'm ready to help with your nutrition. Ask me anything!")
    print("Example: 'What are calories in an apple?' | 'Give me a meal plan' | 'I ate pasta for lunch'\n")

    while True:
        try:
            user_input = input(f"\n{user_id}: ").strip()

            if not user_input:
                continue
            elif user_input.lower() == "quit":
                print("👋 Stay healthy! Goodbye!")
                break
            elif user_input.lower() == "demo":
                demo_all_agents()
            elif user_input.lower() == "help":
                print("""
📚 AVAILABLE COMMANDS:
  • Ask about any food: 'nutrition facts for avocado'
  • Log meals: 'I had scrambled eggs and toast for breakfast'
  • Get meal plans: 'give me a weekly meal plan'
  • Health advice: 'diet tips for diabetes'
  • Daily summary: 'show my daily summary'
  • Supplements: 'what supplements should I take?'
  • quit: Exit the application
  • demo: Run full agent demonstration
                """)
            else:
                print(f"\n🤔 Processing...")
                response = orchestrator.chat(user_id, user_input, {"user_profile": user_profile})
                print(f"\n🤖 NutritionBot [{response['agent_used']}]:")
                print("-" * 50)
                print(response["response"])
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Stay healthy!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}. Please try again.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_all_agents()
    else:
        interactive_chat()
