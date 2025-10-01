# Romeo & Juliet Web Application Guide

## 🌐 Features

This is a Flask-based intelligent Q&A web application that supports two interaction modes:

### 1️⃣ Text Q&A Mode 💬
- Enter your question in the input box
- Click the "Ask" button or press Enter
- System returns an answer and displays the question type (Known/Inferred/Out-of-KB)
- Click the 🔊 icon to play the audio answer

### 2️⃣ Voice Q&A Mode 🎤
- Click the microphone button to start recording
- Speak your question (in English)
- Click again to stop recording
- System automatically transcribes the question, generates an answer, and plays the audio answer

---

## 🚀 Launch Steps

### 1. Install Dependencies

Make sure Flask and related libraries are installed:

```bash
pip install flask
pip install openai-whisper
pip install gtts
pip install sounddevice
pip install scipy
```

### 2. Start Web Server

Run in the `quantitative_eval` directory:

```bash
python app.py
```

You will see output similar to:

```
============================================================
🚀 Romeo & Juliet Intelligent Q&A System
============================================================
Access URL: http://localhost:5000
Press Ctrl+C to stop service
============================================================

Initializing Intelligent RAG System...
Loading Whisper ASR model...
✓ System initialization complete
 * Running on http://0.0.0.0:5000
```

### 3. Access the Web Page

Open in your browser:

```
http://localhost:5000
```

---

## 📱 Interface Description

### Page Layout

```
┌─────────────────────────────────────┐
│  🎭 Romeo & Juliet                  │
│  Intelligent Q&A System - Groundtruth-based Retrieval    │
├─────────────────────────────────────┤
│  [💬 Text Q&A]  [🎤 Voice Q&A]      │
├─────────────────────────────────────┤
│                                     │
│  [Input box] Enter questions about  │
│              Romeo & Juliet... [Ask]│
│                                     │
│  ┌─────────────────────────────────┐│
│  │ Question: What metaphor does...?││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │ Answer: [Known] 🔊              ││
│  │ Romeo employs the sun as a...   ││
│  │ [Audio Player]                  ││
│  └─────────────────────────────────┘│
│                                     │
└─────────────────────────────────────┘
```

### Question Type Indicators

- **Known** - Green label: Answer directly from knowledge base
- **Inferred** - Yellow label: Answer synthesized from multiple passages
- **Out-of-KB** - Red label: Beyond knowledge base scope

---

## 🎯 Example Questions

### Known Type Questions
```
What metaphor does Romeo use to describe Juliet?
Why does Friar Laurence agree to help Romeo and Juliet?
What curse does Mercutio utter before dying?
```

### Inferred Type Questions
```
How does Tybalt's attitude toward Romeo change?
What role does Friar Laurence play in Romeo and Juliet's relationship?
How does the Prince's response to the conflict evolve?
```

### Out-of-KB Type Questions
```
What would happen if Romeo had a smartphone?
How does the feud compare to modern family conflicts?
What advice would Friar Laurence give about social media?
```

---

## 🔧 API Interface Description

### 1. Text Q&A API

**Endpoint:** `POST /api/ask`

**Request Format:**
```json
{
    "question": "What metaphor does Romeo use to describe Juliet?"
}
```

**Response Format:**
```json
{
    "success": true,
    "question": "What metaphor does Romeo use to describe Juliet?",
    "answer": "Romeo employs the sun as a metaphor...",
    "question_type": "Known",
    "passages": ["passage1", "passage2"]
}
```

### 2. Voice Q&A API

**Endpoint:** `POST /api/ask-voice`

**Request:** Upload audio file (multipart/form-data)

**Response Format:**
```json
{
    "success": true,
    "question": "Transcribed question text",
    "answer": "Answer",
    "question_type": "Known",
    "audio_id": "1234567890"
}
```

### 3. Get Audio File

**Endpoint:** `GET /api/audio/<audio_id>`

**Response:** MP3 audio file

### 4. Text-to-Speech API

**Endpoint:** `POST /api/tts`

**Request Format:**
```json
{
    "text": "Text to convert"
}
```

**Response Format:**
```json
{
    "success": true,
    "audio_id": "1234567890"
}
```

---

## ⚙️ Configuration Options

### Change Port

Modify the last line in `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change to another port
```

### Enable/Disable LLM

Modify the initialization code in `app.py`:

```python
rag_system = IntelligentRAGSystem(use_llm=False)  # True to enable LLM
```

### Change Maximum Upload Size

Modify in `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

---

## 🐛 Common Issues

### 1. Microphone Permission Issue

**Problem:** Browser prompts "Cannot access microphone"

**Solution:**
- Make sure browser has microphone permission
- If it's an HTTPS website, you need an SSL certificate
- Try allowing microphone access in Chrome/Firefox

### 2. Audio Cannot Play

**Problem:** Generated audio file cannot play

**Solution:**
- Check if gTTS is installed correctly
- Make sure network connection is normal (gTTS requires internet)
- Check browser console for error messages

### 3. Speech Transcription Inaccurate

**Problem:** Whisper transcription text is incorrect

**Solution:**
- Speak clearly and at moderate speed during recording
- Ensure quiet environment, reduce background noise
- Try upgrading Whisper model (base → small → medium)

### 4. System Startup Slow

**Problem:** First startup takes a long time

**Solution:**
- This is normal, system needs to load:
  - Intelligent RAG system
  - Whisper model
  - SentenceTransformer model
- Subsequent startups will be faster

---

## 📊 Performance Notes

### Response Time

- **Text Q&A:** 0.5-2 seconds (depends on question complexity)
- **Voice Q&A:** 3-10 seconds
  - ASR transcription: 1-3 seconds
  - RAG generation: 0.5-2 seconds
  - TTS synthesis: 1-3 seconds
  - Audio transmission: 0.5-2 seconds

### Concurrent Support

- Development mode: Single-threaded, recommended for 1-5 users
- Production mode: Need to use WSGI server (like Gunicorn)

```bash
# Production deployment
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 🎨 Interface Features

- **Gradient Background** - Purple gradient, modern feel
- **Card Design** - Rounded corners with shadows, clear hierarchy
- **Animation Effects** - Button hover, recording pulse animation
- **Responsive Layout** - Adapts to different screen sizes
- **Type Indicators** - Colored labels distinguish question types
- **Audio Integration** - Built-in HTML5 audio player

---

## 🔒 Security Notes

### Development Environment
Current configuration is suitable for development and testing, **not recommended to expose directly to the public internet**.

### Production Environment Recommendations

1. **Disable Debug Mode**
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

2. **Add Authentication**
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@app.route('/api/ask')
@auth.login_required
def ask_text():
    # ...
```

3. **Enable HTTPS**
- Use SSL certificate
- Configure reverse proxy (Nginx/Apache)

4. **Limit Request Rate**
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/ask')
@limiter.limit("10 per minute")
def ask_text():
    # ...
```

---

## 📝 Technology Stack

- **Backend:** Flask
- **Frontend:** HTML5 + CSS3 + JavaScript
- **Speech Recognition:** OpenAI Whisper
- **Speech Synthesis:** gTTS
- **RAG System:** Intelligent RAG + Groundtruth Retrieval
- **Audio Recording:** MediaRecorder API

---

## 🎓 Extension Suggestions

1. **Add History** - Save user's Q&A history
2. **Multi-language Support** - Support Chinese Q&A
3. **Answer Rating** - Let users provide feedback on answers
4. **Export Function** - Export Q&A records as PDF/Word
5. **Mobile Optimization** - Create PWA application

---

Generated on: 2025-10-01
