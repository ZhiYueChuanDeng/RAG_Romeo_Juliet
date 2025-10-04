#!/usr/bin/env python3
"""
Flask Web Application - Romeo & Juliet Intelligent Q&A System
Supports both text and voice interaction modes
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import tempfile
import logging
from werkzeug.utils import secure_filename

sys.path.append(os.path.dirname(__file__))

from core.intelligent_rag_system import IntelligentRAGSystem
import whisper
from gtts import gTTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Maximum 16MB
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Initialize RAG system and Whisper model
logger.info("Initializing intelligent RAG system...")
rag_system = IntelligentRAGSystem(use_llm=True, llm_model="llama3.2")

logger.info("Loading Whisper ASR model...")
whisper_model = whisper.load_model("base")

logger.info("✓ System initialization complete")


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/ask', methods=['POST'])
def ask_text():
    """
    Text-based Q&A API

    Request format:
    {
        "question": "user question"
    }

    Response format:
    {
        "success": true,
        "question": "user question",
        "answer": "answer",
        "question_type": "Known/Inferred/Out-of-KB",
        "passages": ["passage1", "passage2", ...]
    }
    """
    try:
        data = request.get_json()
        question = data.get('question', '').strip()

        if not question:
            return jsonify({
                'success': False,
                'error': 'Question cannot be empty'
            }), 400

        logger.info(f"Text question: {question}")

        # Use RAG system to generate answer
        answer, question_type, passages = rag_system.answer_question(
            question, debug=False
        )

        logger.info(f"Question type: {question_type}")
        logger.info(f"Answer: {answer[:100]}...")

        return jsonify({
            'success': True,
            'question': question,
            'answer': answer,
            'question_type': question_type,
            'passages': passages[:2]  # Return only first 2 passages
        })

    except Exception as e:
        logger.error(f"Text Q&A error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/ask-voice', methods=['POST'])
def ask_voice():
    """
    Voice-based Q&A API

    Request: Upload audio file

    Response format:
    {
        "success": true,
        "question": "transcribed question",
        "answer": "answer",
        "question_type": "Known/Inferred/Out-of-KB",
        "audio_url": "/api/audio/response_audio_ID"
    }
    """
    try:
        # Check if file is uploaded
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file uploaded'
            }), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename'
            }), 400

        # Save uploaded audio file
        filename = secure_filename(audio_file.filename)
        temp_input = os.path.join(app.config['UPLOAD_FOLDER'], f"input_{filename}")
        audio_file.save(temp_input)

        logger.info(f"Received audio file: {filename}")

        # Step 1: Speech to text (ASR)
        logger.info("Transcribing audio...")
        result = whisper_model.transcribe(temp_input)
        question = result["text"].strip()

        logger.info(f"Transcription complete: {question}")

        # Step 2: Generate answer
        answer, question_type, passages = rag_system.answer_question(
            question, debug=False
        )

        logger.info(f"Question type: {question_type}")

        # Step 3: Text to speech (TTS)
        logger.info("Generating speech...")
        tts = gTTS(text=answer, lang='en', slow=False)

        # Generate unique output filename
        import time
        audio_id = f"{int(time.time())}"
        temp_output = os.path.join(app.config['UPLOAD_FOLDER'], f"output_{audio_id}.mp3")
        tts.save(temp_output)

        logger.info("Speech generation complete")

        # Clean up input file
        if os.path.exists(temp_input):
            os.remove(temp_input)

        return jsonify({
            'success': True,
            'question': question,
            'answer': answer,
            'question_type': question_type,
            'audio_id': audio_id
        })

    except Exception as e:
        logger.error(f"Voice Q&A error: {e}")
        import traceback
        traceback.print_exc()

        # Clean up temporary files
        if 'temp_input' in locals() and os.path.exists(temp_input):
            os.remove(temp_input)

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/audio/<audio_id>')
def get_audio(audio_id):
    """Get generated audio file"""
    try:
        # Security check
        audio_id = secure_filename(audio_id)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], f"output_{audio_id}.mp3")

        if not os.path.exists(audio_path):
            return jsonify({
                'success': False,
                'error': 'Audio file not found'
            }), 404

        return send_file(audio_path, mimetype='audio/mpeg')

    except Exception as e:
        logger.error(f"Get audio error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    """
    Text-to-speech API (provides audio playback for text mode)

    Request format:
    {
        "text": "text to convert"
    }

    Returns: Audio file ID
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({
                'success': False,
                'error': 'Text cannot be empty'
            }), 400

        logger.info("Generating TTS audio...")

        # Text to speech
        tts = gTTS(text=text, lang='en', slow=False)

        # Generate unique ID
        import time
        audio_id = f"{int(time.time())}"
        temp_output = os.path.join(app.config['UPLOAD_FOLDER'], f"output_{audio_id}.mp3")
        tts.save(temp_output)

        return jsonify({
            'success': True,
            'audio_id': audio_id
        })

    except Exception as e:
        logger.error(f"TTS error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Check if running in correct directory
    if not os.path.exists("data/topics.csv"):
        print("❌ Please run this script in the quantitative_eval directory")
        exit(1)

    print("\n" + "=" * 60)
    print("🚀 Romeo & Juliet Intelligent Q&A System")
    print("=" * 60)
    print("Access URL: http://localhost:5000")
    print("Press Ctrl+C to stop service")
    print("=" * 60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
