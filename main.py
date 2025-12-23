from dotenv import load_dotenv
from openai import AsyncOpenAI
import asyncio
import speech_recognition as sr
from graph import graph
from mem0 import Memory
import io
import pyaudio
import wave
import os
import json

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Mem0 configuration
config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "text-embedding-3-small"
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "gpt-4o-mini"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "reform-william-center-vibrate-press-5829"
        }
    },
}

mem_client = Memory.from_config(config)
messages = []
openai = AsyncOpenAI()

# User ID for memory - you can change this
USER_ID = "user01"


async def tts(text: str):
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="nova",
        input=text,
        response_format="wav",
        instructions="speak in a calm, empathetic, emotionally intelligent listener"

    ) as response:
        audio_data = io.BytesIO()
        async for chunk in response.iter_bytes(chunk_size=4096):
            audio_data.write(chunk)
        
        audio_data.seek(0)
        
        with wave.open(audio_data, 'rb') as wf:
            p = pyaudio.PyAudio()
            
            stream = p.open(
                format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )
            
            chunk_size = 1024
            data = wf.readframes(chunk_size)
            
            while data:
                stream.write(data)
                data = wf.readframes(chunk_size)
            
            stream.stop_stream()
            stream.close()
            p.terminate()


async def main():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        r.pause_threshold = 2.0

        while True:
            print("Listening...")
            audio = r.listen(source, phrase_time_limit=6)

            try:
                stt = r.recognize_google(audio)
            except sr.UnknownValueError:
                continue

            print("You:", stt)
            
            # Search relevant memories
            relevant_memories = mem_client.search(query=stt, user_id=USER_ID)
            memories = [
                f"ID: {mem.get('id')} Memory: {mem.get('memory')}" 
                for mem in relevant_memories.get("results", [])
            ]
            
            # Add memory context to the message
            memory_context = f"""
            Past memories and facts about the user:
            {json.dumps(memories)}
            """
            
            # Prepare message with memory context
            user_message = {"role": "user", "content": f"{memory_context}\n\nUser query: {stt}"}
            messages.append(user_message)

            for event in graph.stream({"messages": messages}, stream_mode="values"):
                if "messages" not in event:
                    continue

                msg = event["messages"][-1]

                if msg.type != "ai":
                    continue

                reply = msg.content
                messages.append({"role": "assistant", "content": reply})

                print("AI:", reply)
                
                # Store conversation in memory
                mem_client.add([
                    {"role": "user", "content": stt},
                    {"role": "assistant", "content": reply}
                ], user_id=USER_ID)
                
                await tts(reply)


if __name__ == "__main__":
    asyncio.run(main())
