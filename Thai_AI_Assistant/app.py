import streamlit as st
import numpy as np
import ollama
from faster_whisper import WhisperModel
import io
import os
import asyncio
import edge_tts
import nest_asyncio
from streamlit_mic_recorder import mic_recorder

# Apply nest_asyncio to allow async execution in Streamlit
nest_asyncio.apply()

# --- Page Configuration ---
st.set_page_config(
    page_title="Local Thai AI Assistant (Edge TTS)",
    page_icon="🤖",
    layout="wide"
)

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    .stChatFloatingInputContainer { bottom: 20px; }
    .user-message { background-color: #E6F3FF; padding: 10px; border-radius: 10px; margin: 5px 0; }
    .assistant-message { background-color: #F0F0F0; padding: 10px; border-radius: 10px; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

# --- Model Loading (Cached) ---
@st.cache_resource
def load_whisper_model():
    # Load Faster Whisper Model (Small is a good balance)
    # Check for GPU
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if torch.cuda.is_available() else "int8"
    return WhisperModel("small", device=device, compute_type=compute_type)

# Initialize STT Model only (TTS is API-based now)
try:
    with st.spinner("Loading Whisper Model..."):
        whisper_model = load_whisper_model()
    st.success("Whisper Model Loaded! Ready to chat.")
except Exception as e:
    st.error(f"Error loading Whisper: {e}")
    st.stop()

# --- Helper Functions ---

def transcribe_audio(audio_bytes):
    """Convert audio bytes to text using Faster Whisper."""
    try:
        # Create a temporary file-like object
        # fast-whisper handles BytesIO but sometimes cleaner to save temp if issues arise.
        # Here we use BytesIO.
        segments, info = whisper_model.transcribe(io.BytesIO(audio_bytes), beam_size=5)
        text = " ".join([segment.text for segment in segments])
        return text
    except Exception as e:
        return f"Error transcribing: {e}"

def query_ollama(prompt, model="llama3"):
    """Query local Ollama instance."""
    try:
        response = ollama.chat(model=model, messages=[
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content']
    except Exception as e:
        return f"Error connecting to Ollama: {e}. Make sure Ollama is running."

async def edge_tts_generate(text, voice):
    """Generate audio bytes using Edge TTS."""
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

def generate_audio(text, voice):
    """Wrapper to run async TTS generation."""
    try:
        return asyncio.run(edge_tts_generate(text, voice))
    except RuntimeError:
        # Handle cases where event loop is already running
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(edge_tts_generate(text, voice))

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar ---
with st.sidebar:
    st.title("Settings ⚙️")
    
    # LLM Selection
    llm_model = st.selectbox(
        "Select LLM Model", 
        ["llama3", "scb10x/llama3.1-typhoon2-8b-instruct", "mistral"], 
        index=0
    )
    st.info("Ensure the selected model is pulled in Ollama.")
    
    st.divider()
    
    # TTS Selection
    st.subheader("🗣️ Voice Settings (Edge TTS)")
    tts_lang = st.radio("Language Mode", ["Thai 🇹🇭", "English 🇺🇸"])
    
    if tts_lang == "Thai 🇹🇭":
        voice_option = st.selectbox("Select Voice", ["th-TH-PremwadeeNeural (Female)", "th-TH-NiwatNeural (Male)"])
        # Map to ID
        voice_id = "th-TH-PremwadeeNeural" if "Premwadee" in voice_option else "th-TH-NiwatNeural"
    else:
        voice_option = st.selectbox("Select Voice", ["en-US-AriaNeural (Female)", "en-US-GuyNeural (Male)"])
        voice_id = "en-US-AriaNeural" if "Aria" in voice_option else "en-US-GuyNeural"

    st.divider()
    st.markdown("**System Status**")
    st.markdown("✅ Whisper (Small / GPU)" if "cuda" in str(whisper_model.model.device) else "✅ Whisper (Small / CPU)")
    st.markdown(f"✅ Edge TTS ({voice_option})")
    st.markdown(f"✅ Ollama ({llm_model})")

# --- Main Interface ---
st.title("🤖 Local Thai AI Assistant (Edge TTS Edition)")
st.caption("Hybrid Input: Type or Speak | High-Quality Voice Output")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "audio" in message:
            st.audio(message["audio"], format="audio/mp3")

# Data container
user_input_text = None
process_input = False

# --- Input Area ---
tab1, tab2 = st.tabs(["💬 Text Input", "🎤 Voice Input"])

with tab1:
    text_input = st.chat_input("พิมพ์ข้อความที่นี่...")
    if text_input:
        user_input_text = text_input
        process_input = True

with tab2:
    st.write("กดปุ่มเพื่อเริ่มอัดเสียง:")
    audio_data = mic_recorder(
        start_prompt="Start Recording",
        stop_prompt="Stop Recording",
        just_once=True,
        key='recorder'
    )
    
    if audio_data:
        st.audio(audio_data['bytes'])
        with st.spinner("Transcribing..."):
            transcribed_text = transcribe_audio(audio_data['bytes'])
            st.success(f"Transcribed: {transcribed_text}")
            if st.button("Send Transcribed Text"):
                user_input_text = transcribed_text
                process_input = True

# --- Processing Pipeline ---
if process_input and user_input_text:
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": user_input_text})
    with st.chat_message("user"):
        st.markdown(user_input_text)
    
    # 2. AI Response
    full_response = ""
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            full_response = query_ollama(user_input_text, model=llm_model)
            message_placeholder.markdown(full_response)
        
        # 3. TTS Generation (Edge TTS)
        audio_bytes = None
        if full_response and "Error connecting to Ollama" not in full_response:
            with st.spinner(f"Generating Audio ({voice_option})..."):
                try:
                    audio_bytes = generate_audio(full_response, voice_id)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                except Exception as e:
                    st.error(f"TTS Error: {e}")
        elif "Error connecting to Ollama" in full_response:
             st.error("Please ensure Ollama is running (`ollama serve`).")

    # 4. Save to History
    response_message = {"role": "assistant", "content": full_response}
    if audio_bytes:
        response_message["audio"] = audio_bytes # Store MP3 bytes
    st.session_state.messages.append(response_message)
