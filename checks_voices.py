# checks_voice.py

import asyncio
# This is the CORRECT place to import 'speak' from your other module.
from voice_output import speak

async def test_voices():
    """A simple function to test each AI agent's voice."""
    
    print("--- Testing AI Agent Voices ---")
    
    # Test Ava's Voice
    print("Testing Ava's voice...")
    await speak("Hello, my name is Ava. The voice output system is working correctly.", "en-US-AriaNeural")
    await asyncio.sleep(1) # Pause between tests
    
    # Test Milo's Voice
    print("Testing Milo's voice...")
    await speak("G'day, Milo here! Voice check, loud and clear.", "en-AU-WilliamNeural")
    await asyncio.sleep(1)
    
    # Test Ray's Voice
    print("Testing Ray's voice...")
    await speak("This is Ray. Voice system functionality confirmed.", "en-US-GuyNeural")
    await asyncio.sleep(1)
    
    # Test Nova's Voice
    print("Testing Nova's voice...")
    await speak("Hi, it's Nova. Hope you're having a great day!", "en-CA-ClaraNeural")
    
    print("\n--- Voice Test Complete ---")


if __name__ == "__main__":
    # This block allows you to run this test script directly.
    try:
        asyncio.run(test_voices())
    except KeyboardInterrupt:
        print("\nTest stopped.")