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

# --- PERSONAL PROFILE ---
USER_NAME = "MD AFNAN KHAJA"
COLLEGE = "GM Institute of Technology, Davangere"

# Detailed personal information for authentic responses
LIFE_STORY = """I'm from Davangere, Karnataka, and grew up fascinated by technology. 
I pursued Computer Science Engineering at GM Institute of Technology, where I discovered 
my passion for AI and machine learning. I've spent countless hours building projects, 
from chatbots to ML models, always pushing to learn more."""

SUPERPOWER = """My #1 superpower is rapid learning and adaptation. I can pick up new 
technologies and frameworks incredibly quickly. Whether it's a new programming language, 
ML framework, or cloud platform, I dive deep, build projects, and master it faster than 
most people expect."""

GROWTH_AREAS = """1. System Design & Architecture - I want to build scalable, production-grade 
systems. 2. Advanced Deep Learning - Specifically transformers and computer vision at scale. 
3. Leadership & Communication - I want to effectively lead technical teams and communicate 
complex ideas simply."""

MISCONCEPTION = """People often think I'm purely technical and all about code. But I'm 
actually very creative and love the human side of technology - understanding user needs, 
designing intuitive experiences, and building solutions that genuinely help people."""

PUSH_BOUNDARIES = """I constantly take on projects beyond my current skill level. I participate 
in hackathons, contribute to open-source, and build real-world applications that force me to 
learn. I also set aggressive deadlines that push me out of my comfort zone and make me find 
creative solutions under pressure."""

TECHNICAL_SKILLS = "Python, Machine Learning, Deep Learning, Web Development (Flask, Streamlit, FastAPI), Data Science, NLP, Computer Vision, Cloud Computing (AWS, GCP), Git, SQL, API Development"

PROJECTS_PORTFOLIO = """AI Voice Bot, Sentiment Analysis System, Real-time Object Detection App, 
Chatbot with NLP, Predictive Analytics Dashboard, Automated Resume Parser, Student Performance 
Prediction System"""

INTERESTS = "Artificial Intelligence, Machine Learning, Innovation, Problem Solving, Building Products"

# Page config
st.set_page_config(
    page_title=f"{USER_NAME} - AI Voice Bot", 
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .info-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
    }
    .chat-bubble {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        animation: slideIn 0.5s ease-out;
    }
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stButton>button {
        border-radius: 25px;
        padding: 0.6rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .question-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 0.5rem 0;
        transition: all 0.3s;
    }
    .question-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 8px rgba(102,126,234,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="main-header">
    <h1>🎙️ AI Voice Bot Interview</h1>
    <h2>{USER_NAME}</h2>
    <p style='font-size: 1.2em; margin-top: 1rem;'>{COLLEGE}</p>
    <p style='font-size: 1em; opacity: 0.95; margin-top: 0.5rem;'>
        Ask me anything about my life, skills, or aspirations!
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "audio_count" not in st.session_state:
    st.session_state.audio_count = 0

# Function to call Gemini API
def call_gemini_api(prompt, api_key):
    """Call Google Gemini API"""
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.85,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 250
        }
    }
    
    response = requests.post(url, json=payload, timeout=15)
    return response

# Function to call Claude API
def call_claude_api(prompt, api_key):
    """Call Anthropic Claude API"""
    url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 250,
        "messages": [{
            "role": "user",
            "content": prompt
        }]
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    return response

# Function to call OpenAI API
def call_openai_api(prompt, api_key):
    """Call OpenAI ChatGPT API"""
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "user",
            "content": prompt
        }],
        "temperature": 0.85,
        "max_tokens": 250
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    return response

