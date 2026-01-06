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

        # --- 4. GEMINI API (CONSOLIDATED PROMPT) ---
        with st.spinner("Thinking..."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            
            # We combine identity and question into one clear instruction
            full_prompt = (
                f"You are {USER_NAME}, a CSE student at {COLLEGE}. "
                f"Answer the following question in 2 sentences as yourself: {user_text}"
            )

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": full_prompt}
                        ]
                    }
                ]
            }
            
            response = requests.post(url, json=payload)
            result = response.json()

            # Robust text extraction
            try:
                ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
            except:
                ai_text = f"I'm MD AFNAN KHAJA. I heard you asked about '{user_text}', and I'm ready to discuss my projects like the AI Crypto Bot or my work in AI agents!"

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
