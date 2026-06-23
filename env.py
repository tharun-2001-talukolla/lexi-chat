import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

loaded = load_dotenv(dotenv_path=ENV_PATH, override=True)

if loaded:
    print("✅ .env loaded successfully")
    print("ENV PATH:", ENV_PATH)
else:
    print("❌ Failed to load .env file")