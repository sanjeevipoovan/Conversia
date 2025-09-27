# app.py (The Definitive, Final Version with the Corrected Function Call)

import random
import time
import os
import asyncio
from dotenv import load_dotenv

from ai_agent import get_ai_response
import speech_recognition as sr
import edge_tts
import pygame
from io import BytesIO

import language_tool_python
from textblob import TextBlob
import nltk

load_dotenv()
pygame.init()

try:
    TextBlob("test")
except nltk.downloader.DownloadError:
    print("Downloading NLTK data (one-time setup)...")
    nltk.download('punkt', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)
    print("Download complete.")

# --- Helper Functions (Core logic remains the same) ---
async def speak_from_memory(text: str, voice_name: str):
    audio_bytes = b""
    try:
        communicate = edge_tts.Communicate(text, voice_name)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio": audio_bytes += chunk["data"]
        if audio_bytes:
            pygame.mixer.music.load(BytesIO(audio_bytes))
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
    except Exception as e:
        print(f"An error occurred during speech generation or playback: {e}")
    finally:
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

def listen_for_speech(prompt=None):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nCalibrating microphone...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        recognizer.dynamic_energy_threshold = True
        if prompt: print(prompt)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=20, phrase_time_limit=60)
            print("Recognizing...")
            return recognizer.recognize_google(audio)
        except Exception:
            print("Sorry, I could not understand that.")
            return None

def clean_response_text(text: str) -> str:
    phrases_to_remove = ['(As Ava)', '(As Milo)', '(As Ray)', '(As Nova)', 'Ava:', 'Milo:', 'Ray:', 'Nova:', '[Milo]:', '[Ray]:', '[Nova]:', '[Ava]:']
    for phrase in phrases_to_remove:
        text = text.replace(phrase, '')
    return text.replace('*', '').replace('#', '').strip()

def analyze_user_performance(user_inputs, tool):
    if not user_inputs: return None
    grammar_corrections, polarity, subjectivity, words = [], 0, 0, 0
    for text in user_inputs:
        matches = tool.check(text)
        for rule in matches: grammar_corrections.append({"original": text[rule.offset:rule.offset+rule.errorLength], "correction": rule.replacements[0] if rule.replacements else "N/A", "message": rule.message})
        blob = TextBlob(text)
        polarity += blob.sentiment.polarity
        subjectivity += blob.sentiment.subjectivity
        words += len(text.split())
    num_inputs = len(user_inputs)
    return {"grammar": grammar_corrections, "sentiment": polarity / num_inputs if num_inputs > 0 else 0, "subjectivity": subjectivity / num_inputs if num_inputs > 0 else 0, "words": words, "interventions": num_inputs}

# --- THE DEFINITIVE, FINAL, TWO-PART REPORTING FUNCTION ---
def generate_comprehensive_gd_report(analysis):
    if not analysis:
        print("\nNo user input was provided to generate a report.")
        return

    print("\n\n--- Your Group Discussion Performance Report ---")
    
    # --- PART 1: THE RAW DATA ANALYSIS (As requested) ---
    print("\n📊 Performance Analysis (The Data):")
    
    # Grammar & Style Details
    print("\n  📝 Grammar & Style Suggestions:")
    if analysis["grammar"]:
        for c in analysis["grammar"]:
            print(f"    - In sentence, change '{c['original']}' to '{c['correction']}' ({c['message']})")
    else:
        print("    - No specific grammar errors found. Excellent clarity!")
    
    # Sentiment Details
    sentiment = analysis['sentiment']
    subjectivity = analysis['subjectivity']
    print("\n  😊 Sentiment Analysis:")
    print(f"    - Average Sentiment: {'Positive' if sentiment > 0.1 else 'Negative' if sentiment < -0.1 else 'Neutral'} (Score: {sentiment:.2f})")
    print(f"    - Average Tone: {'Passionate / Opinion-based' if subjectivity > 0.5 else 'Analytical / Fact-based'} (Score: {subjectivity:.2f})")

    # Participation Details
    print("\n  🗣️ Participation:")
    print(f"    - Total Words Spoken: {analysis['words']}")
    print(f"    - Number of Interventions: {analysis['interventions']}")
    
    # --- PART 2: THE ACTIONABLE SUGGESTIONS (The Coaching) ---
    print("\n\n💡 Actionable Suggestions for Your Next GD (The Coaching):")

    # Suggestion 1: Based on Participation
    if analysis['interventions'] < 3:
        print("  - **Goal: Increase Your Presence.** Your participation was a bit low. In your next GD, make it a goal to contribute at least three times. You can do this by agreeing with someone and adding one new thought ('I agree with Milo, and I also think...'), or by asking a clarifying question.")
    else:
        print("  - **Goal: Maintain Your Strong Presence.** You showed excellent engagement by speaking multiple times. This is a key strength. Continue to balance your speaking time with active listening to maintain this strong performance.")

    # Suggestion 2: Based on Communication Style
    if subjectivity > 0.6 and sentiment > 0.2: # Passionate and Positive
        print("  - **Goal: Strengthen Your Arguments with Evidence.** Your passion and optimism are great for driving a conversation! To make your points even more powerful, try backing them up with a specific example or a piece of data. As you did with the NASA example, linking a strong opinion to a fact makes it almost impossible to argue against.")
    elif subjectivity < 0.4: # Fact-based
        print("  - **Goal: Add Your Personal Conviction.** Your arguments are logical and fact-based, which is a fantastic skill. To increase your persuasive impact, try adding a concluding sentence that expresses your personal opinion or belief on the matter, so the team knows exactly where you stand.")
    elif sentiment < -0.1: # Negative
        print("  - **Goal: Frame Critiques Constructively.** You are good at identifying problems. To ensure your points are well-received, try framing them as a shared challenge. For example, instead of 'That won't work,' you could try 'That's an interesting idea. How could we overcome the potential challenge of...?'")
    
    # Suggestion 3: Based on Grammar
    if analysis["grammar"]:
        print("  - **Goal: Polish Your Language for Maximum Clarity.** Your ideas are strong. Paying attention to the small grammatical details listed in the data section above will make them even more impactful and professional.")
    else:
        print("  - **Goal: Continue Your Clear Communication.** Your language was clear and grammatically precise, which is a significant strength in any professional discussion. Keep it up!")

    print("\n--- End of Report ---")

