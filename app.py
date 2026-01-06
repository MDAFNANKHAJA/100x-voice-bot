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

# Detailed personal information for authentic responses
LIFE_STORY = "I'm from Davangere, Karnataka. I pursued CSE at GMIT, where I discovered my passion for AI and logic-building."
SUPERPOWER = "Rapid learning and adaptation. I pick up new frameworks like n8n and Gemini faster than most expect."
GROWTH_AREAS = "System Architecture, Advanced Deep Learning, and Technical Leadership."
MISCONCEPTION = "People think I'm just a coder, but I'm a creative problem-solver who cares about user experience."
TECHNICAL_SKILLS = "Python, ML, Streamlit, n8n, NLP, API Development, SQL, Git."
PROJECTS_PORTFOLIO = "AI Voice Bot, AI-Adaptive Drainage Digital Twin, and AI Crypto Market Bot."

# Page config
st.set_page_config(page_title=f"{USER_NAME} AI Twin", page_icon="🎙️", layout="wide")

# Custom CSS for a professional look
st.markdown("""
<style>
    .main-header {text-align: center; padding: 2rem; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; border-radius: 15px; margin-bottom: 2rem;}
    .chat-bubble {background: #f3f4f6; padding: 1.5rem; border-radius: 15px; border-left: 5px solid #3b82f6; margin: 1rem 0;}
    .info-card {background: #ffffff; padding: 1.5rem; border-radius: 12px; border: 1px solid #e5e7eb; margin: 1rem 0;}
</style>
""", unsafe_allow_html=True)

# API PROVIDER FUNCTIONS
def call_gemini_api(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    return requests.post(url, json=payload, timeout=20)

def call_claude_api(prompt, api_key):
    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    payload = {"model": "claude-3-5-sonnet-20241022", "max_tokens": 300, "messages": [{"role": "user", "content": prompt}]}
    return requests.post(url, json=payload, headers=headers, timeout=20)

def call_openai_api(prompt, api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}], "max_tokens": 300}
    return requests.post(url, json=payload, headers=headers, timeout=20)

# Sidebar UI
with st.sidebar:
    st.title("🤖 Control Panel")
    ai_provider = st.radio("Select AI Brain:", ["Gemini (Student Tier)", "Claude (Sonnet)", "ChatGPT (GPT-4o)"])
    st.divider()
    st.write(f"**Candidate:** {USER_NAME}")
    st.write(f"**University:** {COLLEGE}")
    if st.button("🗑️ Clear Chat"):
        st.session_state.conversation_history = []
        st.rerun()

# Main Header
st.markdown(f'<div class="main-header"><h1>🎙️ {USER_NAME} - Digital Twin</h1><p>Interview AI Agent for 100x</p></div>', unsafe_allow_html=True)

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Mic Input
audio_data = mic_recorder(start_prompt="🎤 Start Interview", stop_prompt="🛑 Stop & Send", key="recorder_prod")

if audio_data:
    try:
        # Step 1: Voice to Text
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

        # Step 2: Build Prompt & Select Key
        api_key_name = "GEMINI_API_KEY" if "Gemini" in ai_provider else "CLAUDE_API_KEY" if "Claude" in ai_provider else "OPENAI_API_KEY"
        
        if api_key_name not in st.secrets:
            st.error(f"Missing {api_key_name} in Streamlit Secrets!")
            st.stop()
            
        full_prompt = f"You are {USER_NAME}, a CSE student at {COLLEGE}. Identity: {LIFE_STORY}. Skills: {TECHNICAL_SKILLS}. Projects: {PROJECTS_PORTFOLIO}. Answer this question in 3 sentences: {user_text}"
        
        # Step 3: Get AI Response
        with st.spinner(f"Agent thinking with {ai_provider}..."):
            if "Gemini" in ai_provider:
                res = call_gemini_api(full_prompt, st.secrets["GEMINI_API_KEY"])
                ai_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif "Claude" in ai_provider:
                res = call_claude_api(full_prompt, st.secrets["CLAUDE_API_KEY"])
                ai_text = res.json()["content"][0]["text"]
            else:
                res = call_openai_api(full_prompt, st.secrets["OPENAI_API_KEY"])
                ai_text = res.json()["choices"][0]["message"]["content"]

        # Step 4: Display & Speak
        st.markdown(f'<div class="chat-bubble">{ai_text}</div>', unsafe_allow_html=True)
        tts = gTTS(ai_text, lang="en")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3:
            tts.save(mp3.name)
            st.audio(mp3.name, autoplay=True)
        
        os.remove(wav_path)

    except Exception as e:
        st.error(f"System Error: {e}")
