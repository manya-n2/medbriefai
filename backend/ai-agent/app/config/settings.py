import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "clinical_agent")
OPENFDA_API_KEY = os.getenv("OPENFDA_API_KEY", "")
OPENFDA_BASE_URL = "https://api.fda.gov/drug/label.json"
RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST/interaction/list.json"
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "prompts")