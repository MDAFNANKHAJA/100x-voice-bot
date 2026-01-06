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

FALLBACK_MESSAGE = (
    "I'm sorry, I hit a temporary thinking limit. "
    "As a hardworking student from GMIT, I'd say: "
    "please try asking me again or ask about my projects like the AI Crypto Bot!"
)

VOICE_ERROR_MESSAGE = (
    "I couldn't clearly hear that. "
    "Please speak a little louder or try again."
)

st.set_page_config(
    page_title=f"{USER_NAME} - AI Digital Twin",
    page_icon="🎙️"
)

# --------------------------------------------------
# 2. PERSONA
# --------------------------------------------------
SYSTEM_PROMPT = f"""
You are the AI Digital Twin of {USER_NAME}, a 7th-semester CSE student from {COLLEGE}.
Rules:
- Be honest about being a learner
- Mention my AI Crypto Bot and AI-Adaptive Drainage Digital Twin projects when relevant
- Keep answers to max 2 sentences
- Always speak in first person using I, me, my
"""

# --------------------------------------------------
# 3. UI
# --------------------------------------------------
st.title("🎙️ Talk to My Digital Twin")
st.write(f"**Candidate:** {USER_NAME}")
st.info("Click the mic, ask a question, and I will reply with my voice.")

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
        # 5. AUDIO → PCM WAV
        # --------------------------------------------------
        with st.spinner("Listening carefully..."):
            audio_bytes = BytesIO(audio_data["bytes"])
            sound = AudioSegment.from_file(audio_bytes, format="webm")
            sound = sound.set_frame_rate(16000).set_channels(1)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
                sound.export(wav_file.name, format="wav")
                wav_path = wav_file.name

        # --------------------------------------------------
        # 6. SPEECH TO TEXT (SAFE)
        # --------------------------------------------------
        r = sr.Recognizer()
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True

        try:
            with sr.AudioFile(wav_path) as source:
                audio = r.record(source)
                user_text = r.recognize_google(audio)
        except sr.UnknownValueError:
            st.warning(VOICE_ERROR_MESSAGE)
            st.chat_message("assistant").write(VOICE_ERROR_MESSAGE)
            os.remove(wav_path)
            st.stop()
        except sr.RequestError:
            st.error("Speech service unavailable. Please try again.")
            os.remove(wav_path)
            st.stop()

        st.chat_message("user").write(user_text)

        # --------------------------------------------------
        # 7. GEMINI CALL (SAFE)
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

            response = requests.post(url, json=payload, timeout=20)
            result = response.json()

            if (
                "candidates" in result and
                len(result["candidates"]) > 0 and
                "content" in result["candidates"][0]
            ):
                ai_text = result["candidates"][0]["content"]["parts"][0].get(
                    "text", FALLBACK_MESSAGE
                )
            else:
                ai_text = FALLBACK_MESSAGE

        st.chat_message("assistant").write(ai_text)

        # --------------------------------------------------
        # 8. TEXT TO SPEECH
        # --------------------------------------------------
        tts = gTTS(ai_text, lang="en")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3:
            tts.save(mp3.name)
            st.audio(mp3.name, autoplay=True)

        os.remove(wav_path)

    except Exception as e:
        st.error("A temporary issue occurred. Please try again.")
        st.chat_message("assistant").write(FALLBACK_MESSAGE)
        st.exception(e)
