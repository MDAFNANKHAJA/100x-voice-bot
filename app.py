import streamlit as st
import requests
import base64
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import tempfile
import os
import speech_recognition as sr
from pydub import AudioSegment

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
- Keep answers to a maximum of 2 sentences
- Always speak in first person using "I", "me", and "my"
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
    start_prompt="🎤 Record your question",
    stop_prompt="🛑 Stop & Send",
    key="recorder"
)

if audio_data:

    # --------------------------------------------------
    # 5. SAVE & CONVERT AUDIO TO PCM WAV
    # --------------------------------------------------
    with st.spinner("Processing your voice..."):
        # Save raw audio (usually webm/ogg)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as raw_file:
            raw_file.write(audio_data["bytes"])
            raw_audio_path = raw_file.name

        # Convert to PCM WAV (SpeechRecognition compatible)
        wav_audio_path = raw_audio_path.replace(".webm", ".wav")
        audio = AudioSegment.from_file(raw_audio_path)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_audio_path, format="wav")

        # --------------------------------------------------
        # 6. SPEECH TO TEXT
        # --------------------------------------------------
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_audio_path) as source:
            recorded_audio = recognizer.record(source)
            user_text = recognizer.recognize_google(recorded_audio)

        st.chat_message("user").write(user_text)

    # --------------------------------------------------
    # 7. SEND TEXT TO GEMINI
    # --------------------------------------------------
    with st.spinner("Thinking as my Digital Twin..."):
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": SYSTEM_PROMPT},
                        {"text": user_text}
                    ]
                }
            ]
        }

        response = requests.post(url, json=payload)
        result = response.json()

        ai_text = result["candidates"][0]["content"]["parts"][0]["text"]

        st.chat_message("assistant").write(ai_text)

    # --------------------------------------------------
    # 8. TEXT TO SPEECH
    # --------------------------------------------------
    with st.spinner("Speaking..."):
        tts = gTTS(text=ai_text, lang="en")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3_file:
            tts.save(mp3_file.name)
            st.audio(mp3_file.name, autoplay=True)

    # --------------------------------------------------
    # 9. CLEANUP (OPTIONAL)
    # --------------------------------------------------
    try:
        os.remove(raw_audio_path)
        os.remove(wav_audio_path)
    except:
        pass
