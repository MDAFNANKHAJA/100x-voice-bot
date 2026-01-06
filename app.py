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

# --- 2. MIC INPUT ---
audio_data = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="🛑 Stop & Send",
    key="recorder_v5" # Changed key to force reset
)

if audio_data:
    try:
        # STEP A: Audio Processing
        st.write("⏳ Step 1: Processing your voice file...")
        audio_bytes = BytesIO(audio_data["bytes"])
        sound = AudioSegment.from_file(audio_bytes) 
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
            sound.export(wav_file.name, format="wav")
            wav_path = wav_file.name

        # STEP B: Speech to Text
        st.write("⏳ Step 2: Converting speech to text...")
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
            user_text = recognizer.recognize_google(audio)
        
        st.success(f"I heard you say: '{user_text}'")

        # STEP C: Gemini AI
        st.write("⏳ Step 3: Getting response from Gemini...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{"parts": [{"text": f"You are {USER_NAME} from {COLLEGE}. Answer this question in 2 sentences: {user_text}"}]}]
        }
        
        response = requests.post(url, json=payload)
        result = response.json()

        if "candidates" in result:
            ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
            st.chat_message("assistant").write(ai_text)

            # STEP D: Voice
            tts = gTTS(ai_text, lang="en")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3:
                tts.save(mp3.name)
                st.audio(mp3.name, autoplay=True)
        else:
            st.error("Gemini API did not return a response. Check your API Key permissions.")
            st.json(result) # This will show us the EXACT error from Google

        os.remove(wav_path)

    except Exception as e:
        st.error(f"Something went wrong: {e}")
