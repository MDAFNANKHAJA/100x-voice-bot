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

# --- 1. SETTINGS ---
USER_NAME = "MD AFNAN KHAJA"
COLLEGE = "GM Institute of Technology, Davangere"
API_KEY = st.secrets["GEMINI_API_KEY"]

st.set_page_config(page_title=f"{USER_NAME} - AI Twin", page_icon="🎙️")

st.title("🎙️ Talk to My Digital Twin")
st.write(f"**Candidate:** {USER_NAME}")

# --- 2. MIC INPUT (WITH UNIQUE KEY) ---
# We use time.time() to ensure the mic recorder resets every time you refresh
audio_data = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="🛑 Stop & Send",
    key=f"recorder_{int(time.time())}" 
)

if audio_data:
    try:
        # 1. Process Voice to Text
        audio_bytes = BytesIO(audio_data["bytes"])
        sound = AudioSegment.from_file(audio_bytes) 
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
            sound.export(wav_file.name, format="wav")
            wav_path = wav_file.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
            user_text = recognizer.recognize_google(audio)

        # Show what the user asked
        st.chat_message("user").write(user_text)

        # 2. GEMINI API (FORCED CONTEXT)
        with st.spinner("Thinking..."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            
            # We put the user question at the VERY TOP so Gemini can't ignore it
            full_prompt = f"""
            QUESTION: {user_text}
            
            INSTRUCTION: You are {USER_NAME}, a CSE student at {COLLEGE}. 
            Answer the QUESTION above in exactly 2 sentences. 
            Be professional and do not repeat the same answer for different questions.
            """

            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}]
            }
            
            response = requests.post(url, json=payload)
            result = response.json()

            ai_text = result["candidates"][0]["content"]["parts"][0]["text"]

            # Show and Speak
            st.chat_message("assistant").write(ai_text)
            
            tts = gTTS(ai_text, lang="en")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3:
                tts.save(mp3.name)
                st.audio(mp3.name, autoplay=True)

        os.remove(wav_path)

    except Exception as e:
        st.error("I'm having trouble hearing clearly. Please try again!")
