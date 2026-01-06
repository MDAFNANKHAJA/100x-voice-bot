import streamlit as st
import requests
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import tempfile
import os
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
import time

# --- 1. SETTINGS ---
USER_NAME = "MD AFNAN KHAJA"
COLLEGE = "GM Institute of Technology, Davangere"
SKILLS = "Python, Machine Learning, Web Development"
INTERESTS = "AI, Data Science, Innovation"

# Page config
st.set_page_config(
    page_title=f"{USER_NAME} - AI Twin", 
    page_icon="🎙️",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        animation: fadeIn 0.5s;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .status-box {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="main-header">
    <h1>🎙️ Talk to My Digital Twin</h1>
    <h3>{USER_NAME}</h3>
    <p>{COLLEGE}</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "audio_count" not in st.session_state:
    st.session_state.audio_count = 0

# Sidebar with info
with st.sidebar:
    st.header("📋 About Me")
    st.write(f"**Name:** {USER_NAME}")
    st.write(f"**College:** {COLLEGE}")
    st.write(f"**Skills:** {SKILLS}")
    st.write(f"**Interests:** {INTERESTS}")
    
    st.divider()
    
    st.header("💬 Conversation History")
    if st.session_state.conversation_history:
        for i, chat in enumerate(st.session_state.conversation_history[-5:]):
            with st.expander(f"Q{i+1}: {chat['user'][:30]}..."):
                st.write(f"**You:** {chat['user']}")
                st.write(f"**AI:** {chat['ai']}")
    else:
        st.info("No conversations yet. Start talking!")
    
    if st.button("🗑️ Clear History"):
        st.session_state.conversation_history = []
        st.rerun()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎤 Voice Input")
    st.info("Click 'Start Recording' to ask me anything about my background, skills, or experience!")
    
    # Mic recorder
    audio_data = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="🛑 Stop & Send",
        key=f"recorder_v{st.session_state.audio_count}"
    )

with col2:
    st.subheader("📊 Stats")
    st.metric("Conversations", len(st.session_state.conversation_history))
    st.metric("Status", "🟢 Ready" if not audio_data else "🔴 Processing")

# Process audio
if audio_data:
    st.session_state.audio_count += 1
    
    with st.spinner("Processing your request..."):
        try:
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # STEP 1: Audio Processing
            status_text.markdown("**Step 1/4:** 🎵 Processing audio file...")
            progress_bar.progress(25)
            
            audio_bytes = BytesIO(audio_data["bytes"])
            sound = AudioSegment.from_file(audio_bytes)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
                sound.export(wav_file.name, format="wav")
                wav_path = wav_file.name
            
            time.sleep(0.3)
            
            # STEP 2: Speech to Text
            status_text.markdown("**Step 2/4:** 🗣️ Converting speech to text...")
            progress_bar.progress(50)
            
            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = recognizer.record(source)
                user_text = recognizer.recognize_google(audio)
            
            st.success(f"✅ **You said:** '{user_text}'")
            time.sleep(0.3)
            
            # STEP 3: Get API Key
            if "GEMINI_API_KEY" not in st.secrets:
                st.error("⚠️ API Key not found! Please add GEMINI_API_KEY to your secrets.")
                st.stop()
            
            API_KEY = st.secrets["GEMINI_API_KEY"]
            
            # Build context-aware prompt
            context = f"""You are {USER_NAME}, a student from {COLLEGE}.
Your skills include: {SKILLS}
Your interests are: {INTERESTS}

Answer questions as if you are introducing yourself in an interview or conversation.
Be professional, friendly, and concise (2-3 sentences max).
If asked about specific projects or achievements, be creative but realistic for a college student."""
            
            status_text.markdown("**Step 3/4:** 🤖 Generating AI response...")
            progress_bar.progress(75)
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"{context}\n\nQuestion: {user_text}"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 150
                }
            }
            
            response = requests.post(url, json=payload, timeout=10)
            result = response.json()
            
            if "candidates" in result and len(result["candidates"]) > 0:
                ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Save to conversation history
                st.session_state.conversation_history.append({
                    "user": user_text,
                    "ai": ai_text
                })
                
                # STEP 4: Text to Speech
                status_text.markdown("**Step 4/4:** 🔊 Generating voice response...")
                progress_bar.progress(100)
                
                # Display response
                st.markdown("### 💬 AI Response")
                with st.chat_message("assistant"):
                    st.write(ai_text)
                
                # Generate audio
                tts = gTTS(ai_text, lang="en", slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3:
                    tts.save(mp3.name)
                    st.audio(mp3.name, autoplay=True)
                    os.remove(mp3.name)
                
                status_text.markdown("✅ **Complete!** Ask another question or review the conversation history.")
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()
                
            else:
                st.error("❌ Gemini API did not return a valid response.")
                with st.expander("🔍 View API Response"):
                    st.json(result)
            
            # Cleanup
            os.remove(wav_path)
            
        except sr.UnknownValueError:
            st.error("😕 Sorry, I couldn't understand the audio. Please try speaking more clearly.")
        except sr.RequestError as e:
            st.error(f"❌ Speech recognition service error: {e}")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {e}")
            with st.expander("🔍 Error Details"):
                st.exception(e)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>💡 <b>Tips:</b> Speak clearly and ask about my education, skills, projects, or interests!</p>
    <p>Built with Streamlit • Powered by Google Gemini</p>
</div>
""", unsafe_allow_html=True)
