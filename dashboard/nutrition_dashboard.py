"""
Visualization Dashboard for Nutrition Agent
Interactive terminal/web dashboard for nutritional data visualization.
"""
import json
from datetime import date, timedelta
from typing import Dict, List
from config.settings import DAILY_RECOMMENDED_INTAKE


def generate_ascii_bar(value: float, max_value: float, width: int = 30, label: str = "") -> str:
    """Generate ASCII progress bar"""
    if max_value == 0:
        percentage = 0
    else:
        percentage = min(value / max_value, 1.5)  # Cap at 150%

    filled = int(percentage * width)
    bar = "█" * filled + "░" * (width - min(filled, width))
    pct = percentage * 100

    # Color coding via symbols
    status = "✅" if 80 <= pct <= 120 else ("⚠️" if pct < 80 else "🔴")
    return f"{status} {label:<18} [{bar}] {value:.1f}/{max_value} ({pct:.0f}%)"


def display_daily_dashboard(daily_summary: Dict) -> str:
    """
    Generate a comprehensive ASCII dashboard for daily nutrition
    
    Args:
        daily_summary: Output from FoodLogFeedbackAgent.get_daily_summary()
        
    Returns:
        Formatted dashboard string
    """
    lines = []
    today = daily_summary.get("date", str(date.today()))

    lines.append("=" * 70)
    lines.append(f"    🥗 NUTRITION DASHBOARD — {today}")
    lines.append("=" * 70)

    # Meals logged
    meals = daily_summary.get("meals_summary", [])
    lines.append(f"\n📋 MEALS LOGGED TODAY ({len(meals)} meals):")
    lines.append("-" * 40)
    for meal in meals:
        lines.append(f"  • {meal['type'].upper()}: {meal['description'][:50]}... ({meal['calories']:.0f} cal)")

    # Nutrient progress bars
    daily_totals = daily_summary.get("daily_totals", {})
    lines.append(f"\n📊 NUTRIENT PROGRESS (vs Daily Recommended Intake):")
    lines.append("-" * 70)

    key_nutrients = [
        ("calories", "Calories (kcal)"),
        ("protein", "Protein (g)"),
        ("carbohydrates", "Carbs (g)"),
        ("fat", "Fat (g)"),
        ("fiber", "Fiber (g)"),
        ("sodium", "Sodium (mg)"),
        ("calcium", "Calcium (mg)"),
        ("iron", "Iron (mg)"),
        ("vitamin_c", "Vitamin C (mg)"),
        ("potassium", "Potassium (mg)")
    ]

    for nutrient_key, label in key_nutrients:
        if nutrient_key in daily_totals:
            value = daily_totals[nutrient_key]
            target = DAILY_RECOMMENDED_INTAKE.get(nutrient_key, 100)
            lines.append(generate_ascii_bar(value, target, 25, label))

    # Deficiencies and excesses
    deficiencies = daily_summary.get("deficiencies", [])
    excesses = daily_summary.get("excesses", [])

    if deficiencies:
        lines.append(f"\n⚠️  DEFICIENCIES (< 70% DRI): {', '.join(deficiencies)}")
    if excesses:
        lines.append(f"🔴 EXCESSES (> 150% DRI): {', '.join(excesses)}")

    # AI Analysis
    analysis = daily_summary.get("daily_analysis", "")
    if analysis:
        lines.append(f"\n🤖 AI NUTRITIONAL ASSESSMENT:")
        lines.append("-" * 70)
        lines.append(analysis[:500] + "..." if len(analysis) > 500 else analysis)

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


