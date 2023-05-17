from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv("MONGODB_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
