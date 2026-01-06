import streamlit as st
import requests
import base64
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import tempfile
import speech_recognition as sr
import os

# --- SETTINGS ---
USER_NAME = "MD AFNAN KHAJA"
COLLEGE = "GM Institute of Technology, Davangere"
API_KEY = st.secrets["GEMINI_API_KEY"]

st.set_page_config(page_title=f"{USER_NAME} - AI Twin", page_icon="🎙️")

# --- PERSONA ---
SYSTEM_PROMPT = f"""
You are the AI Digital Twin of {USER_NAME}, a 7th-semester CSE student from {COLLEGE}.
Rules:
- Be honest about being a learner
- Mention Crypto Bot & AI Drainage Digital Twin projects
- Max 2 sentences
- Use 'I', 'me', 'my'
"""

st.title("🎙️ Talk to My Digital Twin")
st.info("Click the mic and ask a question")

# --- MIC ---
audio_data = mic_recorder(start_prompt="🎤 Speak", stop_prompt="🛑 Stop", key="rec")

if audio_data:
    with st.spinner("Transcribing your voice..."):
        # Save audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_data["bytes"])
            audio_path = f.name

        # Speech → Text
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
            user_text = r.recognize_google(audio)

        st.chat_message("user").write(user_text)

    with st.spinner("Thinking as Digital Twin..."):
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

        payload = {
            "contents": [{
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {"text": user_text}
                ]
            }]
        }

        response = requests.post(url, json=payload)
        result = response.json()

        ai_text = result["candidates"][0]["content"]["parts"][0]["text"]

        st.chat_message("assistant").write(ai_text)

        # Voice Output
        tts = gTTS(ai_text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3:
            tts.save(mp3.name)
            st.audio(mp3.name, autoplay=True)
