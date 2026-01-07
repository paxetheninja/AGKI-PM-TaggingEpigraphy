from google import genai
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)
    print("Client initialized")
else:
    print("No GOOGLE_API_KEY found")
