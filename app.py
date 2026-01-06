import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import tempfile
import os

# --- 1. SETTINGS ---
USER_NAME = "MD AFNAN KHAJA" 
COLLEGE = "GM Institute of Technology, Davangere"

st.set_page_config(page_title=f"{USER_NAME} - AI Twin", page_icon="🎙️")

# API Key Check
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- 2. THE PERSONA ---
SYSTEM_PROMPT = f"""
You are the AI Digital Twin of {USER_NAME}, a 7th-semester CSE student from {COLLEGE}. 
Rules: Be honest, show grit, mention your Crypto Bot and Drainage projects. 
Keep answers to 2-3 sentences max. Use 'I', 'me', 'my'.
"""

# --- 3. THE FRONT END ---
st.title("🎙️ Talk to My Digital Twin")
st.write(f"**Candidate:** {USER_NAME}")
st.info("Click the mic, ask a question, and I will reply with my voice.")

# --- 4. THE MAGIC ---
audio_data = mic_recorder(
    start_prompt="⏺️ Record Your Question",
    stop_prompt="⏹️ Stop & Send to AI",
    key='recorder'
)

if audio_data:
    with st.spinner("Processing..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_data['bytes'])
            temp_path = temp_audio.name

        try:
            # FIX: Using the absolute model name to bypass the 404
            model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
            
            audio_file = genai.upload_file(path=temp_path)
            
            # Generate response
            response = model.generate_content([SYSTEM_PROMPT, audio_file])
            
            if response and response.text:
                ai_text = response.text
                with st.chat_message("assistant"):
                    st.write(ai_text)

                # Voice Output
                tts = gTTS(text=ai_text, lang='en')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3:
                    tts.save(temp_mp3.name)
                    st.audio(temp_mp3.name, format="audio/mp3", autoplay=True)
            else:
                st.warning("I processed the audio but couldn't generate text. Please try again!")

        except Exception as e:
            st.error("Still hitting a connection glitch!")
            st.write(f"Technical Log: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

st.divider()
st.caption("Built with ❤️ and Grit | Powered by Gemini 1.5 & Streamlit")
