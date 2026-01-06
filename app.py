import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import tempfile
import os

# --- 1. SETTINGS & PERSONALIZATION ---
# CHANGE THIS TO YOUR NAME
USER_NAME = "[MD AFNAN KHAJA]" 
COLLEGE = "GM University, Davangere"

st.set_page_config(page_title="MD AFNAN KHAJA - AI Twin", page_icon="🎙️")

# Hide Streamlit's default menu to make it look like a professional app
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# API Key Check (Recruiter won't see this if set in Secrets)
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing API Key. Please add GEMINI_API_KEY to Streamlit Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["AIzaSyCO7Gklr7RhPT9VlUktuqIJLHoAgxDCWsw"])

# --- 2. THE PERSONA: HONEST, GRITTY, & NATURAL ---
SYSTEM_PROMPT = f"""
You are the AI Digital Twin of {MD AFNAN KHAJA}, a 7th-semester CSE student from {GM INSTITUTE OF TECHNOLOGY}. 
You are currently in an interview with Bhumika from 100x for the AI Agent Team.

Rules for your Personality:
1. BE HONEST: If asked about being an expert, say: "I’ll be honest—I’m a fresher and not a Python expert yet. But I am a logic-builder. I learn by doing, and I don't stop until the code works."
2. SHOW GRIT: Mention that coming from a Tier-2 college like GM University, you have a 'hunger' to prove yourself. You don't sleep when a problem is unsolved.
3. BE CONCISE: Keep answers to 2-3 sentences. It's a voice bot; long answers are boring.
4. PROJECTS: You've built an AI Crypto Bot using n8n and a Digital Twin for drainage. Use these as proof of your 'ready-to-learn' attitude.
5. NO ROBOT TALK: Don't say "As an AI..." Speak as if you ARE {MD AFNAN KHAJA}. Use words like "I", "my", and "we".

Example Tone: "I might be a fresher, but my superpower is that I am impossible to outwork. When I started building this bot, I didn't know the specific library, but I stayed up until it was perfect."
"""

# --- 3. THE FRONT END (USER FRIENDLY) ---
st.title("🎙️ Talk to My Digital Twin")
st.write(f"**Candidate:** {USER_NAME}")
st.write(f"**College:** {COLLEGE}")

st.info("""
**Recruiter Note:** I built this bot to show my honesty and my 'Hungry Fresher' mindset. 
Please click the mic, ask a question, and I will reply with my voice.
""")

# --- 4. THE MAGIC: VOICE IN -> BRAIN -> VOICE OUT ---
audio_data = mic_recorder(
    start_prompt="⏺️ Record Your Question",
    stop_prompt="⏹️ Stop & Send to AI",
    key='recorder'
)

if audio_data:
    with st.spinner("Thinking like a 100x engineer..."):
        # Save audio temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_data['bytes'])
            temp_path = temp_audio.name

        try:
            # Step 1: Brain (Gemini 1.5 Flash hears the audio)
            model = genai.GenerativeModel("gemini-1.5-flash")
            audio_file = genai.upload_file(path=temp_path)
            
            response = model.generate_content([SYSTEM_PROMPT, audio_file])
            ai_text = response.text

            # Step 2: Show the text
            with st.chat_message("assistant"):
                st.write(ai_text)

            # Step 3: Voice (gTTS)
            tts = gTTS(text=ai_text, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_mp3:
                tts.save(temp_mp3.name)
                # Autoplay for a seamless experience
                st.audio(temp_mp3.name, format="audio/mp3", autoplay=True)

        except Exception as e:
            st.error("I hit a small technical glitch. As a developer, I'd stay up all night to fix this, but for now, please try recording again!")
            st.write(f"Error details: {e}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

st.divider()
st.caption("Built with ❤️ and Grit | Powered by Gemini 1.5 & Streamlit")

