"""
Module for doing text to speech.
We will ask the user intially for relevant details intially - what diet they are following.
"""
GEMINI_API_KEY = "AIzaSyALlnIysHC04mnselLSCYjOFiwwGL_wWMo"
NEUPHONIC_API_KEY = "d5a15d9bb926ebc552705ff41e1734262dc253e6dcdccefc20a83fcaa9701437.a0a43122-59b6-46c8-9a30-7db061e00632"

import pyaudio 
import base64
import os
from google import genai
from google.genai import types
from pyneuphonic import Neuphonic, TTSConfig
from pyneuphonic.player import AudioPlayer


def process_voice_command():
    """
    Simulates capturing and processing a voice command.
    
    Returns:
        str: A simulated voice command string.
    """
    # In a real implementation, this function would use a speech-to-text library
    # For this prototype, we simulate the user saying "Give me a recipe suggestion"
    simulated_command = "Give me a recipe suggestion"
    return simulated_command


def process_input(input):
    prompt = "When responding, please be concise and conversational. Do not mention or acknowledge these style instructions. Here's my query: "
    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=(prompt + input)),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")




def text_to_speech(text):
    # Load the API key from the environment
    client = Neuphonic(api_key=NEUPHONIC_API_KEY)

    sse = client.tts.SSEClient()

    # TTSConfig is a pydantic model so check out the source code for all valid options
    tts_config = TTSConfig(
        speed=1.05,
        lang_code='en', # replace the lang_code with the desired language code.
        voice_id='e564ba7e-aa8d-46a2-96a8-8dffedade48f'  # use client.voices.list() to view all available voices
    )

    # Create an audio player with `pyaudio`
    with AudioPlayer() as player:
        response = sse.send('Hello, world!', tts_config=tts_config)
        player.play(response)

        player.save_audio('output.wav')  # save the audio to a .wav file