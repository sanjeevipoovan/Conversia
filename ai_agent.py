# ai_agent.py

import os
from dotenv import load_dotenv
import google.generativeai as genai

# --- FIX: Load .env variables explicitly at the start ---
load_dotenv()

# Configure the Gemini API client from the loaded .env variable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_ai_response(conversation_history: list, persona: str) -> str:
    """
    Gets a conversational response from the Gemini model, applying a persona.
    """
    model = genai.GenerativeModel(
        model_name='gemini-2.5-pro',
        system_instruction=persona
    )
    
    gemini_history = []
    for msg in conversation_history:
        role = 'user' if msg.get('role', 'user') == 'user' else 'model'
        content = f"[{msg.get('name', 'User')}]: {msg.get('content', '')}"
        gemini_history.append({'role': role, 'parts': [content]})

    try:
        response = model.generate_content(
            gemini_history,
            generation_config=genai.types.GenerationConfig(temperature=0.8),
        )
        return response.text
    except Exception as e:
        print(f"Error getting AI response from Gemini: {e}")
        return "I seem to be having trouble thinking right now. Let's try that again."