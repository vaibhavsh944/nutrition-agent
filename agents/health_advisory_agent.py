"""
Health Advisory Agent
Provides preventive health guidance and disease-specific nutrition recommendations.
"""
from typing import Dict, List, Optional
from utils.groq_client import GroqClient
from config.settings import HEALTH_ADVISORY_AGENT


class HealthAdvisoryAgent:
    """
    Agent focused on preventive health nutrition, chronic disease management,
    and evidence-based dietary interventions for health optimization.
    """

    SYSTEM_PROMPT = """You are a preventive medicine specialist and clinical nutritionist with expertise 
in nutrition epidemiology, chronic disease prevention, and integrative medicine. You provide 
evidence-based health and nutrition guidance grounded in peer-reviewed research. 
Always emphasize that dietary advice complements (never replaces) medical treatment.
Reference established guidelines (WHO, AHA, ADA, etc.) when relevant.
Use clear risk communication and always recommend consulting healthcare providers for medical conditions."""

    def __init__(self):
        self.name = HEALTH_ADVISORY_AGENT
        self.groq_client = GroqClient()

    def get_preventive_nutrition_guide(self, age: int, gender: str, risk_factors: List[str] = None) -> Dict:
        """
        Generate preventive nutrition guidance based on demographics and risk factors
        
        Args:
            age: User's age
            gender: User's gender
            risk_factors: List of risk factors (family history, lifestyle, etc.)
            
        Returns:
            Preventive nutrition guide
        """
        risk_text = ", ".join(risk_factors) if risk_factors else "General population"

        prompt = f"""Create a comprehensive preventive nutrition guide for:
- Age: {age} years old
- Gender: {gender}
- Risk Factors: {risk_text}

Include:
1. **Age-Specific Nutritional Priorities**
   - Critical nutrients for this life stage
   - Recommended daily intakes
   - Common deficiencies at this age

2. **Disease Prevention Through Diet**
   - Top 3 chronic diseases to prevent at this age
   - Specific foods that reduce risk
   - Foods/patterns that increase risk

3. **Protective Foods & Eating Patterns**
   - 10 must-eat superfoods for this profile
   - Optimal eating pattern (timing, frequency)
   - Key dietary pattern recommendation

4. **Screening Recommendations**
   - Nutritional biomarkers to monitor
   - How often to check

5. **Actionable 30-Day Prevention Plan**
   - Week-by-week implementation steps
   - Easy dietary swaps to start immediately

Base all recommendations on current WHO/NIH/ADA guidelines."""

        guide = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "age": age,
            "gender": gender,
            "risk_factors": risk_factors or [],
            "preventive_guide": guide
        }

    def get_chronic_disease_nutrition(self, condition: str, severity: str = "moderate") -> Dict:
        """
        Detailed nutrition protocol for chronic disease management
        
        Args:
            condition: Chronic condition name
            severity: mild/moderate/severe
            
        Returns:
            Disease-specific nutrition protocol
        """
        prompt = f"""Develop a comprehensive Medical Nutrition Therapy (MNT) protocol for:
**Condition:** {condition} ({severity} severity)

Provide evidence-based guidance on:

## 1. Nutritional Goals
- Specific targets (e.g., HbA1c, LDL, blood pressure range)
- Caloric and macronutrient targets

## 2. Therapeutic Diet Framework
- Primary dietary pattern recommended
- Scientific rationale

## 3. Critical Foods to Include
- List 15 specific foods with quantities and reasons
- How each food impacts the condition

## 4. Foods to Strictly Avoid
- List with clear explanations of harm
- Hidden sources of harmful components

## 5. Meal Timing & Frequency
- Optimal eating schedule for condition management
- Pre/post medication meal guidance

## 6. Supplements to Consider
- Evidence-based supplements (with dosages)
- Supplements to avoid

## 7. Monitoring & Adjustment
- How to track dietary compliance
- Signs the diet is working
- Red flags requiring medical attention

## 8. Sample 3-Day Meal Plan
- Condition-specific meals with nutritional targets

Reference: ADA, AHA, KDIGO, or relevant clinical guidelines."""

        protocol = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "condition": condition,
            "severity": severity,
            "nutrition_protocol": protocol
        }

    def assess_health_risks(self, user_data: Dict) -> Dict:
        """
        Assess nutritional health risks based on user profile
        
        Args:
            user_data: Dict with health metrics and lifestyle data
            
        Returns:
            Health risk assessment with nutritional recommendations
        """
        prompt = f"""Perform a nutritional health risk assessment for:

**Demographics:** {user_data.get('age')}yr {user_data.get('gender')}
**Physical:** Weight {user_data.get('weight_kg')}kg, Height {user_data.get('height_cm')}cm
**BMI:** {user_data.get('bmi', 'Not calculated')}
**Lab Values:** {user_data.get('lab_values', 'Not provided')}
**Current Diet:** {user_data.get('current_diet', 'Not specified')}
**Lifestyle:** Activity: {user_data.get('activity_level', 'moderate')}, Sleep: {user_data.get('sleep_hours', 7)}hrs, Stress: {user_data.get('stress_level', 'moderate')}
**Family History:** {user_data.get('family_history', 'Not provided')}
**Current Medications:** {user_data.get('medications', 'None')}

Assess:
1. **Risk Score** (Low/Moderate/High) for: Heart Disease, Diabetes T2, Osteoporosis, Metabolic Syndrome
2. **Primary Nutritional Deficiency Risks** (top 5 with probability)
3. **Dietary Pattern Gaps** - what's missing from their diet
4. **Urgent Nutritional Interventions** (prioritized list)
5. **6-Month Health Improvement Roadmap** via diet
6. **Recommended Medical Tests** related to nutrition

Be direct about risks while remaining supportive and actionable."""

        risk_assessment = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "user_data": user_data,
            "risk_assessment": risk_assessment,
            "disclaimer": "This assessment is for informational purposes only and does not replace professional medical advice."
        }

    def get_supplement_advice(self, user_profile: Dict, symptoms: List[str] = None) -> Dict:
        """
        Evidence-based supplement recommendations
        
        Args:
            user_profile: User health profile
            symptoms: List of symptoms or deficiency signs
            
        Returns:
            Supplement recommendations with safety info
        """
        symptoms_text = ", ".join(symptoms) if symptoms else "No specific symptoms"

        prompt = f"""Provide evidence-based supplement recommendations for:

**Profile:** {user_profile.get('age')}yr {user_profile.get('gender')}
**Health Conditions:** {user_profile.get('health_conditions', 'None')}
**Diet Type:** {user_profile.get('dietary_preferences', 'Mixed')}
**Symptoms/Concerns:** {symptoms_text}
**Medications:** {user_profile.get('medications', 'None')}

For each recommended supplement provide:
1. Name and form (e.g., Magnesium Glycinate vs Oxide)
2. Recommended dose and timing
3. Scientific evidence level (Strong/Moderate/Preliminary)
4. Expected benefits timeline
5. Contraindications and drug interactions
6. Quality markers to look for when buying
7. Food sources as alternatives

Also list:
- Supplements to AVOID for this profile
- Supplement combinations to NEVER take together
- When to stop and consult a doctor

Format as a clear, prioritized list."""

        supplement_advice = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "user_profile": user_profile,
            "symptoms": symptoms or [],
            "supplement_recommendations": supplement_advice,
            "disclaimer": "Always consult a healthcare provider before starting supplements, especially with medications."
        }

    def get_gut_health_protocol(self, symptoms: List[str] = None) -> Dict:
        """
        Gut health optimization through nutrition
        
        Args:
            symptoms: Digestive symptoms if any
            
        Returns:
            Gut health nutrition protocol
        """
        symptoms_text = ", ".join(symptoms) if symptoms else "General gut health optimization"

        prompt = f"""Create a comprehensive gut health nutrition protocol for: {symptoms_text}

Include:
1. **The Gut-Health Diet Framework**
   - Core principles (fiber targets, diversity goals)
   - Probiotic-rich foods with serving recommendations
   - Prebiotic foods (top 10 with portions)

2. **5R Gut Restoration Protocol** (Remove, Replace, Reinoculate, Repair, Rebalance)
   - Specific dietary actions for each phase
   - Duration recommendations

3. **Foods That Heal the Gut**
   - Anti-inflammatory foods
   - Gut barrier supportive foods
   - Microbiome diversity boosters

4. **Foods That Harm the Gut**
   - Inflammatory foods to eliminate
   - Hidden gut disruptors
   - Problematic food combinations

5. **4-Week Gut Reset Meal Plan Outline**
   - Phase progression
   - Key foods each week

6. **Microbiome Testing**
   - What to test
   - How to interpret and act on results"""

        protocol = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "symptoms": symptoms or [],
            "gut_health_protocol": protocol
        }

    def analyze_food_drug_interactions(self, medications: List[str], foods: List[str]) -> Dict:
        """
        Check for food-drug interactions
        
        Args:
            medications: List of medications user takes
            foods: List of foods in their diet
            
        Returns:
            Food-drug interaction analysis
        """
        prompt = f"""Analyze potential food-drug interactions for:
**Medications:** {', '.join(medications)}
**Regular Foods:** {', '.join(foods)}

For each significant interaction found:
1. Drug + Food combination
2. Type of interaction (absorption, metabolism, effect enhancement/reduction)
3. Clinical significance (minor/moderate/major)
4. What happens physiologically
5. Management recommendation (timing, avoidance, monitoring)

Also provide:
- Overall dietary guidance for this medication combination
- Best times to take medications relative to meals
- Nutrients that may be depleted by these medications
- Recommended monitoring parameters"""

        interactions = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "medications": medications,
            "foods": foods,
            "interaction_analysis": interactions,
            "disclaimer": "This analysis is informational only. Always discuss food-drug interactions with your pharmacist or physician."
        }

    def get_sports_nutrition_guide(self, sport: str, training_phase: str, user_profile: Dict) -> Dict:
        """
        Sports-specific nutrition guidance
        
        Args:
            sport: Type of sport/exercise
            training_phase: pre_season/in_season/off_season/competition
            user_profile: Athlete's profile
            
        Returns:
            Sport-specific nutrition plan
        """
        prompt = f"""Create a sports nutrition guide for:
**Sport:** {sport}
**Training Phase:** {training_phase}
**Athlete Profile:** {user_profile.get('age')}yr {user_profile.get('gender')}, {user_profile.get('weight_kg')}kg

Include:
1. **Energy Requirements** - total daily calories and periodization
2. **Macronutrient Targets** - specific grams per kg body weight
3. **Meal Timing Protocol**
   - Pre-workout meal (timing, composition, examples)
   - During training nutrition (if applicable)
   - Post-workout recovery meal
   - Daily meal structure
4. **Hydration Strategy** - amounts, timing, electrolyte needs
5. **Performance-Enhancing Foods** - evidenced-based list
6. **Recovery Nutrition** - sleep nutrition, off-day eating
7. **Competition Day Protocol** - pre/during/post race/game nutrition
8. **Supplements** - evidence-based for this sport (NSF-certified preferred)
9. **Sample Training Day vs Rest Day Meal Plan**

Base on current ISSN and ACSM guidelines."""

        sports_guide = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "sport": sport,
            "training_phase": training_phase,
            "athlete_profile": user_profile,
            "sports_nutrition_guide": sports_guide
        }

    def get_mental_health_nutrition(self, mood_concerns: List[str] = None) -> Dict:
        """
        Nutritional psychiatry guidance for mental health
        
        Args:
            mood_concerns: List of mental health concerns (anxiety, depression, etc.)
            
        Returns:
            Mental health nutrition protocol
        """
        concerns_text = ", ".join(mood_concerns) if mood_concerns else "General mood and cognitive health"

        prompt = f"""Provide nutritional psychiatry guidance for: {concerns_text}

Based on current nutritional psychiatry research, include:

1. **Brain-Gut Connection**
   - How gut microbiome affects mental health
   - Key microbial metabolites and mood

2. **Key Nutrients for Mental Health**
   - Omega-3 fatty acids (dosage and sources)
   - Magnesium (types and amounts)
   - Zinc, Iron, B vitamins, Vitamin D
   - Specific amino acids (tryptophan, tyrosine)

3. **The Anti-Inflammatory Diet for Brain Health**
   - Mediterranean diet for depression research
   - Foods that reduce neuroinflammation
   - Specific weekly intake targets

4. **Foods That Worsen Mental Health**
   - Ultra-processed food research
   - Sugar and mood connection
   - Alcohol and mental health nutrition

5. **7-Day Brain-Boosting Meal Plan**

6. **Lifestyle Factors**
   - Meal timing and circadian rhythm
   - Fasting and mental health

Reference: SMILES Trial, PREDIMED, and other landmark studies."""

        mental_nutrition = self.groq_client.simple_query(prompt, self.SYSTEM_PROMPT)

        return {
            "mood_concerns": mood_concerns or [],
            "mental_health_nutrition": mental_nutrition
        }