# Sidebar
with st.sidebar:
    st.markdown("### 🤖 AI Provider Selection")
    
    ai_provider = st.radio(
        "Choose AI Provider:",
        ["Gemini (Google)", "Claude (Anthropic)", "ChatGPT (OpenAI)"],
        help="Select which AI to use for responses"
    )
    
    st.markdown("---")
    
    st.markdown("### 👤 About Me")
    st.markdown(f"**Name:** {USER_NAME}")
    st.markdown(f"**College:** {COLLEGE}")
    
    st.markdown("---")
    
    st.markdown("### 🎯 Quick Stats")
    st.markdown(f"""
    <div class="metric-box">
        <h3>{len(st.session_state.conversation_history)}</h3>
        <p>Questions Asked</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 💬 Conversation History")
    if st.session_state.conversation_history:
        for i, chat in enumerate(reversed(st.session_state.conversation_history[-5:])):
            with st.expander(f"Q{len(st.session_state.conversation_history)-i}: {chat['user'][:30]}..."):
                st.markdown(f"**Q:** {chat['user']}")
                st.markdown(f"**A:** {chat['ai']}")
    else:
        st.info("Start asking questions!")
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.conversation_history = []
        st.rerun()

# Main content
st.markdown("### 🎤 Ask Me Anything!")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
    <div class="info-card">
        <h4>📢 How to Use:</h4>
        <ol>
            <li>Select AI Provider in sidebar (Currently: <b>{ai_provider}</b>)</li>
            <li>Click "🎤 Start Recording"</li>
            <li>Ask your question clearly</li>
            <li>Click "🛑 Stop & Send"</li>
            <li>Listen to my response!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <h4>💡 Status:</h4>
        <p style='font-size: 1.2em;'>🟢 Ready to Chat!</p>
    </div>
    """, unsafe_allow_html=True)

# Microphone recorder
audio_data = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="🛑 Stop & Send",
    key=f"recorder_{st.session_state.audio_count}"
)

# Suggested questions
st.markdown("---")
st.markdown("### 💭 Suggested Questions:")

questions = [
    "What should we know about your life story in a few sentences?",
    "What's your #1 superpower?",
    "What are the top 3 areas you'd like to grow in?",
    "What misconception do your coworkers have about you?",
    "How do you push your boundaries and limits?",
    "What are your technical skills?",
    "Tell me about your projects",
    "What are your career goals?"
]

col1, col2 = st.columns(2)
for i, q in enumerate(questions):
    with col1 if i % 2 == 0 else col2:
        st.markdown(f"""
        <div class="question-card">
            <small><b>Q{i+1}:</b></small><br>
            {q}
        </div>
        """, unsafe_allow_html=True)

