# backend.py

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import random
from dotenv import load_dotenv
import uuid
import os
import base64

from ai_agent import get_ai_response
import google.generativeai as genai
import edge_tts

load_dotenv()
app = FastAPI()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

conversations = {}

# --- Helper Functions ---
def clean_response_text(text: str) -> str:
    phrases_to_remove = ['(As Ava)', '(As Milo)', '(As Ray)', '(As Nova)', 'Ava:', 'Milo:', 'Ray:', 'Nova:']
    for phrase in phrases_to_remove:
        text = text.replace(phrase, '')
    return text.replace('*', '').replace('#', '').strip()

async def generate_ai_speech(text: str, voice_name: str):
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

def transcribe_audio_with_gemini(audio_file_path: str):
    uploaded_file = None
    try:
        uploaded_file = genai.upload_file(path=audio_file_path)
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        response = model.generate_content(["Transcribe this audio file accurately.", uploaded_file])
        return response.text.strip()
    except Exception as e:
        print(f"Error during Gemini transcription: {e}")
        return "[Transcription failed]"
    finally:
        if uploaded_file:
            try: genai.delete_file(uploaded_file.name)
            except Exception: pass

# --- Agent Configuration for a REAL GD ---
agents = ["Milo", "Ray", "Nova", "Ava"]
voice_map = {"Ava": "en-US-AriaNeural", "Milo": "en-AU-WilliamNeural", "Ray": "en-US-GuyNeural", "Nova": "en-CA-ClaraNeural"}
natural_personas = {
    "Ava": "You are Ava, the team lead. Act as a facilitator. Guide the conversation, summarize conflicts, and pose questions to resolve differences, but do it naturally, like a real manager.",
    "Milo": "You are Milo, an optimistic strategist. Proactively argue for the ADVANTAGES of the topic. Be enthusiastic and focus on innovation. If Ray or the user raises a concern, passionately counter it with a positive perspective without being asked.",
    "Ray": "You are Ray, a pragmatic analyst. Proactively argue for the DISADVANTAGES of the topic. Be a polite but firm critical thinker. Ground the conversation in data and problems. If Milo or the user is optimistic, challenge them with a realistic concern.",
    "Nova": "You are Nova, the user advocate. You analyze the arguments from Milo and Ray and comment on the HUMAN IMPACT. You don't take sides. Translate their points into how real people would be affected, using phrases like 'Listening to Ray and Milo, I'm thinking about...'"
}

# --- API Endpoints ---
@app.post("/start_discussion")
async def start_discussion_from_audio(audio_file: UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    temp_audio_path = f"temp_{session_id}_topic.wav"
    with open(temp_audio_path, "wb") as f: f.write(await audio_file.read())
        
    topic = transcribe_audio_with_gemini(temp_audio_path)
    os.remove(temp_audio_path)

    if "[Transcription failed]" in topic:
        return JSONResponse(status_code=500, content={"error": "Transcription of the topic failed."})

    history = [{"role": "user", "name": "Moderator", "content": f"The topic is: '{topic}'."}]
    kickoff_msg = f"Okay team, our topic is '{topic}'. This should be a good one. Milo, you seem excited, why don't you give us an optimistic opening take?"
    history.append({"role": "assistant", "name": "Ava", "content": kickoff_msg})
    
    conversations[session_id] = {"history": history, "last_speaker": "Ava"}
    
    audio_bytes = await generate_ai_speech(kickoff_msg, voice_map["Ava"])
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    return JSONResponse(content={"session_id": session_id, "topic": topic, "text": kickoff_msg, "audio_b64": audio_b64, "speaker": "Ava"})

@app.post("/chat/{session_id}")
async def chat(session_id: str, audio_file: UploadFile = File(...)):
    session = conversations.get(session_id)
    if not session: return JSONResponse(status_code=404, content={"error": "Session not found"})

    temp_audio_path = f"temp_{session_id}_chat.wav"
    with open(temp_audio_path, "wb") as f: f.write(await audio_file.read())
        
    user_text = transcribe_audio_with_gemini(temp_audio_path)
    os.remove(temp_audio_path)

    if "[Transcription failed]" in user_text: return JSONResponse(status_code=500, content={"error": "Transcription failed"})

    session["history"].append({"role": "user", "name": "User", "content": user_text})
    session["last_speaker"] = "User"
    
    possible_speakers = [agent for agent in agents if agent != session["last_speaker"]]
    current_agent = random.choice(possible_speakers)
    
    raw_response = get_ai_response(session["history"], natural_personas[current_agent])
    cleaned_response = clean_response_text(raw_response)
    
    session["history"].append({"role": "assistant", "name": current_agent, "content": cleaned_response})
    session["last_speaker"] = current_agent
    
    audio_bytes = await generate_ai_speech(cleaned_response, voice_map[current_agent])
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    return JSONResponse(content={"user_text": user_text, "text": cleaned_response, "audio_b64": audio_b64, "speaker": current_agent})

@app.get("/")
async def root():
    return {"message": "AI Group Discussion Backend is running."}