def display_weekly_dashboard(weekly_data: Dict) -> str:
    """
    Generate weekly nutrition trend dashboard
    
    Args:
        weekly_data: Output from FoodLogFeedbackAgent.get_weekly_analysis()
        
    Returns:
        Formatted weekly dashboard string
    """
    lines = []

    lines.append("=" * 70)
    lines.append("    📈 WEEKLY NUTRITION TRENDS")
    lines.append("=" * 70)

    chart_data = weekly_data.get("chart_data", {})
    dates = chart_data.get("dates", [])
    calories = chart_data.get("calories", [])
    protein = chart_data.get("protein", [])

    lines.append(f"\n📅 Days Tracked: {weekly_data.get('days_logged', 0)}")
    lines.append(f"📆 Dates: {', '.join(dates) if dates else 'No data'}")

    # Weekly averages comparison
    weekly_averages = weekly_data.get("weekly_averages", {})
    if weekly_averages:
        lines.append(f"\n📊 WEEKLY AVERAGES vs RECOMMENDED:")
        lines.append("-" * 70)

        key_nutrients = [
            ("calories", "Calories (kcal)"),
            ("protein", "Protein (g)"),
            ("carbohydrates", "Carbs (g)"),
            ("fat", "Fat (g)"),
            ("fiber", "Fiber (g)")
        ]

        for nutrient_key, label in key_nutrients:
            if nutrient_key in weekly_averages:
                value = weekly_averages[nutrient_key]
                target = DAILY_RECOMMENDED_INTAKE.get(nutrient_key, 100)
                lines.append(generate_ascii_bar(value, target, 25, label))

    # Calorie trend chart
    if dates and calories:
        lines.append(f"\n📈 CALORIE TREND:")
        lines.append("-" * 40)
        max_cal = max(calories) if calories else 2000
        for i, (d, cal) in enumerate(zip(dates, calories)):
            bar_width = int((cal / max_cal) * 30) if max_cal else 0
            bar = "█" * bar_width
            lines.append(f"  {d}: {bar} {cal:.0f}")

    # Weekly analysis
    analysis = weekly_data.get("weekly_analysis", "")
    if analysis:
        lines.append(f"\n🤖 WEEKLY AI ANALYSIS:")
        lines.append("-" * 70)
        lines.append(analysis[:600] + "..." if len(analysis) > 600 else analysis)

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


def display_meal_plan_dashboard(meal_plan_data: Dict) -> str:
    """
    Display formatted meal plan from DietRecommendationAgent
    
    Args:
        meal_plan_data: Output from generate_weekly_meal_plan()
        
    Returns:
        Formatted meal plan display
    """
    lines = []

    profile = meal_plan_data.get("user_profile", {})
    lines.append("=" * 70)
    lines.append("    🍽️  PERSONALIZED MEAL PLAN")
    lines.append("=" * 70)

    lines.append(f"\n👤 Profile: {profile.get('name', 'User')}, "
                 f"Age: {profile.get('age')}, BMI: {profile.get('bmi')}")
    lines.append(f"🎯 Goal: {profile.get('fitness_goals', 'Maintain weight')}")
    lines.append(f"🔥 Daily Target: {profile.get('target_calories', 2000)} calories")

    conditions = profile.get("health_conditions", [])
    if conditions:
        lines.append(f"🏥 Health Conditions: {', '.join(conditions)}")

    notes = meal_plan_data.get("notes", [])
    if notes:
        lines.append(f"\n⚠️  IMPORTANT NOTES:")
        for note in notes:
            lines.append(f"  • {note}")

    lines.append(f"\n📅 MEAL PLAN:")
    lines.append("-" * 70)
    lines.append(meal_plan_data.get("meal_plan", "No meal plan generated"))

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


