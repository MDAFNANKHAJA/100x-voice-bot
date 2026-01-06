import streamlit as st
import requests
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import tempfile
import os
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
import time

# --- PERSONAL PROFILE ---
USER_NAME = "MD AFNAN KHAJA"
COLLEGE = "GM Institute of Technology, Davangere"

# --- 1. THE BRAINS: STABLE API FUNCTIONS ---

def call_gemini_api(prompt, api_key):
    """Stable 2026 Google Gemini 1.5 Pro Endpoint"""
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={api_key}"
    # Gemini requires 'contents' -> 'parts' -> 'text'
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    return requests.post(url, json=payload, timeout=20)

def call_claude_api(prompt, api_key):
    """Stable 2026 Anthropic Claude 3.5 Sonnet Endpoint"""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    # Claude requires 'messages' -> 'role/content' and 'model'
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 300,
        "messages": [{"role": "user", "content": prompt}]
    }
    return requests.post(url, json=payload, headers=headers, timeout=20)

def call_openai_api(prompt, api_key):
    """Stable 2026 OpenAI GPT-4o Endpoint"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    # OpenAI requires 'choices' in the response
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300
    }
    return requests.post(url, json=payload, headers=headers, timeout=20)

# --- 2. STREAMLIT UI SETUP ---
st.set_page_config(page_title=f"{USER_NAME} AI", layout="wide")

# Sidebar for choosing the brain
with st.sidebar:
    st.title("🤖 Brain Selector")
    ai_provider = st.radio("Select Brain:", ["Gemini (Student Tier)", "Claude (Anthropic)", "ChatGPT (OpenAI)"])

st.title(f"🎙️ {USER_NAME} - Digital Twin")
st.info("Click the mic and speak clearly to begin the interview.")

# --- 3. THE MAGIC: INTERACTION LOGIC ---
audio_data = mic_recorder(start_prompt="🎤 Start Recording", stop_prompt="🛑 Stop & Send", key="recorder_vFinal")

if audio_data:
    try:
        # STEP A: Audio to Text
        audio_bytes = BytesIO(audio_data["bytes"])
        sound = AudioSegment.from_file(audio_bytes)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
            sound.export(wav_file.name, format="wav")
            wav_path = wav_file.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
            user_text = recognizer.recognize_google(audio)
        
        st.write(f"**Recruiter:** {user_text}")

        # STEP B: API Execution
        full_prompt = f"Respond as {USER_NAME} from {COLLEGE}. Answer in 2 sentences: {user_text}"
        
        with st.spinner(f"Agent thinking with {ai_provider}..."):
            if "Gemini" in ai_provider:
                res = call_gemini_api(full_prompt, st.secrets["GEMINI_API_KEY"])
                # Extract text using Gemini-specific path
                ai_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            
            elif "Claude" in ai_provider:
                res = call_claude_api(full_prompt, st.secrets["CLAUDE_API_KEY"])
                # Extract text using Claude-specific path
                ai_text = res.json()["content"][0]["text"]
            
            else:
                res = call_openai_api(full_prompt, st.secrets["OPENAI_API_KEY"])
                # Extract text using OpenAI-specific path
                ai_text = res.json()["choices"][0]["message"]["content"]

        # STEP C: Output Display & Voice
        st.success(ai_text)
        tts = gTTS(ai_text, lang="en")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3:
            tts.save(mp3.name)
            st.audio(mp3.name, autoplay=True)
        
        os.remove(wav_path)

    except Exception as e:
        st.error("I hit a glitch. Please check your API Keys in the Streamlit Secrets.")
        st.write(f"**Technical Debug Info:** {e}")