# Process audio
if audio_data:
    st.session_state.audio_count += 1
    
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0, text="Initializing...")
        status_text = st.empty()
    
    try:
        # Step 1: Audio Processing
        status_text.info("🎵 **Step 1/4:** Processing audio...")
        progress_bar.progress(25, text="Processing audio...")
        
        audio_bytes = BytesIO(audio_data["bytes"])
        sound = AudioSegment.from_file(audio_bytes)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
            sound.export(wav_file.name, format="wav")
            wav_path = wav_file.name
        
        # Step 2: Speech to Text
        status_text.info("🗣️ **Step 2/4:** Converting speech to text...")
        progress_bar.progress(50, text="Understanding your question...")
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = recognizer.record(source)
            user_text = recognizer.recognize_google(audio)
        
        status_text.success(f"✅ **You asked:** *'{user_text}'*")
        time.sleep(0.5)
        
        # Step 3: Generate Response
        status_text.info(f"🤖 **Step 3/4:** Generating response using {ai_provider}...")
        progress_bar.progress(75, text="Thinking...")
        
        # Check API key based on provider
        api_key_name = None
        if "Gemini" in ai_provider:
            api_key_name = "GEMINI_API_KEY"
        elif "Claude" in ai_provider:
            api_key_name = "CLAUDE_API_KEY"
        elif "ChatGPT" in ai_provider:
            api_key_name = "OPENAI_API_KEY"
        
        if api_key_name not in st.secrets:
            status_text.error(f"⚠️ {api_key_name} not found in secrets!")
            st.error(f"""
            **Setup Instructions:**
            1. Go to your Streamlit Cloud app settings
            2. Click on "Secrets"
            3. Add: `{api_key_name} = "your-key-here"`
            4. Redeploy the app
            """)
            st.stop()
        
        api_key = st.secrets[api_key_name]
        
        # Build conversation context
        context = ""
        if st.session_state.conversation_history:
            recent = st.session_state.conversation_history[-2:]
            context = "Previous conversation:\n" + "\n".join([
                f"Q: {c['user']}\nA: {c['ai']}" for c in recent
            ]) + "\n\n"
        
        # Create intelligent prompt
        prompt = f"""You are {USER_NAME}, a passionate Computer Science student from {COLLEGE}.

COMPREHENSIVE PROFILE:

LIFE STORY: {LIFE_STORY}

#1 SUPERPOWER: {SUPERPOWER}

TOP 3 GROWTH AREAS: {GROWTH_AREAS}

MISCONCEPTION: {MISCONCEPTION}

PUSHING BOUNDARIES: {PUSH_BOUNDARIES}

TECHNICAL SKILLS: {TECHNICAL_SKILLS}

PROJECTS: {PROJECTS_PORTFOLIO}

INTERESTS: {INTERESTS}

{context}

INSTRUCTIONS:
1. Answer as {USER_NAME} authentically and personally
2. Use first-person ("I", "my", "me")
3. Be conversational, enthusiastic, and genuine
4. Provide specific examples and details
5. Keep responses 3-5 sentences
6. Make each answer unique and contextual
7. Show personality and passion

CURRENT QUESTION: {user_text}

Respond as {USER_NAME}:"""
        
        # Call appropriate API
        response = None
        ai_text = None
        
        try:
            if "Gemini" in ai_provider:
                response = call_gemini_api(prompt, api_key)
                
                if response.status_code == 200:
                    result = response.json()
                    if "candidates" in result and result["candidates"]:
                        ai_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                
            elif "Claude" in ai_provider:
                response = call_claude_api(prompt, api_key)
                
                if response.status_code == 200:
                    result = response.json()
                    if "content" in result:
                        ai_text = result["content"][0]["text"].strip()
            
            elif "ChatGPT" in ai_provider:
                response = call_openai_api(prompt, api_key)
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result:
                        ai_text = result["choices"][0]["message"]["content"].strip()
            
            # Handle errors
            if response and response.status_code != 200:
                status_text.error(f"❌ API Error: {response.status_code}")
                
                error_solutions = {
                    400: "Invalid request. Check your API key format.",
                    401: "Authentication failed. Your API key is invalid.",
                    403: "Access denied. Check API key permissions.",
                    404: "Endpoint not found. The API URL or model might be wrong.",
                    429: "Rate limit exceeded. Wait a moment and try again.",
                    500: "Server error. Try again in a moment.",
                    503: "Service unavailable. Try again later."
                }
                
                st.error(f"**Error:** {error_solutions.get(response.status_code, 'Unknown error')}")
                
                with st.expander("🔍 Debug Info"):
                    st.write(f"**Status Code:** {response.status_code}")
                    st.write(f"**Response:** {response.text}")
                    st.write(f"**Provider:** {ai_provider}")
                
                st.stop()
            
            if not ai_text:
                status_text.error("❌ No response generated")
                st.error("The AI didn't generate a response. Try again.")
                st.stop()
            
        except Exception as api_error:
            status_text.error(f"❌ API Error: {str(api_error)}")
            st.error(f"Failed to connect to {ai_provider}. Check your API key and internet connection.")
            with st.expander("🔍 Error Details"):
                st.exception(api_error)
            st.stop()
        
        # Save conversation
        st.session_state.conversation_history.append({
            "user": user_text,
            "ai": ai_text
        })
        
        # Step 4: Text to Speech
        status_text.info("🔊 **Step 4/4:** Generating voice...")
        progress_bar.progress(100, text="Finalizing...")
        
        # Display response
        st.markdown("---")
        st.markdown(f"### 💬 My Response (via {ai_provider}):")
        st.markdown(f"""
        <div class="chat-bubble">
            <p style='font-size: 1.1em; margin: 0;'>{ai_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate audio
        tts = gTTS(ai_text, lang="en", slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3:
            tts.save(mp3.name)
            st.audio(mp3.name, autoplay=True)
            time.sleep(0.5)
            try:
                os.remove(mp3.name)
            except:
                pass
        
        status_text.success("✅ **Response complete!** Ask another question!")
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        # Cleanup
        os.remove(wav_path)
        
    except sr.UnknownValueError:
        status_text.error("😕 Couldn't understand the audio. Please speak clearly.")
        progress_bar.empty()
    except sr.RequestError as e:
        status_text.error(f"❌ Speech recognition error: {e}")
        progress_bar.empty()
    except Exception as e:
        status_text.error(f"❌ Error: {str(e)}")
        with st.expander("🔍 Full Error"):
            st.exception(e)
        progress_bar.empty()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; color: #666;'>
    <p style='font-size: 1.1em; margin-bottom: 1rem;'>
        <b>💡 Pro Tips:</b> Speak clearly • Use a quiet environment • Ask specific questions
    </p>
    <p style='font-size: 0.95em;'>
        Built with ❤️ by {name} | Supports Gemini, Claude & ChatGPT
    </p>
</div>
""".format(name=USER_NAME), unsafe_allow_html=True)
