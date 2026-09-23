# 🥗 AI-Powered Nutrition Agent
### IBM Hackathon 2025 — Problem Statement #1

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![GROQ](https://img.shields.io/badge/LLM-GROQ%20GPT--OSS--20B-orange.svg)](https://groq.com)
[![USDA](https://img.shields.io/badge/Data-USDA%20FoodData%20Central-green.svg)](https://fdc.nal.usda.gov)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Problem Statement

Good nutrition is the foundation of health, but individuals struggle with diet planning, portion control, and tracking nutritional intake. Information about healthy diets is scattered across unreliable sources. Without personalized, real-time guidance, many fail to maintain balanced diets or make informed food choices.

## 🎯 Solution

An **AI-powered Multi-Agent Nutrition System** that delivers personalized dietary insights and guidance for individuals, families, and health professionals.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              NutritionAgentOrchestrator                  │
│         (Intent Router + Conversation Manager)           │
└──────────┬──────────┬──────────┬───────────┬────────────┘
           │          │          │           │
    ┌──────▼──┐ ┌─────▼───┐ ┌───▼──────┐ ┌──▼──────────┐
    │Nutrition│ │  Diet   │ │ Health  │ │  Food Log  │
    │Knowledge│ │ Recom-  │ │Advisory │ │ & Feedback │
    │  Agent  │ │mendation│ │  Agent  │ │   Agent    │
    │  (RAG)  │ │  Agent  │ │         │ │            │
    └──────┬──┘ └────┬────┘ └────┬────┘ └──────┬─────┘
           │         │           │              │
    ┌──────▼─────────▼───────────▼──────────────▼─────┐
    │          GROQ API (openai/gpt-oss-20b)           │
    │          USDA FoodData Central API               │
    │          Whisper (whisper-large-v3-turbo)        │
    └──────────────────────────────────────────────────┘
```

---

## 🤖 Multi-Agent System

### 1. 🧠 Nutrition Knowledge Agent
- **Purpose**: Fetch and summarize nutritional data using RAG
- **Data Source**: USDA FoodData Central API (official government database)
- **Capabilities**:
  - Look up nutritional facts for any food (calories, macros, vitamins, minerals)
  - Compare foods nutritionally
  - Find best food sources for specific nutrients
  - Analyze complete meal nutrition
  - Suggest healthy food substitutes

### 2. 🥗 Diet Recommendation Agent  
- **Purpose**: Generate personalized meal plans
- **Capabilities**:
  - Create daily and weekly meal plans based on user profile
  - Account for health conditions (diabetes, hypertension, etc.)
  - Support dietary preferences (vegetarian, vegan, keto, etc.)
  - Family meal planning
  - Condition-specific diet protocols (DASH, Mediterranean, low-GI)
  - TDEE/BMR calculation for calorie targets

### 3. 🏥 Health Advisory Agent
- **Purpose**: Preventive health and disease-specific nutrition
- **Capabilities**:
  - Chronic disease nutrition protocols (Medical Nutrition Therapy)
  - Health risk assessments
  - Evidence-based supplement recommendations
  - Sports nutrition guidance
  - Gut health protocols
  - Mental health nutrition (nutritional psychiatry)
  - Food-drug interaction analysis

### 4. 📊 Food Log & Feedback Agent
- **Purpose**: Real-time meal tracking and feedback
- **Capabilities**:
  - Log meals via text, voice (Whisper transcription), or image description
  - Instant nutritional analysis vs. daily recommended intake
  - Daily summaries with DRI% tracking
  - Weekly trend analysis
  - Goal progress tracking
  - Personalized improvement suggestions

---

## 📊 Visualization Dashboard

- **ASCII Terminal Dashboard**: Real-time nutrient progress bars with status indicators
- **HTML Web Dashboard**: Interactive visual dashboard with progress charts
- **Weekly Trend Charts**: Calorie and macro trends over time
- **Deficiency/Excess Alerts**: Color-coded alerts for nutritional imbalances

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/nutrition-agent-ibm-hackathon.git
cd nutrition-agent-ibm-hackathon

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Edit .env.example and rename to .env
cp .env.example .env
```

### Configuration

Set up your API keys in `.env`:
```env
GROQ_API_KEY=your_groq_api_key
USDA_API_KEY=your_usda_api_key
GROQ_MODEL=openai/gpt-oss-20b
WHISPER_MODEL=whisper-large-v3-turbo
```

### Running the Application

```bash
# Interactive chat mode
python app.py

# Run full demonstration
python app.py --demo
```

---

## 💻 Usage Examples

### Chat Interface
```
👤 User: What are the nutritional facts for quinoa?
🤖 NutritionBot [NutritionKnowledgeAgent]: Quinoa is a complete protein...

👤 User: I had oatmeal with banana for breakfast
🤖 NutritionBot [FoodLogFeedbackAgent]: ✅ Logged your breakfast!
   Great choice! ~380 calories, 12g protein...

👤 User: Give me a diabetes-friendly weekly meal plan
🤖 NutritionBot [DietRecommendationAgent]: Here's your 7-day low-GI plan...
```

### Python API
```python
from nutrition_orchestrator import NutritionAgentOrchestrator

orchestrator = NutritionAgentOrchestrator()

# Chat interface
response = orchestrator.chat("user123", "What should I eat for heart health?")
print(response["response"])

# Direct agent usage
from agents.nutrition_knowledge_agent import NutritionKnowledgeAgent
agent = NutritionKnowledgeAgent()
data = agent.get_food_nutrition("salmon")
print(data["ai_summary"])
```

---

## 📁 Project Structure

```
nutrition-agent/
├── app.py                          # Main application entry point
├── nutrition_orchestrator.py       # Multi-agent orchestrator
├── requirements.txt                # Python dependencies
├── agents/
│   ├── nutrition_knowledge_agent.py  # RAG + USDA data fetching
│   ├── diet_recommendation_agent.py  # Personalized meal planning
│   ├── health_advisory_agent.py      # Preventive health guidance
│   └── food_log_feedback_agent.py    # Meal tracking & analysis
├── utils/
│   ├── groq_client.py             # GROQ API client (LLM + Whisper)
│   └── usda_client.py             # USDA FoodData Central client
├── config/
│   └── settings.py               # Configuration & constants
├── dashboard/
│   └── nutrition_dashboard.py    # ASCII + HTML visualization
└── data/                         # Sample data files
```

---

## 🔑 API Keys

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| GROQ API | LLM (GPT-OSS-20B) + Whisper STT | Yes |
| USDA FoodData Central | Official nutrition database | Yes (unlimited) |

---

## 🌟 Key Features

| Feature | Status |
|---------|--------|
| Personalized Diet Plans | ✅ |
| USDA Food Data RAG Retrieval | ✅ |
| Text Meal Logging | ✅ |
| Voice Meal Logging (Whisper) | ✅ |
| Image-based Meal Analysis | ✅ (description-based) |
| Chronic Disease Nutrition | ✅ |
| Multi-Agent Orchestration | ✅ |
| Dashboard Visualization | ✅ (ASCII + HTML) |
| Family Meal Planning | ✅ |
| Sports Nutrition | ✅ |
| Supplement Guidance | ✅ |
| Food-Drug Interactions | ✅ |

---

## 🛠️ Technology Stack

- **LLM**: GROQ API — `openai/gpt-oss-20b`
- **Speech-to-Text**: GROQ Whisper — `whisper-large-v3-turbo`
- **Nutrition Database**: USDA FoodData Central API
- **Framework**: Python 3.9+
- **Architecture**: Multi-Agent System with Orchestrator Pattern
- **Cloud**: IBM Cloud (deployment ready)

---

## 👥 Team

Built for **IBM Hackathon 2025 — Problem Statement #1: Nutrition Agent**

🔗 **GitHub Repository:** [https://github.com/vaibhavsh944/nutrition-agent](https://github.com/vaibhavsh944/nutrition-agent)

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.
