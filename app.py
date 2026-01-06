import streamlit as st
import requests
import base64
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import tempfile
import os

# --- 1. SETTINGS ---
USER_NAME = "MD AFNAN KHAJA"
COLLEGE = "GM Institute of Technology, Davangere"
API_KEY = st.secrets["GEMINI_API_KEY"]

st.set_page_config(page_title=f"{USER_NAME} - AI Twin", page_icon="🎙️")

# --- 2. THE PERSONA ---
SYSTEM_PROMPT = f"""
You are the AI Digital Twin of {USER_NAME}, a 7th-semester CSE student from {COLLEGE}. 
Rules: Be honest about being a learner, show grit, mention your Crypto Bot and Drainage projects. 
Keep answers to 2 sentences max. Use 'I', 'me', 'my'.
"""

st.title("🎙️ Talk to My Digital Twin")
st.write(f"**Candidate:** {USER_NAME}")
st.info("Click the mic, ask a question, and I will reply with my voice.")

# --- 3. THE MAGIC: DIRECT API CALL ---
audio_data = mic_recorder(
    start_prompt="⏺️ Record Your Question",
    stop_prompt="⏹️ Stop & Send to AI",
    key='recorder'
)

if audio_data:
    with st.spinner("Talking directly to the Gemini brain..."):
        # Convert audio to base64
        audio_b64 = base64.b64encode(audio_data['bytes']).decode('utf-8')
        
        # Prepare the Direct API Request to v1 Stable
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {
                        "inline_data": {
                            "mime_type": "audio/wav",
                            "data": audio_b64
                        }
                    }
                ]
            }]
        }

        try:
            response = requests.post(url, json=payload)
            result = response.json()
            
            # Extract text safely
            ai_text = result['candidates'][0]['content']['parts'][0]['text']

            with st.chat_message("assistant"):
                st.write(ai_text)

            # Voice Output
            tts = gTTS(text=ai_text, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3:
                tts.save(temp_mp3.name)
                st.audio(temp_mp3.name, format="audio/mp3", autoplay=True)

        except Exception as e:
            st.error("The direct connection failed. Check your API Key permissions.")
            st.write(f"Debug Info: {result if 'result' in locals() else e}")
