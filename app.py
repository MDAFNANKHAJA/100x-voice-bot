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

# Detailed personal responses
PROFILE = {
    "life_story": f"I'm {USER_NAME} from Davangere, Karnataka. I'm pursuing Computer Science at {COLLEGE}, where I discovered my passion for AI and machine learning. I love building innovative projects and constantly pushing myself to learn cutting-edge technologies!",
    
    "superpower": "My #1 superpower is rapid learning and adaptation. I can master new technologies, frameworks, and programming languages incredibly quickly - I dive deep, build real projects, and learn faster than most people expect!",
    
    "growth_areas": "I want to grow in three areas: First, System Design for building scalable architectures. Second, Advanced Deep Learning with transformers and computer vision. Third, Leadership and Communication to effectively lead technical teams.",
    
    "misconception": "People think I'm purely technical and all about code. But I'm actually very creative and passionate about the human side of technology - understanding users, designing intuitive experiences, and building solutions that genuinely help people!",
    
    "push_boundaries": "I constantly take on projects beyond my skill level! I participate in hackathons, contribute to open-source projects, and build real-world applications. I set aggressive deadlines that force me to learn and find creative solutions under pressure!",
    
    "skills": "I'm proficient in Python, Machine Learning, Deep Learning, Web Development with Flask and Streamlit, Data Science, NLP, Computer Vision, and Cloud Computing on AWS and GCP!",
    
    "projects": "I've built an AI Voice Bot, Sentiment Analysis System, Real-time Object Detection App, NLP Chatbot, Predictive Analytics Dashboard, and several other ML projects that solve real problems!"
}

# --- 1. THE BRAINS: STABLE API FUNCTIONS ---

def call_gemini_api(prompt, api_key):
    """Stable 2026 Google Gemini Pro Endpoint"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 500
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
    }
    return requests.post(url, json=payload, timeout=20)

def call_claude_api(prompt, api_key):
    """Stable 2026 Anthropic Claude Endpoint"""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}]
    }
    return requests.post(url, json=payload, headers=headers, timeout=20)

def call_openai_api(prompt, api_key):
    """Stable 2026 OpenAI GPT Endpoint"""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-3.5-turbo",  # More stable and free-tier friendly
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.9
    }
    return requests.post(url, json=payload, headers=headers, timeout=20)

def get_fallback_response(question):
    """Smart fallback based on question keywords"""
    q = question.lower()
    
    if any(word in q for word in ["life", "story", "background", "about you", "introduce", "tell me about"]):
        return PROFILE["life_story"]
    elif any(word in q for word in ["superpower", "strength", "best at", "good at", "excel"]):
        return PROFILE["superpower"]
    elif any(word in q for word in ["grow", "growth", "improve", "learn", "development", "areas", "weak"]):
        return PROFILE["growth_areas"]
    elif any(word in q for word in ["misconception", "misunderstand", "wrong", "think", "assume"]):
        return PROFILE["misconception"]
    elif any(word in q for word in ["boundaries", "limits", "push", "challenge", "overcome"]):
        return PROFILE["push_boundaries"]
    elif any(word in q for word in ["skill", "technical", "technologies", "know", "programming"]):
        return PROFILE["skills"]
    elif any(word in q for word in ["project", "built", "created", "developed", "work"]):
        return PROFILE["projects"]
    else:
        return f"Great question! I'm {USER_NAME}, a passionate Computer Science student at {COLLEGE}. I specialize in AI, Machine Learning, and building innovative solutions. I'm always excited to discuss technology and problem-solving!"

def extract_ai_response(response, provider):
    """Safely extract text from API response"""
    try:
        result = response.json()
        
        if "Gemini" in provider:
            # Check for errors first
            if "error" in result:
                return None, f"Gemini Error: {result['error'].get('message', 'Unknown')}"
            
            # Check for content blocks
            if "promptFeedback" in result and "blockReason" in result["promptFeedback"]:
                return None, f"Content blocked: {result['promptFeedback']['blockReason']}"
            
            # Extract text
            if "candidates" in result and result["candidates"]:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    return candidate["content"]["parts"][0]["text"].strip(), None
            return None, "No candidates in response"
        
        elif "Claude" in provider:
            if "error" in result:
                return None, f"Claude Error: {result['error'].get('message', 'Unknown')}"
            
            if "content" in result and result["content"]:
                return result["content"][0]["text"].strip(), None
            return None, "No content in response"
        
        elif "ChatGPT" in provider:
            if "error" in result:
                return None, f"OpenAI Error: {result['error'].get('message', 'Unknown')}"
            
            if "choices" in result and result["choices"]:
                return result["choices"][0]["message"]["content"].strip(), None
            return None, "No choices in response"
        
    except Exception as e:
        return None, f"Parse error: {str(e)}"
    
    return None, "Unknown error"

# --- 2. STREAMLIT UI SETUP ---
st.set_page_config(page_title=f"{USER_NAME} AI Voice Bot", page_icon="🎙️", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-bubble {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Sidebar
with st.sidebar:
    st.markdown("### 🤖 AI Provider")
    ai_provider = st.radio(
        "Select AI Brain:",
        ["Gemini (Google)", "Claude (Anthropic)", "ChatGPT (OpenAI)"],
        help="Choose which AI to use"
    )
    
    # Show which key is needed
    if "Gemini" in ai_provider:
        key_needed = "GEMINI_API_KEY"
    elif "Claude" in ai_provider:
        key_needed = "CLAUDE_API_KEY"
    else:
        key_needed = "OPENAI_API_KEY"
    
    if key_needed in st.secrets:
        st.success(f"✅ {key_needed} found!")
    else:
        st.error(f"⚠️ {key_needed} not found!")
        st.info("Add it to Streamlit Secrets")
    
    st.markdown("---")
    st.markdown("### 💬 History")
    st.metric("Questions Asked", len(st.session_state.conversation))
    
    if st.button("🗑️ Clear History"):
        st.session_state.conversation = []
        st.rerun()

# Header
st.markdown(f"""
<div class="main-header">
    <h1>🎙️ AI Voice Bot Interview</h1>
    <h2>{USER_NAME}</h2>
    <p>{COLLEGE}</p>
