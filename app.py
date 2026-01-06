import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import tempfile
import os

# --- 1. SETTINGS & PERSONALIZATION ---
USER_NAME = "MD AFNAN KHAJA" 
COLLEGE = "GM Institute of Technology, Davangere"

st.set_page_config(page_title="MD AFNAN KHAJA - AI Twin", page_icon="🎙️")

# Professional UI
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# API Key Check
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key in Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- 2. THE PERSONA ---
SYSTEM_PROMPT = f"""
You are the AI Digital Twin of {USER_NAME}, a 7th-semester CSE student from {COLLEGE}. 
You are being interviewed by Bhumika from 100x for the AI Agent Team.

Rules:
1. BE HONEST: Say you are a logic-builder and a learner, not a Python expert.
2. SHOW GRIT: Mention your hunger to prove yourself coming from a Tier-2 college in Davangere.
3. PROJECTS: Mention your AI Crypto Bot and Drainage Digital Twin.
4. PERSONA: Speak as {USER_NAME} using "I", "me", "my". Keep it to 2 sentences.
"""

# --- 3. THE FRONT END ---
st.title("🎙️ Talk to My Digital Twin")
st.write(f"**Candidate:** {USER_NAME}")
st.info("Click the mic, ask a question, and wait for my voice response.")

# --- 4. THE MAGIC: VOICE INTERACTION ---
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
            # THE FIX: Explicitly calling the stable model
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Upload audio
            audio_file = genai.upload_file(path=temp_path)
            
            # Generate response
            response = model.generate_content([SYSTEM_PROMPT, audio_file])
            
            if response.text:
                ai_text = response.text
                with st.chat_message("assistant"):
                    st.write(ai_text)

                # Voice Output
                tts = gTTS(text=ai_text, lang='en')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3:
                    tts.save(temp_mp3.name)
                    st.audio(temp_mp3.name, format="audio/mp3", autoplay=True)
            else:
                st.warning("Could not generate a response. Please speak again.")

        except Exception as e:
            st.error("Technical glitch! Please check the logs.")
            st.write(f"Error: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

st.divider()
st.caption("Built with ❤️ and Grit | Powered by Gemini 1.5 & Streamlit")
