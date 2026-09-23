"""
USDA FoodData Central API Client
Fetches nutritional data from the official USDA database
"""
import requests
from typing import Dict, List, Optional
from config.settings import USDA_API_KEY, USDA_BASE_URL


class USDAClient:
    """Client for USDA FoodData Central API"""

    def __init__(self, api_key: str = USDA_API_KEY):
        self.api_key = api_key
        self.base_url = USDA_BASE_URL

    def search_food(self, query: str, page_size: int = 5) -> List[Dict]:
        """
        Search for foods in USDA database
        
        Args:
            query: Food name or description to search
            page_size: Number of results to return
            
        Returns:
            List of food items with basic info
        """
        params = {
            "query": query,
            "pageSize": page_size,
            "api_key": self.api_key,
            "dataType": ["Foundation", "SR Legacy", "Branded"]
        }

        try:
            response = requests.get(
                f"{self.base_url}/foods/search",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            foods = []
            for food in data.get("foods", []):
                food_info = {
                    "fdc_id": food.get("fdcId"),
                    "description": food.get("description", ""),
                    "brand": food.get("brandOwner", ""),
                    "category": food.get("foodCategory", ""),
                    "nutrients": self._extract_key_nutrients(food.get("foodNutrients", []))
                }
                foods.append(food_info)
            
            return foods
        except requests.exceptions.RequestException as e:
            print(f"USDA API search error: {e}")
            return []

    def get_food_details(self, fdc_id: int) -> Optional[Dict]:
        """
        Get detailed nutritional information for a specific food
        
        Args:
            fdc_id: FoodData Central ID
            
        Returns:
            Detailed food nutrition data
        """
        params = {"api_key": self.api_key}

        try:
            response = requests.get(
                f"{self.base_url}/food/{fdc_id}",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "fdc_id": data.get("fdcId"),
                "description": data.get("description", ""),
                "category": data.get("foodCategory", {}).get("description", ""),
                "nutrients": self._extract_all_nutrients(data.get("foodNutrients", [])),
                "serving_size": data.get("servingSize"),
                "serving_size_unit": data.get("servingSizeUnit", "g")
            }
        except requests.exceptions.RequestException as e:
            print(f"USDA API detail error: {e}")
            return None

    def get_multiple_foods(self, fdc_ids: List[int]) -> List[Dict]:
        """
        Get details for multiple foods at once
        
        Args:
            fdc_ids: List of FoodData Central IDs
            
        Returns:
            List of food nutrition data
        """
        params = {"api_key": self.api_key}
        payload = {"fdcIds": fdc_ids}

        try:
            response = requests.post(
                f"{self.base_url}/foods",
                params=params,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            foods = response.json()
            
            return [
                {
                    "fdc_id": food.get("fdcId"),
                    "description": food.get("description", ""),
                    "nutrients": self._extract_all_nutrients(food.get("foodNutrients", []))
                }
                for food in foods
            ]
        except requests.exceptions.RequestException as e:
            print(f"USDA API bulk error: {e}")
            return []

    def _extract_key_nutrients(self, food_nutrients: List[Dict]) -> Dict:
        """Extract the most important nutrients from USDA data"""
        key_nutrient_ids = {
            1008: "calories",      # Energy (kcal)
            1003: "protein",       # Protein
            1005: "carbohydrates", # Carbohydrates
            1004: "fat",           # Total Fat
            1079: "fiber",         # Dietary Fiber
            1087: "calcium",       # Calcium
            1089: "iron",          # Iron
            1092: "potassium",     # Potassium
            1093: "sodium",        # Sodium
            1162: "vitamin_c",     # Vitamin C
        }
        
        nutrients = {}
        for nutrient in food_nutrients:
            nutrient_id = nutrient.get("nutrientId")
            if nutrient_id in key_nutrient_ids:
                name = key_nutrient_ids[nutrient_id]
                nutrients[name] = {
                    "value": nutrient.get("value", 0),
                    "unit": nutrient.get("unitName", "g")
                }
        
        return nutrients

    def _extract_all_nutrients(self, food_nutrients: List[Dict]) -> Dict:
        """Extract all available nutrients from USDA data"""
        nutrients = {}
        for nutrient in food_nutrients:
            nutrient_info = nutrient.get("nutrient", {})
            name = nutrient_info.get("name", "").lower().replace(" ", "_").replace(",", "")
            if name:
                nutrients[name] = {
                    "value": nutrient.get("amount", 0),
                    "unit": nutrient_info.get("unitName", "g"),
                    "nutrient_id": nutrient_info.get("id")
                }
        
        return nutrients

    def get_nutrient_summary(self, food_name: str) -> str:
        """
        Get a formatted nutrient summary for a food item
        
        Args:
            food_name: Name of the food
            
        Returns:
            Formatted string with nutrition info
        """
        foods = self.search_food(food_name, page_size=1)
        
        if not foods:
            return f"No nutritional data found for '{food_name}'"
        
        food = foods[0]
        nutrients = food.get("nutrients", {})
        
        summary_lines = [
            f"**{food['description']}** (per 100g)",
            "---"
        ]
        
        nutrient_labels = {
            "calories": "Calories",
            "protein": "Protein",
            "carbohydrates": "Carbohydrates",
            "fat": "Total Fat",
            "fiber": "Dietary Fiber",
            "sodium": "Sodium",
            "calcium": "Calcium",
            "iron": "Iron",
            "vitamin_c": "Vitamin C",
            "potassium": "Potassium"
        }
        
        for key, label in nutrient_labels.items():
            if key in nutrients:
                val = nutrients[key]
                summary_lines.append(f"• {label}: {val['value']:.1f} {val['unit']}")
        
        return "\n".join(summary_lines)
