import os
from dotenv import load_dotenv

load_dotenv()

print("Gemini Key Loaded:", bool(os.getenv("GEMINI_API_KEY")))
print("Hindsight Key Loaded:", bool(os.getenv("HINDSIGHT_API_KEY")))
