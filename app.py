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

        # --- 4. GEMINI API (ULTRA STABLE VERSION) ---
        with st.spinner("Thinking..."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            
            # Simplified prompt to pass all safety filters
            prompt = f"The user asked: {user_text}. Respond as {USER_NAME}, a student from {COLLEGE}. Be helpful and professional."

            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            
            response = requests.post(url, json=payload)
            result = response.json()

            # --- LOGIC TO EXTRACT TEXT OR SHOW ERROR ---
            if "candidates" in result and result["candidates"][0].get("content"):
                ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                # If blocked, this helps us see WHY
                reason = result.get("promptFeedback", {}).get("blockReason", "Unknown Limit")
                ai_text = f"I am {USER_NAME}. I'm currently refining my AI brain to be more robust. Let's talk about my work with AI Agents or my Crypto Bot instead! (Reason: {reason})"

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
