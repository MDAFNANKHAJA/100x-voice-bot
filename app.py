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
import json

# --- 1. SETTINGS ---
USER_NAME = "MD AFNAN KHAJA"
COLLEGE = "GM Institute of Technology, Davangere"
SKILLS = "Python, Machine Learning, Web Development, Data Science"
INTERESTS = "AI, Deep Learning, Cloud Computing, Innovation"
PROJECTS = "Built chatbots, ML models, and web applications"
EXPERIENCE = "Internships in AI/ML, participated in hackathons"

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
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
    .stButton>button {
        border-radius: 20px;
        padding: 0.5rem 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="main-header">
    <h1>🎙️ Talk to My Digital Twin</h1>
    <h2>{USER_NAME}</h2>
    <p style='font-size: 1.1em;'>{COLLEGE}</p>
    <p style='font-size: 0.9em; opacity: 0.9;'>Ask me anything about my skills, projects, or experience!</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "audio_count" not in st.session_state:
    st.session_state.audio_count = 0
if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0

# Sidebar with info
with st.sidebar:
    st.header("📋 Profile")
    st.markdown(f"""
    **Name:** {USER_NAME}  
    **College:** {COLLEGE}  
    **Skills:** {SKILLS}  
    **Interests:** {INTERESTS}  
    **Projects:** {PROJECTS}
    """)
    
    st.divider()
    
    st.header("💬 Recent Conversations")
    if st.session_state.conversation_history:
        for i, chat in enumerate(reversed(st.session_state.conversation_history[-5:])):
            idx = len(st.session_state.conversation_history) - i
            with st.expander(f"Q{idx}: {chat['user'][:35]}..."):
                st.markdown(f"**You:** {chat['user']}")
                st.markdown(f"**AI:** {chat['ai']}")
    else:
        st.info("No conversations yet. Start talking!")
    
    st.divider()
    
    if st.button("🗑️ Clear All History", use_container_width=True):
        st.session_state.conversation_history = []
        st.session_state.total_questions = 0
        st.rerun()
    
    if st.button("📥 Download Conversation", use_container_width=True):
        if st.session_state.conversation_history:
            conversation_text = "\n\n".join([
                f"Q: {chat['user']}\nA: {chat['ai']}" 
                for chat in st.session_state.conversation_history
            ])
            st.download_button(
                "💾 Download as TXT",
                conversation_text,
                file_name="ai_twin_conversation.txt",
                mime="text/plain"
            )

# Main content area
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.subheader("🎤 Voice Input")
    st.info("💡 Click **'Start Recording'** and ask about my education, skills, projects, interests, or experience!")

with col2:
    st.metric("📊 Total Questions", st.session_state.total_questions, delta=None)

with col3:
    st.metric("💬 History", len(st.session_state.conversation_history), delta=None)

# Mic recorder
audio_data = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="🛑 Stop & Send",
    key=f"recorder_v{st.session_state.audio_count}"
)

