# voice_helpers.py

import edge_tts
import asyncio
import os

# --- NEW: Using Google Generative AI for transcription ---
import google.generativeai as genai

# --- TEXT-TO-SPEECH (AI Speaking) - No changes here ---
async def generate_ai_speech(text: str, voice_name: str = "en-US-AriaNeural"):
    """
    Generates speech from text and returns it as audio bytes.
    """
    try:
        communicate = edge_tts.Communicate(text, voice_name)
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
        return audio_bytes
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

# --- SPEECH-TO-TEXT (User Speaking) - MODIFIED FOR GEMINI ---
# Make sure your GOOGLE_API_KEY is in your .env file.
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Takes audio bytes, uploads the file, and returns the transcribed text using Gemini.
    """
    if not audio_bytes:
        return ""

    # Gemini API requires a file path, so we save the bytes to a temporary file
    temp_audio_path = "temp_user_audio.wav"
    with open(temp_audio_path, "wb") as f:
        f.write(audio_bytes)

    uploaded_file = None
    try:
        # 1. Upload the audio file to Google's servers
        print("Uploading audio to Gemini...")
        uploaded_file = genai.upload_file(path=temp_audio_path)
        print("Upload complete.")
        
        # 2. Call the model with a prompt to transcribe the uploaded file
        print("Transcribing with Gemini...")
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        response = model.generate_content([
            "Please transcribe this audio file accurately.", uploaded_file
        ])
        print("Transcription complete.")
        
        # The transcription is in the 'text' attribute of the response
        transcribed_text = response.text
        return transcribed_text.strip()

    except Exception as e:
        print(f"Error during Gemini transcription: {e}")
        return "[Transcription failed]"

    finally:
        # 3. Clean up the temporary files (local and remote)
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        
        if uploaded_file:
            print(f"Deleting remote file: {uploaded_file.name}")
            genai.delete_file(uploaded_file.name)