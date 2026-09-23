"""
Food Log & Feedback Agent
Handles meal logging, nutritional analysis, and progress tracking.
"""
import json
from datetime import datetime, date
from typing import Dict, List, Optional
from utils.groq_client import GroqClient
from utils.usda_client import USDAClient
from config.settings import FOOD_LOG_AGENT, DAILY_RECOMMENDED_INTAKE


class FoodLogFeedbackAgent:
    """
    Agent for tracking daily food intake, analyzing nutrition,
    and providing real-time feedback on dietary habits.
    """

    SYSTEM_PROMPT = """You are a supportive nutrition coach and dietetic technician specializing 
in dietary assessment and behavior change. Your role is to analyze food logs, provide constructive 
feedback, identify nutritional gaps, and motivate users to achieve their dietary goals. 
Be encouraging yet honest about dietary shortcomings. Use positive reinforcement while providing 
concrete, actionable advice. Always contextualize feedback within the user's goals and lifestyle."""

    def __init__(self):
        self.name = FOOD_LOG_AGENT
        self.groq_client = GroqClient()
        self.usda_client = USDAClient()
        self.food_logs = {}  # {user_id: {date: [meal_entries]}}

    def log_meal_text(self, user_id: str, meal_text: str, meal_type: str = "meal") -> Dict:
        """
        Log a meal from text description and analyze nutrition
        
        Args:
            user_id: User identifier
            meal_text: Natural language meal description
            meal_type: breakfast/lunch/dinner/snack
            
        Returns:
            Meal log entry with nutritional analysis
        """
        today = str(date.today())

        # Parse meal using LLM to extract food items and quantities
        parse_prompt = f"""Parse this meal log into structured food items:
"{meal_text}"

Extract each food item and estimate quantity in grams.
Return a JSON array: [{{"food": "food name", "amount_g": estimated_grams, "cooked": true/false}}]
Be reasonable with portion estimates based on typical serving sizes.
If no quantity is mentioned, use standard single serving."""

        try:
            parsed_items = self.groq_client.structured_query(
                parse_prompt,
                "You are a food parsing expert. Return only valid JSON arrays."
            )
            if not isinstance(parsed_items, list):
                parsed_items = [{"food": meal_text, "amount_g": 150}]
        except Exception:
            parsed_items = [{"food": meal_text, "amount_g": 150}]

        # Fetch nutritional data for parsed items
        nutrition_data = {}
        total_nutrients = {k: 0 for k in DAILY_RECOMMENDED_INTAKE.keys()}

        for item in parsed_items:
            foods = self.usda_client.search_food(item["food"], page_size=1)
            if foods:
                food = foods[0]
                amount = item.get("amount_g", 100)
                item_nutrients = {}
                for nutrient, values in food.get("nutrients", {}).items():
                    scaled = (values["value"] * amount) / 100
                    item_nutrients[nutrient] = round(scaled, 2)
                    if nutrient in total_nutrients:
                        total_nutrients[nutrient] += scaled
                nutrition_data[item["food"]] = item_nutrients

        # Round totals
        total_nutrients = {k: round(v, 2) for k, v in total_nutrients.items()}

        # Create log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "meal_type": meal_type,
            "original_text": meal_text,
            "parsed_items": parsed_items,
            "nutrition": nutrition_data,
            "total_nutrients": total_nutrients
        }

        # Store in food log
        if user_id not in self.food_logs:
            self.food_logs[user_id] = {}
        if today not in self.food_logs[user_id]:
            self.food_logs[user_id][today] = []

        self.food_logs[user_id][today].append(log_entry)

        # Generate immediate feedback
        feedback = self._generate_meal_feedback(meal_text, total_nutrients, meal_type)
        log_entry["feedback"] = feedback

        return log_entry

    def log_meal_voice(self, user_id: str, audio_file_path: str, meal_type: str = "meal") -> Dict:
        """
        Log a meal from voice recording
        
        Args:
            user_id: User identifier
            audio_file_path: Path to audio file
            meal_type: Type of meal
            
        Returns:
            Meal log entry with transcription and nutritional analysis
        """
        try:
            # Transcribe audio using Whisper
            transcribed_text = self.groq_client.transcribe_audio(audio_file_path)
            if not transcribed_text:
                return {"error": "Could not transcribe audio. Please try again."}

            # Process transcribed text as meal log
            result = self.log_meal_text(user_id, transcribed_text, meal_type)
            result["transcribed_from_voice"] = True
            result["transcription"] = transcribed_text
            return result
        except Exception as e:
            return {"error": f"Voice logging failed: {str(e)}"}

    def get_daily_summary(self, user_id: str, target_date: str = None) -> Dict:
        """
        Get comprehensive daily nutritional summary
        
        Args:
            user_id: User identifier
            target_date: Date string (YYYY-MM-DD) or None for today
            
        Returns:
            Daily nutrition summary with analysis
        """
        if not target_date:
            target_date = str(date.today())

        user_logs = self.food_logs.get(user_id, {})
        day_logs = user_logs.get(target_date, [])

        if not day_logs:
            return {
                "date": target_date,
                "message": "No meals logged for this date",
                "total_nutrients": {},
                "meals_logged": 0
            }

        # Aggregate all nutrients for the day
        daily_totals = {k: 0.0 for k in DAILY_RECOMMENDED_INTAKE.keys()}
        meals_summary = []

        for log_entry in day_logs:
            meal_totals = log_entry.get("total_nutrients", {})
            for nutrient, value in meal_totals.items():
                if nutrient in daily_totals:
                    daily_totals[nutrient] += value

            meals_summary.append({
                "type": log_entry["meal_type"],
                "time": log_entry["timestamp"],
                "description": log_entry["original_text"],
                "calories": meal_totals.get("calories", 0)
            })

        # Round totals
        daily_totals = {k: round(v, 2) for k, v in daily_totals.items()}

        # Calculate percentage of DRI met
        dri_percentages = {}
        for nutrient, value in daily_totals.items():
            dri = DAILY_RECOMMENDED_INTAKE.get(nutrient, 0)
            if dri > 0:
                dri_percentages[nutrient] = round((value / dri) * 100, 1)

        # Generate AI analysis
        analysis = self._generate_daily_analysis(daily_totals, dri_percentages, meals_summary)

        return {
            "date": target_date,
            "meals_logged": len(day_logs),
            "meals_summary": meals_summary,
            "daily_totals": daily_totals,
            "dri_percentages": dri_percentages,
            "daily_analysis": analysis,
            "deficiencies": [k for k, v in dri_percentages.items() if v < 70],
            "excesses": [k for k, v in dri_percentages.items() if v > 150]
        }

    def get_weekly_analysis(self, user_id: str) -> Dict:
        """
        Generate weekly nutritional trend analysis
        
        Args:
            user_id: User identifier
            
        Returns:
            Weekly trends and recommendations
        """
        user_logs = self.food_logs.get(user_id, {})

        if not user_logs:
            return {"message": "No food logs found. Start logging meals to see weekly analysis."}

        # Aggregate weekly data
        weekly_nutrients = {k: [] for k in DAILY_RECOMMENDED_INTAKE.keys()}
        dates_with_data = []

        for log_date, day_entries in user_logs.items():
            day_totals = {k: 0.0 for k in DAILY_RECOMMENDED_INTAKE.keys()}
            for entry in day_entries:
                for nutrient, value in entry.get("total_nutrients", {}).items():
                    if nutrient in day_totals:
                        day_totals[nutrient] += value

            dates_with_data.append(log_date)
            for nutrient in weekly_nutrients:
                weekly_nutrients[nutrient].append(round(day_totals.get(nutrient, 0), 2))

        # Calculate averages
        weekly_averages = {}
        for nutrient, values in weekly_nutrients.items():
            if values:
                weekly_averages[nutrient] = round(sum(values) / len(values), 2)

        # Generate trend analysis
        prompt = f"""Analyze these weekly nutritional averages vs daily recommended intakes:

Weekly Averages: {weekly_averages}
Recommended Daily Intakes: {DAILY_RECOMMENDED_INTAKE}
Days tracked: {len(dates_with_data)}

Provide:
1. **Overall diet quality score** (1-10 with justification)
2. **Top 3 nutritional achievements** (where they're meeting/exceeding goals)
3. **Top 3 critical deficiencies** needing immediate attention
4. **Weekly eating pattern analysis** (meal frequency, consistency)
5. **Specific food recommendations** to address deficiencies
6. **Week-over-week improvement suggestions** (3 actionable changes)
7. **Progress toward health goals** assessment

Be encouraging and specific with your recommendations."""

        weekly_analysis = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "dates_tracked": dates_with_data,
            "days_logged": len(dates_with_data),
            "weekly_averages": weekly_averages,
            "recommended_intakes": DAILY_RECOMMENDED_INTAKE,
            "weekly_analysis": weekly_analysis,
            "chart_data": {
                "dates": dates_with_data,
                "calories": weekly_nutrients.get("calories", []),
                "protein": weekly_nutrients.get("protein", []),
                "carbohydrates": weekly_nutrients.get("carbohydrates", []),
                "fat": weekly_nutrients.get("fat", [])
            }
        }

    def analyze_meal_image_description(self, user_id: str, image_description: str, meal_type: str = "meal") -> Dict:
        """
        Analyze meal from image description (simulates image-based logging)
        
        Args:
            user_id: User identifier
            image_description: Description of what's in the meal image
            meal_type: Type of meal
            
        Returns:
            Nutrition analysis based on image description
        """
        prompt = f"""Based on this meal image description: "{image_description}"

Identify all food items visible and estimate:
1. Each food item present
2. Approximate portion size in grams
3. Cooking method if visible

Return JSON: {{"items": [{{"food": "name", "amount_g": grams, "notes": "observations"}}], "meal_type": "type", "overall_description": "summary"}}"""

        try:
            meal_data = self.groq_client.structured_query(
                prompt,
                "You are an expert at identifying foods from images and estimating portions."
            )
            meal_description = " ".join([item["food"] for item in meal_data.get("items", [])])
        except Exception:
            meal_description = image_description

        result = self.log_meal_text(user_id, meal_description or image_description, meal_type)
        result["analyzed_from_image"] = True
        result["image_description"] = image_description
        return result

    def get_nutrition_goals_progress(self, user_id: str, goals: Dict) -> Dict:
        """
        Track progress toward user-defined nutrition goals
        
        Args:
            user_id: User identifier
            goals: Dict with target values for nutrients
            
        Returns:
            Progress report toward goals
        """
        # Get today's data
        today_summary = self.get_daily_summary(user_id)

        if "message" in today_summary:
            return {"message": "Log meals first to track progress toward goals."}

        daily_totals = today_summary.get("daily_totals", {})

        # Calculate progress
        progress = {}
        for nutrient, target in goals.items():
            current = daily_totals.get(nutrient, 0)
            percentage = (current / target * 100) if target > 0 else 0
            progress[nutrient] = {
                "current": current,
                "target": target,
                "percentage": round(percentage, 1),
                "status": "on_track" if 80 <= percentage <= 120 else ("under" if percentage < 80 else "over"),
                "remaining": max(0, target - current)
            }

        # AI feedback on progress
        prompt = f"""Based on today's nutritional progress:
{json.dumps(progress, indent=2)}

Provide:
1. Motivational assessment (are they on track?)
2. Priority nutrients to focus on for remaining meals today
3. Specific food suggestions to meet remaining targets
4. One positive achievement to celebrate
Keep it concise and encouraging."""

        progress_feedback = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "date": str(date.today()),
            "goals": goals,
            "progress": progress,
            "feedback": progress_feedback
        }

    def _generate_meal_feedback(self, meal_text: str, nutrients: Dict, meal_type: str) -> str:
        """Generate immediate feedback after logging a meal"""
        calories = nutrients.get("calories", 0)
        protein = nutrients.get("protein", 0)
        fiber = nutrients.get("fiber", 0)

        prompt = f"""Quick feedback on this {meal_type}: "{meal_text}"
Estimated nutrition: {calories:.0f} cal, {protein:.1f}g protein, {fiber:.1f}g fiber

In 2-3 sentences: What did they do well? What's one improvement? Keep it positive and brief."""

        return self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

    def _generate_daily_analysis(
        self,
        daily_totals: Dict,
        dri_percentages: Dict,
        meals_summary: List[Dict]
    ) -> str:
        """Generate comprehensive daily nutrition analysis"""
        prompt = f"""Daily nutrition analysis:

Totals: {daily_totals}
% of Daily Recommended Intake: {dri_percentages}
Meals logged: {len(meals_summary)} ({', '.join([m['type'] for m in meals_summary])})

Provide:
1. Overall day rating (Excellent/Good/Needs Improvement/Poor)
2. Top 2 nutritional wins
3. Top 2 areas needing improvement
4. Best foods to add for tomorrow to address gaps
5. Hydration reminder if not tracked

Be specific with food recommendations and keep total response under 200 words."""

        return self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

    def get_all_logs(self, user_id: str) -> Dict:
        """Get all logs for a user"""
        return self.food_logs.get(user_id, {})

    def clear_day_log(self, user_id: str, target_date: str = None) -> Dict:
        """Clear logs for a specific day"""
        if not target_date:
            target_date = str(date.today())

        if user_id in self.food_logs and target_date in self.food_logs[user_id]:
            del self.food_logs[user_id][target_date]
            return {"message": f"Logs cleared for {target_date}"}

        return {"message": "No logs found for specified date"}