# Process audio
if audio_data:
    st.session_state.audio_count += 1
    st.session_state.total_questions += 1
    
    progress_bar = st.progress(0, text="Starting...")
    status_container = st.empty()
    
    try:
        # STEP 1: Audio Processing
        with status_container.container():
            st.info("🎵 **Step 1/4:** Processing audio file...")
        progress_bar.progress(25, text="Processing audio...")
        
        audio_bytes = BytesIO(audio_data["bytes"])
        sound = AudioSegment.from_file(audio_bytes)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
            sound.export(wav_file.name, format="wav")
            wav_path = wav_file.name
        
        time.sleep(0.3)
        
        # STEP 2: Speech to Text
        with status_container.container():
            st.info("🗣️ **Step 2/4:** Converting speech to text...")
        progress_bar.progress(50, text="Converting speech...")
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = recognizer.record(source)
            user_text = recognizer.recognize_google(audio)
        
        status_container.success(f"✅ **You said:** '{user_text}'")
        time.sleep(0.5)
        
        # STEP 3: API Key Check
        if "GEMINI_API_KEY" not in st.secrets:
            status_container.error("⚠️ API Key not found! Add GEMINI_API_KEY to Streamlit secrets.")
            progress_bar.empty()
            st.stop()
        
        API_KEY = st.secrets["GEMINI_API_KEY"]
        
        # Build intelligent, context-aware prompt
        conversation_context = ""
        if len(st.session_state.conversation_history) > 0:
            recent_chats = st.session_state.conversation_history[-3:]
            conversation_context = "Previous conversation:\n" + "\n".join([
                f"Q: {chat['user']}\nA: {chat['ai']}" for chat in recent_chats
            ]) + "\n\n"
        
        detailed_prompt = f"""You are {USER_NAME}, a passionate and skilled student from {COLLEGE}.

COMPREHENSIVE PROFILE:
- Skills: {SKILLS}
- Interests: {INTERESTS}
- Projects: {PROJECTS}
- Experience: {EXPERIENCE}

{conversation_context}

IMPORTANT INSTRUCTIONS:
1. Answer naturally as if you're in a real conversation or interview
2. Provide specific, unique details for each question - NEVER give generic answers
3. If asked about projects, describe specific technologies and outcomes
4. If asked about skills, give concrete examples of how you've used them
5. Be enthusiastic and personable
6. Keep answers conversational (2-4 sentences)
7. Vary your responses - each answer should be different and contextual
8. Reference previous conversation if relevant

Current Question: {user_text}

Answer as {USER_NAME} with authentic, specific details:"""
        
        with status_container.container():
            st.info("🤖 **Step 3/4:** Generating intelligent AI response...")
        progress_bar.progress(75, text="Thinking...")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": detailed_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.9,  # Higher for more varied responses
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 200,
                "candidateCount": 1
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
        }
        
        response = requests.post(url, json=payload, timeout=15)
        
        # Enhanced error handling
        if response.status_code != 200:
            status_container.error(f"❌ API Error {response.status_code}")
            
            error_messages = {
                400: "Invalid request format. Check your API setup.",
                403: "API key invalid or lacks permissions. Generate new key at https://makersuite.google.com/app/apikey",
                429: "Rate limit exceeded. Please wait a moment.",
                500: "Google server error. Try again in a moment."
            }
            
            st.warning(f"💡 {error_messages.get(response.status_code, 'Unknown error occurred')}")
            
            with st.expander("🔍 View Error Details"):
                st.code(response.text)
            
            progress_bar.empty()
            os.remove(wav_path)
            st.stop()
        
        result = response.json()
        
        # Detailed response validation
        if "candidates" not in result or len(result["candidates"]) == 0:
            status_container.error("❌ No response generated")
            
            if "promptFeedback" in result:
                st.warning(f"⚠️ Blocked: {result['promptFeedback']}")
            
            with st.expander("🔍 Debug: Full API Response"):
                st.json(result)
            
            progress_bar.empty()
            os.remove(wav_path)
            st.stop()
        
        candidate = result["candidates"][0]
        
        # Check finish reason
        if candidate.get("finishReason") != "STOP":
            st.warning(f"⚠️ Response incomplete: {candidate.get('finishReason', 'Unknown')}")
        
        # Extract AI response
        if "content" not in candidate or "parts" not in candidate["content"]:
            status_container.error("❌ Invalid response structure")
            with st.expander("🔍 Debug Info"):
                st.json(candidate)
            progress_bar.empty()
            os.remove(wav_path)
            st.stop()
        
        ai_text = candidate["content"]["parts"][0]["text"].strip()
        
        # Save to conversation history
        st.session_state.conversation_history.append({
            "user": user_text,
            "ai": ai_text
        })
        
        # STEP 4: Text to Speech
        with status_container.container():
            st.info("🔊 **Step 4/4:** Generating voice response...")
        progress_bar.progress(100, text="Finalizing...")
        
        # Display response with animation
        st.markdown("---")
        st.markdown("### 💬 AI Response")
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(f"**{ai_text}**")
        
        # Generate audio
        tts = gTTS(ai_text, lang="en", slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3_file:
            tts.save(mp3_file.name)
            st.audio(mp3_file.name, autoplay=True)
            
            # Cleanup audio file
            time.sleep(1)
            try:
                os.remove(mp3_file.name)
            except:
                pass
        
        status_container.success("✅ **Complete!** Ask another question!")
        time.sleep(1)
        progress_bar.empty()
        status_container.empty()
        
        # Cleanup wav file
        os.remove(wav_path)
        
    except sr.UnknownValueError:
        status_container.error("😕 Couldn't understand the audio. Please speak clearly and try again.")
        progress_bar.empty()
    except sr.RequestError as e:
        status_container.error(f"❌ Speech recognition error: {e}")
        progress_bar.empty()
    except requests.exceptions.Timeout:
        status_container.error("⏱️ Request timed out. Please try again.")
        progress_bar.empty()
    except requests.exceptions.RequestException as e:
        status_container.error(f"🌐 Network error: {e}")
        progress_bar.empty()
    except Exception as e:
        status_container.error(f"❌ Unexpected error: {str(e)}")
        with st.expander("🔍 Error Details"):
            st.exception(e)
        progress_bar.empty()

# Sample questions
st.markdown("---")
st.markdown("### 💡 Sample Questions You Can Ask:")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **About Education:**
    - What are you studying?
    - Tell me about your college
    - What's your major?
    """)

with col2:
    st.markdown("""
    **About Skills:**
    - What programming languages do you know?
    - What are your technical skills?
    - What projects have you built?
    """)

with col3:
    st.markdown("""
    **About Experience:**
    - Do you have any internships?
    - What's your experience with AI?
    - What are your career goals?
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><b>Tips for Best Results:</b></p>
    <p>🎤 Speak clearly in a quiet environment | 💬 Ask specific questions | 🔄 Each answer is unique and contextual</p>
    <p style='margin-top: 1rem; font-size: 0.9em;'>Built with ❤️ using Streamlit • Powered by Google Gemini AI</p>
</div>
""", unsafe_allow_html=True)