</div>
""", unsafe_allow_html=True)

st.info("🎤 Click 'Start Recording' below, ask your question, then click 'Stop & Send'")

# Sample questions
with st.expander("💡 Sample Questions to Ask"):
    st.markdown("""
    - What should we know about your life story in a few sentences?
    - What's your #1 superpower?
    - What are the top 3 areas you'd like to grow in?
    - What misconception do your coworkers have about you?
    - How do you push your boundaries and limits?
    - What are your technical skills?
    - Tell me about your projects
    """)

# --- 3. THE MAGIC: INTERACTION LOGIC ---
audio_data = mic_recorder(
    start_prompt="🎤 Start Recording", 
    stop_prompt="🛑 Stop & Send", 
    key="recorder_vFinal"
)

if audio_data:
    progress_bar = st.progress(0, text="Processing...")
    status = st.empty()
    
    try:
        # STEP 1: Audio to Text
        status.info("🎵 Step 1/4: Processing audio...")
        progress_bar.progress(25)
        
        audio_bytes = BytesIO(audio_data["bytes"])
        sound = AudioSegment.from_file(audio_bytes)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as wav_file:
            sound.export(wav_file.name, format="wav")
            wav_path = wav_file.name

        # STEP 2: Speech Recognition
        status.info("🗣️ Step 2/4: Converting speech to text...")
        progress_bar.progress(50)
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            audio = recognizer.record(source)
            user_text = recognizer.recognize_google(audio)
        
        status.success(f"✅ You asked: '{user_text}'")
        time.sleep(0.5)
        
        # STEP 3: Get AI Response
        status.info(f"🤖 Step 3/4: Getting response from {ai_provider}...")
        progress_bar.progress(75)
        
        # Build comprehensive prompt
        full_prompt = f"""You are {USER_NAME}, a passionate Computer Science student from {COLLEGE}.

