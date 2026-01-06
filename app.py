import streamlit as st
import requests
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import tempfile
import os
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO

# --- 1. SETTINGS ---
USER_NAME = "MD AFNAN KHAJA"
COLLEGE = "GM Institute of Technology, Davangere"
API_KEY = st.secrets["GEMINI_API_KEY"]

st.set_page_config(page_title=f"{USER_NAME} - AI Twin", page_icon="🎙️")

st.title("🎙️ Talk to My Digital Twin")
st.write(f"**Candidate:** {USER_NAME}")
st.info("Click the mic, ask a question, and I will reply with my voice.")

# --- 2. MIC INPUT ---
audio_data = mic_recorder(
    start_prompt="🎤 Record",
    stop_prompt="🛑 Stop & Send",
    key="recorder"
)

if audio_data:
    try:
        with st.spinner("Processing voice..."):
            audio_bytes = BytesIO(audio_data["bytes"])
            sound = AudioSegment.from_file(audio_bytes) 
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
                sound.export(wav_file.name, format="wav")
                wav_path = wav_file.name

        # --- 3. SPEECH TO TEXT ---
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
            user_text = recognizer.recognize_google(audio)

        st.chat_message("user").write(user_text)

        # --- 4. GEMINI API (STRICT SAFETY BYPASS) ---
        with st.spinner("Thinking..."):
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            
            # Refined prompt to avoid safety triggers
            prompt = f"You are the professional AI Digital Twin of {USER_NAME}. Answer this interview question as a hardworking student: {user_text}"

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            }
            
            response = requests.post(url, json=payload)
            result = response.json()

            # Attempt to get text, otherwise provide a fallback
            try:
                ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                ai_text = "I'm sorry, I hit a temporary thinking limit. As a hardworking student from GMIT, I'd say: please try asking me again or ask about my projects like the AI Crypto Bot!"

            st.chat_message("assistant").write(ai_text)

            # --- 5. TEXT TO SPEECH ---
            tts = gTTS(ai_text, lang="en")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3:
                tts.save(mp3.name)
                st.audio(mp3.name, autoplay=True)

        os.remove(wav_path)

    except Exception as e:
        st.error("Audio processing failed. Try again!")
        st.write(f"Error Details: {e}")
