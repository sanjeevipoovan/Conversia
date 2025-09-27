# audio_processing.py

import speech_recognition as sr
import time

def listen_for_speech_with_duration(prompt=None):
    """
    Listens for speech with HIGHLY improved accuracy by dynamically adjusting for ambient noise.
    Returns both the recognized text and the duration in seconds.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        
        # --- KEY IMPROVEMENTS FOR ACCURACY ---

        # 1. Higher Pause Threshold: Allows for slightly longer pauses mid-sentence
        #    without cutting off the user. Default is 0.8.
        recognizer.pause_threshold = 1.5

        # 2. Dynamic Energy Threshold: This tells the recognizer to ignore background noise
        #    that is constant. It will automatically adjust its "volume gate".
        recognizer.dynamic_energy_threshold = True

        # 3. Ambient Noise Adjustment (The Most Important Change):
        #    The recognizer listens for one second to learn the ambient noise level.
        #    This is crucial for filtering out background sounds.
        print("Calibrating microphone for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Microphone calibrated.")
        
        # --- END OF IMPROVEMENTS ---

        if prompt:
            print(prompt)

        try:
            # Start the timer just before listening
            start_time = time.time()
            # Listen for the user's input with better settings
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=45)
            end_time = time.time()

            duration = end_time - start_time
            
            print("Recognizing...")
            # Use Google's online speech recognition, which is generally high-quality.
            text = recognizer.recognize_google(audio)
            
            return text, duration

        except sr.UnknownValueError:
            print("Sorry, I could not understand what you said. Please try again.")
            return None, 0
        except sr.RequestError as e:
            print(f"Could not request results from service; {e}")
            return None, 0
        except sr.WaitTimeoutError:
            # This is expected if the user doesn't speak.
            return None, 0