PROFILE:
- Life Story: {PROFILE['life_story']}
- #1 Superpower: {PROFILE['superpower']}
- Growth Areas: {PROFILE['growth_areas']}
- Misconception: {PROFILE['misconception']}
- Push Boundaries: {PROFILE['push_boundaries']}
- Skills: {PROFILE['skills']}
- Projects: {PROFILE['projects']}

Answer this question as {USER_NAME} in first person, authentically and conversationally (3-4 sentences):
{user_text}"""
        
        ai_text = None
        error_msg = None
        
        # Try API call
        try:
            # Check if API key exists
            if key_needed not in st.secrets:
                status.warning(f"⚠️ {key_needed} not found. Using smart fallback...")
                ai_text = get_fallback_response(user_text)
            else:
                api_key = st.secrets[key_needed]
                
                # Call appropriate API
                if "Gemini" in ai_provider:
                    response = call_gemini_api(full_prompt, api_key)
                elif "Claude" in ai_provider:
                    response = call_claude_api(full_prompt, api_key)
                else:
                    response = call_openai_api(full_prompt, api_key)
                
                # Check response status
                if response.status_code != 200:
                    error_msg = f"API Error {response.status_code}: {response.text[:200]}"
                    status.warning(f"⚠️ {error_msg}")
                    ai_text = get_fallback_response(user_text)
                else:
                    # Extract response
                    ai_text, error = extract_ai_response(response, ai_provider)
                    
                    if not ai_text:
                        status.warning(f"⚠️ {error} - Using smart fallback...")
                        ai_text = get_fallback_response(user_text)
                        
                        # Show debug info
                        with st.expander("🔍 Debug Info (Optional)"):
                            st.json(response.json())
        
        except Exception as api_error:
            status.warning(f"⚠️ Connection failed. Using smart fallback...")
            ai_text = get_fallback_response(user_text)
            
            with st.expander("🔍 Technical Details (Optional)"):
                st.error(f"Error: {str(api_error)}")
        
        # Ensure we have a response
        if not ai_text:
            ai_text = get_fallback_response(user_text)
        
        # Save to history
        st.session_state.conversation.append({
            "question": user_text,
            "answer": ai_text,
            "provider": ai_provider
        })
        
        # STEP 4: Text to Speech
        status.info("🔊 Step 4/4: Generating voice response...")
        progress_bar.progress(100)
        
        # Display response
        st.markdown("---")
        st.markdown(f"### 💬 Response (via {ai_provider}):")
        st.markdown(f"""
        <div class="chat-bubble">
            <p style='font-size: 1.1em; margin: 0;'><strong>Q:</strong> {user_text}</p>
            <p style='font-size: 1.1em; margin-top: 1rem;'><strong>A:</strong> {ai_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate and play audio
        tts = gTTS(ai_text, lang="en", slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3:
            tts.save(mp3.name)
            st.audio(mp3.name, autoplay=True)
            time.sleep(0.5)
            try:
                os.remove(mp3.name)
            except:
                pass
        
        status.success("✅ Complete! Ask another question!")
        time.sleep(1)
        progress_bar.empty()
        status.empty()
        
        # Cleanup
        os.remove(wav_path)

    except sr.UnknownValueError:
        status.error("😕 Couldn't understand the audio. Please speak clearly and try again.")
        progress_bar.empty()
    except sr.RequestError as e:
        status.error(f"❌ Speech recognition error: {e}")
        progress_bar.empty()
    except Exception as e:
        status.error(f"❌ Unexpected error: {str(e)}")
        progress_bar.empty()

# Show conversation history
if st.session_state.conversation:
    st.markdown("---")
    st.markdown("### 📜 Conversation History")
    
    for i, conv in enumerate(reversed(st.session_state.conversation[-3:])):
        with st.expander(f"Q{len(st.session_state.conversation)-i}: {conv['question'][:50]}..."):
            st.markdown(f"**Question:** {conv['question']}")
            st.markdown(f"**Answer:** {conv['answer']}")
            st.caption(f"Answered by: {conv['provider']}")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>💡 Tips:</strong> Speak clearly • Use quiet environment • Ask specific questions</p>
    <p>Built with ❤️ by {USER_NAME} | Supports Gemini, Claude & ChatGPT</p>
</div>
""", unsafe_allow_html=True)