def display_nutrition_info(food_data: Dict) -> str:
    """
    Display nutritional information for a food item
    
    Args:
        food_data: Output from NutritionKnowledgeAgent.get_food_nutrition()
        
    Returns:
        Formatted nutrition display
    """
    lines = []

    lines.append("=" * 60)
    lines.append(f"    🥬 NUTRITION FACTS: {food_data.get('food', '').upper()}")
    lines.append("=" * 60)
    lines.append(f"USDA: {food_data.get('usda_description', 'N/A')}")
    lines.append(f"Category: {food_data.get('category', 'N/A')}")
    lines.append(f"Source: {food_data.get('data_source', 'USDA FoodData Central')}")

    nutrients = food_data.get("nutrients", {})
    if nutrients:
        lines.append("\n📊 NUTRIENTS (per 100g):")
        lines.append("-" * 40)
        for nutrient, data in nutrients.items():
            lines.append(f"  {nutrient:<20}: {data['value']:.2f} {data['unit']}")

    summary = food_data.get("ai_summary", "")
    if summary:
        lines.append("\n🤖 NUTRITIONIST'S NOTES:")
        lines.append("-" * 60)
        lines.append(summary)

    alternatives = food_data.get("alternatives", [])
    if alternatives:
        lines.append(f"\n📋 Similar Foods in USDA Database:")
        for alt in alternatives:
            lines.append(f"  • {alt}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def generate_html_dashboard(daily_summary: Dict) -> str:
    """
    Generate an HTML nutrition dashboard
    
    Args:
        daily_summary: Daily nutrition summary data
        
    Returns:
        HTML string for web display
    """
    daily_totals = daily_summary.get("daily_totals", {})
    dri_percentages = daily_summary.get("dri_percentages", {})
    meals = daily_summary.get("meals_summary", [])

    # Build nutrient chart data
    nutrients_display = [
        ("calories", "Calories", "#FF6384"),
        ("protein", "Protein", "#36A2EB"),
        ("carbohydrates", "Carbohydrates", "#FFCE56"),
        ("fat", "Fat", "#4BC0C0"),
        ("fiber", "Fiber", "#9966FF"),
        ("calcium", "Calcium", "#FF9F40"),
        ("iron", "Iron", "#C9CBCF"),
        ("vitamin_c", "Vitamin C", "#FF6384"),
    ]

    bars_html = ""
    for key, label, color in nutrients_display:
        if key in daily_totals:
            pct = min(dri_percentages.get(key, 0), 150)
            value = daily_totals[key]
            target = DAILY_RECOMMENDED_INTAKE.get(key, 100)
            status_color = "#28a745" if 80 <= pct <= 120 else ("#ffc107" if pct < 80 else "#dc3545")
            bars_html += f"""
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                    <span style="font-size: 13px; color: #333;">{label}</span>
                    <span style="font-size: 12px; color: #666;">{value:.1f} / {target} ({pct:.0f}%)</span>
                </div>
                <div style="background: #e9ecef; border-radius: 4px; height: 16px; overflow: hidden;">
                    <div style="background: {status_color}; width: {min(pct, 100):.1f}%; height: 100%; border-radius: 4px; transition: width 0.3s;"></div>
                </div>
            </div>"""

    meals_html = ""
    for meal in meals:
        meals_html += f"""<div style="padding: 8px; background: #f8f9fa; margin-bottom: 6px; border-radius: 6px; border-left: 3px solid #007bff;">
            <strong>{meal['type'].upper()}</strong>: {meal['description'][:60]}... 
            <span style="color: #666;">({meal['calories']:.0f} kcal)</span>
        </div>"""

    deficiencies = daily_summary.get("deficiencies", [])
    excesses = daily_summary.get("excesses", [])

    def_html = ""
    if deficiencies:
        def_html = f'<div style="background: #fff3cd; padding: 10px; border-radius: 6px; margin-top: 10px;">⚠️ <strong>Low:</strong> {", ".join(deficiencies)}</div>'
    if excesses:
        def_html += f'<div style="background: #f8d7da; padding: 10px; border-radius: 6px; margin-top: 6px;">🔴 <strong>Excess:</strong> {", ".join(excesses)}</div>'

    analysis = daily_summary.get("daily_analysis", "").replace("\n", "<br>")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nutrition Dashboard - {daily_summary.get('date', 'Today')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .card {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 12px; padding: 24px; margin-bottom: 20px; }}
        h1 {{ margin: 0; font-size: 24px; }}
        h2 {{ color: #333; font-size: 18px; margin-top: 0; }}
        .stat {{ display: inline-block; margin-right: 24px; text-align: center; }}
        .stat-value {{ font-size: 28px; font-weight: bold; }}
        .stat-label {{ font-size: 12px; opacity: 0.8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🥗 Nutrition Dashboard</h1>
            <p style="margin: 8px 0 16px;">Date: {daily_summary.get('date', 'Today')} | Meals Logged: {daily_summary.get('meals_logged', 0)}</p>
            <div>
                <div class="stat">
                    <div class="stat-value">{daily_totals.get('calories', 0):.0f}</div>
                    <div class="stat-label">Calories</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{daily_totals.get('protein', 0):.1f}g</div>
                    <div class="stat-label">Protein</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{daily_totals.get('carbohydrates', 0):.1f}g</div>
                    <div class="stat-label">Carbs</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{daily_totals.get('fat', 0):.1f}g</div>
                    <div class="stat-label">Fat</div>
                </div>
            </div>
        </div>
        <div class="card">
            <h2>📊 Nutrient Progress</h2>
            {bars_html}
            {def_html}
        </div>
        <div class="card">
            <h2>🍽️ Today's Meals</h2>
            {meals_html if meals_html else '<p style="color: #666;">No meals logged yet today.</p>'}
        </div>
        <div class="card">
            <h2>🤖 AI Nutritional Assessment</h2>
            <p style="line-height: 1.6; color: #444;">{analysis if analysis else 'Log your meals to receive personalized nutritional analysis.'}</p>
        </div>
    </div>
</body>
</html>"""
