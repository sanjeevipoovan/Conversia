# app.py (The Streamlit Frontend)

import streamlit as st
import requests
import base64
from streamlit_audiorec import st_audiorec

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(layout="wide", page_title="AI Voice GD")
st.title("🎙️ AI Speech-to-Speech Group Discussion")
st.markdown("Your definitive voice-powered GD simulator. Speak your mind and listen to the AI team respond.")

if 'session_id' not in st.session_state:
    st.session_state.clear()
    st.session_state.session_id = None
    st.session_state.messages = []
    st.session_state.discussion_ended = False
    st.session_state.autoplay_audio = None
    st.session_state.topic = ""

avatar_map = {"User": "👤", "Ava": "👩‍💼", "Milo": "🚀", "Ray": "📈", "Nova": "❤️"}
for message in st.session_state.messages:
    with st.chat_message(message["name"], avatar=avatar_map.get(message["name"], "🤖")):
        st.write(message["content"])

if st.session_state.autoplay_audio:
    st.audio(st.session_state.autoplay_audio, autoplay=True)
    st.session_state.autoplay_audio = None

# --- MAIN APP LOGIC: MODIFIED STARTUP FOR VOICE-ONLY ---
if not st.session_state.session_id and not st.session_state.discussion_ended:
    st.info("To begin, click the microphone below and state the topic for the discussion.")
    
    # Use the audio recorder for the topic input
    topic_audio_bytes = st_audiorec()
    
    if topic_audio_bytes:
        with st.spinner("Transcribing topic and starting the discussion..."):
            files = {'audio_file': ('topic_audio.wav', topic_audio_bytes, 'audio/wav')}
            
            # Send the audio to the backend's single start endpoint
            response = requests.post(f"{BACKEND_URL}/start", files=files)
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.session_id = data["session_id"]
                st.session_state.topic = data["topic"]
                # Display the transcribed topic to confirm it was understood
                st.session_state.messages.append({"name": "Moderator", "content": f"Topic: {st.session_state.topic}"})
                # Add Ava's opening message
                st.session_state.messages.append({"name": data["speaker"], "content": data["text"]})
                # Queue Ava's opening audio for playback
                audio_bytes = base64.b64decode(data["audio_b64"])
                st.session_state.autoplay_audio = audio_bytes
                st.rerun()
            else:
                st.error(f"Could not start the discussion. The server said: {response.text}")

elif st.session_state.session_id and not st.session_state.discussion_ended:
    st.subheader(f"Discussion Topic: {st.session_state.topic}")
    st.markdown("---")
    st.write("#### Your Turn: Click the microphone to speak")
    audio_bytes = st_audiorec()
    
    if audio_bytes:
        with st.spinner("The team is listening and thinking..."):
            files = {'audio_file': ('user_audio.wav', audio_bytes, 'audio/wav')}
            response = requests.post(f"{BACKEND_URL}/chat/{st.session_state.session_id}", files=files)
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.messages.append({"name": "User", "content": data["user_text"]})
                st.session_state.messages.append({"name": data["speaker"], "content": data["text"]})
                audio_bytes = base64.b64decode(data["audio_b64"])
                st.session_state.autoplay_audio = audio_bytes
                st.rerun()
            else:
                st.error(f"An error occurred. The server said: {response.text}")

    st.markdown("---")
    if st.button("End Discussion & Get Report"):
        st.session_state.discussion_ended = True
        st.rerun()

elif st.session_state.discussion_ended:
    st.success("Discussion Ended! (Final report feature can be built out here)")
    if st.button("Start New Discussion"):
        st.session_state.clear()
        st.rerun()