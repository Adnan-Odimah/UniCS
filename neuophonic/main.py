"""
Entry point for the EcoMeal Mentor application.
Integrates voice command processing with backend API functions to provide recipe suggestions.
"""
NEUPHONIC_API_KEY = "d5a15d9bb926ebc552705ff41e1734262dc253e6dcdccefc20a83fcaa9701437.a0a43122-59b6-46c8-9a30-7db061e00632"


from voice_module import process_input, text_to_speech, test_agent
import asyncio
import websockets
from pyneuphonic.player import AudioPlayer
from pyneuphonic import Neuphonic, WebsocketEvents, Agent
from pyneuphonic.models import APIResponse, TTSResponse
from pyneuphonic.models import APIResponse, AgentResponse
import aioconsole

async def get_user_audio_as_text(client, agent_id):
    user_input = None
    stop_event = asyncio.Event()

    def on_message(message: APIResponse[AgentResponse]):
        nonlocal user_input
        if message.data.type == 'user_transcript':
            user_input = message.data.text
            stop_event.set()

    agent = Agent(
        client,
        agent_id=agent_id,
        tts_model='neu_hq',
        on_message=on_message,
    )

    await agent.start()

    try:
        await stop_event.wait()  # Wait for the event to be set
    finally:
        await agent.stop()

    return user_input

async def main():   

    client = Neuphonic(api_key=NEUPHONIC_API_KEY)

    agent_id_1 = client.agents.create(name='Agent 1',prompt='You are a friendly assistant.',  greeting='Hello').data['agent_id']
    agent_id_2 = client.agents.create(name='Agent 2',prompt='You are a friendly assistant.',  greeting='').data['agent_id']

    ws = client.tts.AsyncWebsocketClient()

    player = AudioPlayer()
    player.open()

    # Attach event handlers. Check WebsocketEvents enum for all valid events.
    async def on_message(message: APIResponse[TTSResponse]):
        player.play(message.data.audio)

    async def on_close():
        player.close()

    ws.on(WebsocketEvents.MESSAGE, on_message)
    ws.on(WebsocketEvents.CLOSE, on_close)

    

    await ws.open()

    while True:

        user_text = await get_user_audio_as_text(client, agent_id_1)

        if user_text.lower() == 'quit':
            break
        
        text_response = process_input(user_text)

        await ws.send(text_response, autocomplete=True)

    await ws.close()  # close the websocket and terminate the audio resources


asyncio.run(main())