# --- MAIN APPLICATION LOGIC ---
async def main_discussion():
    print("--- 🎙️ Initializing AI Group Discussion Simulator ---")
    
    agents = ["Milo", "Ray", "Nova", "Ava"]
    voice_map = {"Ava": "en-US-AriaNeural", "Milo": "en-AU-WilliamNeural", "Ray": "en-US-GuyNeural", "Nova": "en-CA-ClaraNeural"}
    QUIT_COMMANDS = {"quit", "quiet", "exit", "stop", "end discussion", "end the conversation"}
    
    concise_personas = {
        "Ava": "You are Ava, the team lead. Your responses must be VERY CONCISE (1-2 sentences). You guide the conversation and summarize conflicts.",
        "Milo": "You are Milo, an optimist. Proactively argue for ADVANTAGES. Keep your points VERY CONCISE (2-3 sentences max).",
        "Ray": "You are Ray, a pragmatist. Proactively argue for DISADVANTAGES. Your arguments must be VERY CONCISE (2-3 sentences max).",
        "Nova": "You are Nova, the user advocate. Analyze the HUMAN IMPACT of the arguments. Keep your analysis VERY CONCISE (2-3 sentences max)."
    }
    
    print("Loading grammar tool...")
    grammar_tool = language_tool_python.LanguageTool('en-US')

    conversation_history = []
    user_inputs_for_analysis = []
    
    loop = asyncio.get_running_loop()
    topic = await loop.run_in_executor(None, listen_for_speech, "To begin, please state the topic for the discussion:")
    if not topic: print("No topic provided. Exiting."); return
        
    print(f"\n--- Discussion Topic: {topic} ---")
    conversation_history.append({"role": "user", "name": "Moderator", "content": f"The topic is: '{topic}'."})
    
    kickoff_msg = f"Okay team, the topic is '{topic}'. Who has an initial thought?"
    conversation_history.append({"role": "user", "name": "Ava", "content": kickoff_msg})
    
    ava_response = get_ai_response(conversation_history, concise_personas["Ava"])
    cleaned_ava_response = clean_response_text(ava_response)
    print(f"\n[Ava]: {cleaned_ava_response}")
    await speak_from_memory(cleaned_ava_response, voice_map["Ava"])
    conversation_history.append({"role": "assistant", "name": "Ava", "content": cleaned_ava_response})
    last_speaker = "Ava"

    while True:
        user_text = await loop.run_in_executor(None, listen_for_speech, "\nYour turn to speak (or say 'quit' to end):")
        
        if user_text:
            if any(command in user_text.lower() for command in QUIT_COMMANDS):
                print("Quit command recognized. Ending discussion."); break
            print(f"[You]: {user_text}")
            conversation_history.append({"role": "user", "name": "Participant", "content": user_text})
            user_inputs_for_analysis.append(user_text)
            last_speaker = "Participant"
        else:
            print("No user input detected, letting the team continue.")
            
        possible_speakers = [agent for agent in agents if agent != last_speaker]
        current_agent = random.choice(possible_speakers)
        
        print(f"\n[{current_agent} is thinking...]")
        raw_response = get_ai_response(conversation_history, concise_personas[current_agent])
        cleaned_response = clean_response_text(raw_response)
        
        print(f"[{current_agent}]: {cleaned_response}")
        await speak_from_memory(cleaned_response, voice_map[current_agent])
        
        conversation_history.append({"role": "assistant", "name": current_agent, "content": cleaned_response})
        last_speaker = current_agent
        
    print("\n--- Discussion Concluded ---")
    summary_prompt = "The discussion is over. As Ava, summarize the core conflict. Importantly, ALSO SUMMARIZE the key points the human 'Participant' made and how they influenced the discussion. Keep it concise."
    conversation_history.append({"role": "user", "name": "Ava", "content": summary_prompt})
    
    summary_response = get_ai_response(conversation_history, concise_personas["Ava"])
    cleaned_summary = clean_response_text(summary_response)
    print("\n[Ava's Summary]:")
    print(cleaned_summary)
    await speak_from_memory(cleaned_summary, voice_map["Ava"])
    
    if grammar_tool:
        final_analysis = analyze_user_performance(user_inputs_for_analysis, grammar_tool)
        
        # --- THE FINAL, CRITICAL FIX IS HERE ---
        # Call the correct, new, two-part report function
        generate_comprehensive_gd_report(final_analysis)
        
        grammar_tool.close()

if __name__ == "__main__":
    try:
        asyncio.run(main_discussion())
    except KeyboardInterrupt:
        print("\nApplication exiting.")
    finally:
        pygame.quit()