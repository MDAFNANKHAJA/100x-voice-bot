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

# Professional UI Tweak
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# API Key Check
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key. Please add GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

# --- THE FIX: FORCE API VERSION V1 ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- 2. THE PERSONA ---
SYSTEM_PROMPT = f"""
You are the AI Digital Twin of {USER_NAME}, a 7th-semester CSE student from {COLLEGE}. 
You are being interviewed by Bhumika from 100x for the AI Agent Team.

Rules:
1. BE HONEST: Say you are a learner/logic-builder, not yet a Python expert.
2. SHOW GRIT: Mention your hunger to prove yourself coming from a Tier-2 college.
3. CONCISE: Keep answers to 2 sentences max.
4. PROJECTS: Mention your AI Crypto Bot (n8n) and Drainage Digital Twin.
5. PERSONA: Speak as {USER_NAME} using "I", "me", "my".
"""

# --- 3. THE FRONT END ---
st.title("🎙️ Talk to My Digital Twin")
st.write(f"**Candidate:** {USER_NAME}")
st.write(f"**College:** {COLLEGE}")

st.info("Click the mic, ask a question, and I will reply with my voice.")

# --- 4. THE MAGIC: VOICE INTERACTION ---
audio_data = mic_recorder(
    start_prompt="⏺️ Record Your Question",
    stop_prompt="⏹️ Stop & Send to AI",
    key='recorder'
)

if audio_data:
    with st.spinner("Thinking like a 100x engineer..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_data['bytes'])
            temp_path = temp_audio.name

        try:
            # FIX: Use the stable model call
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Upload and process
            audio_file = genai.upload_file(path=temp_path)
            
            # Generate response
            response = model.generate_content([SYSTEM_PROMPT, audio_file])
            
            if response:
                ai_text = response.text

                # Show text
                with st.chat_message("assistant"):
                    st.write(ai_text)

                # Voice Output
                tts = gTTS(text=ai_text, lang='en')
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3:
                    tts.save(temp_mp3.name)
                    st.audio(temp_mp3.name, format="audio/mp3", autoplay=True)
            else:
                st.warning("I heard you, but the brain didn't reply. Try again!")

        except Exception as e:
            # Check if it's the 404 error again and provide a specific fix
            st.error("Technical glitch!")
            st.write(f"Debug Info: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

st.divider()
st.caption("Built with ❤️ and Grit | Powered by Gemini 1.5 & Streamlit")
