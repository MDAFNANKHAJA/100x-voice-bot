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
# SETTINGS
# --------------------------------------------------
USER_NAME = "MD AFNAN KHAJA"
COLLEGE = "GM Institute of Technology, Davangere"
API_KEY = st.secrets["GEMINI_API_KEY"]

FALLBACK_MESSAGE = (
    "I'm sorry, I hit a temporary thinking limit. "
    "As a hardworking student from GMIT, I'd say: "
    "please try asking me again or ask about my projects like the AI Crypto Bot!"
)

VOICE_ERROR_MESSAGE = "I couldn't clearly hear that. Please try again."

st.set_page_config(page_title="AI Digital Twin", page_icon="🎙️")

# --------------------------------------------------
# UI
# --------------------------------------------------
st.title("🎙️ Talk to My Digital Twin")
st.write(f"**Candidate:** {USER_NAME}")

audio_data = mic_recorder("🎤 Record", "🛑 Stop", key="rec")

if audio_data:
    # --------------------------------------------------
    # AUDIO → TEXT
    # --------------------------------------------------
    audio_bytes = BytesIO(audio_data["bytes"])
    sound = AudioSegment.from_file(audio_bytes, format="webm")
    sound = sound.set_frame_rate(16000).set_channels(1)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        sound.export(f.name, format="wav")
        wav_path = f.name

    r = sr.Recognizer()

    try:
        with sr.AudioFile(wav_path) as src:
            audio = r.record(src)
            user_text = r.recognize_google(audio)
    except sr.UnknownValueError:
        st.warning(VOICE_ERROR_MESSAGE)
        st.stop()

    st.chat_message("user").write(user_text)

    # 🚫 Reject useless inputs
    if len(user_text.strip()) < 4:
        st.chat_message("assistant").write(
            "Could you please ask a complete question?"
        )
        st.stop()

    # --------------------------------------------------
    # GEMINI PROMPT (FIXED)
    # --------------------------------------------------
    final_prompt = f"""
You are {USER_NAME}, a 7th-semester CSE student from {COLLEGE}.
You must always answer as yourself in first person.

Rules:
- Max 2 sentences
- Be confident but honest
- Mention AI Crypto Bot or AI Drainage Digital Twin if relevant
- NEVER refuse to answer unless unsafe

Question:
{user_text}
"""

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    payload = {
        "contents": [{
            "parts": [{"text": final_prompt}]
        }]
    }

    response = requests.post(url, json=payload, timeout=20)
    result = response.json()

    if "candidates" in result and result["candidates"]:
        ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
    else:
        ai_text = FALLBACK_MESSAGE

    st.chat_message("assistant").write(ai_text)

    # --------------------------------------------------
    # VOICE OUTPUT
    # --------------------------------------------------
    tts = gTTS(ai_text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3:
        tts.save(mp3.name)
        st.audio(mp3.name, autoplay=True)

    os.remove(wav_path)
