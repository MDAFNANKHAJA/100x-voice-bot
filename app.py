import streamlit as st
import requests
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import tempfile
import os
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO

# --------------------------------------------------
# 1. SETTINGS
# --------------------------------------------------
USER_NAME = "MD AFNAN KHAJA"
COLLEGE = "GM Institute of Technology, Davangere"
API_KEY = st.secrets["GEMINI_API_KEY"]

st.set_page_config(
    page_title=f"{USER_NAME} - AI Digital Twin",
    page_icon="🎙️",
    layout="centered"
)

# --------------------------------------------------
# 2. PERSONA PROMPT
# --------------------------------------------------
SYSTEM_PROMPT = f"""
You are the AI Digital Twin of {USER_NAME}, a 7th-semester CSE student from {COLLEGE}.
Rules:
- Be honest about being a learner
- Mention my Crypto Bot and AI-Adaptive Drainage Digital Twin projects when relevant
- Keep answers to max 2 sentences
- Always speak in first person using I, me, my
"""

# --------------------------------------------------
# 3. UI
# --------------------------------------------------
st.title("🎙️ Talk to My Digital Twin")
st.write(f"**Candidate:** {USER_NAME}")
st.info("Click the mic, ask your question, and I will reply with my voice.")

# --------------------------------------------------
# 4. MIC INPUT
# --------------------------------------------------
audio_data = mic_recorder(
    start_prompt="🎤 Record",
    stop_prompt="🛑 Stop & Send",
    key="recorder"
)

if audio_data:
    try:
        # --------------------------------------------------
        # 5. AUDIO BYTES → PCM WAV (SAFE METHOD)
        # --------------------------------------------------
        with st.spinner("Processing your voice..."):
            audio_bytes = BytesIO(audio_data["bytes"])

            # mic_recorder always gives webm/ogg → tell pydub explicitly
            sound = AudioSegment.from_file(audio_bytes, format="webm")
            sound = sound.set_frame_rate(16000).set_channels(1)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
                sound.export(wav_file.name, format="wav")
                wav_path = wav_file.name

        # --------------------------------------------------
        # 6. SPEECH TO TEXT
        # --------------------------------------------------
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
            user_text = recognizer.recognize_google(audio)

        st.chat_message("user").write(user_text)

        # --------------------------------------------------
        # 7. GEMINI TEXT RESPONSE
        # --------------------------------------------------
        with st.spinner("Thinking as my Digital Twin..."):
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

        # --------------------------------------------------
        # 8. TEXT TO SPEECH
        # --------------------------------------------------
        with st.spinner("Speaking..."):
            tts = gTTS(ai_text, lang="en")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3:
                tts.save(mp3.name)
                st.audio(mp3.name, autoplay=True)

        # --------------------------------------------------
        # 9. CLEANUP
        # --------------------------------------------------
        os.remove(wav_path)

    except Exception as e:
        st.error("Something went wrong while processing audio.")
        st.exception(e)
