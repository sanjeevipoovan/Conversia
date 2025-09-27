# voice_output.py

import asyncio
import edge_tts
import pygame
import os

# This async function DEFINES 'speak'. It should NOT try to import itself.
async def speak(text: str, voice_name: str, file_path="temp_audio.mp3"):
    """
    Asynchronously generates and plays audio. This function is designed to be
    awaited from within an already running asyncio event loop.
    """
    try:
        # Generate the audio file
        communicate = edge_tts.Communicate(text, voice_name)
        await communicate.save(file_path)

        # Initialize pygame mixer (must be done in the same thread)
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)

        # Play the audio
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            # This non-blocking sleep is crucial for async compatibility
            await asyncio.sleep(0.1)

    except Exception as e:
        print(f"Error in speak function: {e}")
    finally:
        # Clean up mixer and file
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        # A brief sleep to ensure the file handle is released before deleting
        await asyncio.sleep(0.2) 
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except PermissionError as e:
                print(f"Could not remove temp audio file: {e}")