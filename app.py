import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import speech_recognition as sr
from graph import graph
from mem0 import Memory
import os
import json
import threading
import queue
import tempfile
import pygame

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

# Initialize
if "mem_client" not in st.session_state:
    st.session_state.mem_client = Memory.from_config(config)

if "openai_client" not in st.session_state:
    st.session_state.openai_client = OpenAI()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "listening" not in st.session_state:
    st.session_state.listening = False

if "voice_mode" not in st.session_state:
    st.session_state.voice_mode = False

if "audio_queue" not in st.session_state:
    st.session_state.audio_queue = queue.Queue()

USER_ID = "therapy_user"

# Page config
st.set_page_config(page_title="Therapy AI Assistant", page_icon="🧠", layout="wide")

st.title("🧠 Therapy AI Assistant")
st.caption("A calm, empathetic listener with memory")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    voice_option = st.selectbox(
        "🔊 Voice",
        ["alloy", "echo", "fable", "onyx", "nova", "shimmer", "coral", "sage"],
        index=6
    )
    
    st.divider()
    
    if st.button("🗑️ Clear Memory", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.success("Memory cleared!")
    
    if st.button("📊 View Memories", use_container_width=True):
        memories = st.session_state.mem_client.get_all(user_id=USER_ID)
        if memories:
            st.write("**Stored Memories:**")
            for mem in memories.get("results", [])[:5]:
                st.info(mem.get("memory", ""))
        else:
            st.warning("No memories stored yet")
    
    st.divider()
    st.caption("💡 Tip: Use voice or text input")


def text_to_speech(text: str, voice: str):
    """Convert text to speech and play it through speakers"""
    try:
        response = st.session_state.openai_client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
        )
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(response.content)
            temp_path = f.name
        
        # Initialize pygame mixer and play
        pygame.mixer.init()
        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        # Cleanup
        pygame.mixer.quit()
        os.unlink(temp_path)
        
    except Exception as e:
        st.error(f"TTS Error: {e}")


def speech_to_text():
    """Convert speech to text"""
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        st.info("🎤 Listening... Speak now")
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            text = r.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            st.warning("No speech detected")
            return None
        except sr.UnknownValueError:
            st.warning("Could not understand audio")
            return None
        except Exception as e:
            st.error(f"Error: {e}")
            return None


def process_message(user_input: str, voice: str):
    """Process user message with memory and graph"""
    
    # Search relevant memories
    relevant_memories = st.session_state.mem_client.search(
        query=user_input, 
        user_id=USER_ID
    )
    
    memories = [
        f"ID: {mem.get('id')} Memory: {mem.get('memory')}" 
        for mem in relevant_memories.get("results", [])
    ]
    
    # Add memory context
    memory_context = f"""
    Past context about the user:
    {json.dumps(memories)}
    """
    
    # Prepare message
    user_message = {
        "role": "user", 
        "content": f"{memory_context}\n\nUser: {user_input}"
    }
    st.session_state.messages.append(user_message)
    
    # Stream through graph
    for event in graph.stream(
        {"messages": st.session_state.messages}, 
        stream_mode="values"
    ):
        if "messages" not in event:
            continue
        
        msg = event["messages"][-1]
        
        if msg.type != "ai":
            continue
        
        reply = msg.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        
        # Store in memory
        st.session_state.mem_client.add([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": reply}
        ], user_id=USER_ID)
        
        # Add to chat history for display
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        
        return reply


# Main layout
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 Conversation")
    
    # Display chat history
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])

with col2:
    st.subheader("🎤 Voice Input")
    
    # Toggle continuous voice mode
    voice_mode = st.toggle("🔄 Continuous Voice Mode", value=st.session_state.voice_mode)
    st.session_state.voice_mode = voice_mode
    
    if voice_mode:
        st.info("🎙️ Continuous mode active - listening after each response")
        
        if st.button("⏹️ Stop Voice Mode", use_container_width=True, type="secondary"):
            st.session_state.voice_mode = False
            st.rerun()
        
        # Continuous listening loop
        user_input = speech_to_text()
        
        if user_input:
            st.success(f"You said: {user_input}")
            
            with st.spinner("Thinking..."):
                reply = process_message(user_input, voice_option)
            
            if reply:
                st.success("Response generated!")
                text_to_speech(reply, voice_option)
                st.rerun()  # Loop back to listen again
    
    else:
        if st.button("🎙️ Single Voice Input", use_container_width=True, type="primary"):
            user_input = speech_to_text()
            
            if user_input:
                st.success(f"You said: {user_input}")
                
                with st.spinner("Thinking..."):
                    reply = process_message(user_input, voice_option)
                
                if reply:
                    st.success("Response generated!")
                    text_to_speech(reply, voice_option)
                    st.rerun()

# Text input at bottom
st.divider()
user_text = st.chat_input("Type your message here...")

if user_text:
    with st.spinner("Processing..."):
        reply = process_message(user_text, voice_option)
    
    if reply:
        text_to_speech(reply, voice_option)
        st.rerun()


# Footer
st.divider()
st.caption("⚠️ This is a support tool, not a replacement for professional therapy.")