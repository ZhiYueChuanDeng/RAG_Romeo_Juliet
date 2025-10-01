#!/usr/bin/env python3
"""
Voice RAG System - Based on Intelligent RAG System
Complete workflow: Voice recording → Whisper ASR → Intelligent RAG → TTS → Audio playback
"""

import sounddevice as sd
from scipy.io.wavfile import write
import threading
import numpy as np
import whisper
import os
import sys
from gtts import gTTS
import pygame
import time
import logging
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.intelligent_rag_system import IntelligentRAGSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VoiceRAGSystem:
    """Voice RAG System"""

    def __init__(self,
                 use_llm: bool = False,
                 sample_rate: int = 16000,
                 channels: int = 1):
        """
        Initialize voice RAG system

        Args:
            use_llm: Whether to use LLM (for Inferred and Out-of-KB)
            sample_rate: Recording sample rate
            channels: Number of audio channels
        """
        logger.info("=" * 60)
        logger.info("Initializing Voice RAG System")
        logger.info("=" * 60)

        self.sample_rate = sample_rate
        self.channels = channels

        # Recording state
        self.is_recording = False
        self.audio_data = []

        # Initialize intelligent RAG system
        logger.info("Loading intelligent RAG system...")
        self.rag_system = IntelligentRAGSystem(use_llm=use_llm)

        # Initialize Whisper ASR
        logger.info("Loading Whisper ASR model...")
        self.whisper_model = whisper.load_model("base")
        logger.info("✓ Whisper model loaded")

        # Initialize pygame for audio playback
        pygame.mixer.init()

        logger.info("✓ Voice RAG system initialization complete")
        logger.info("=" * 60)

    def start_recording(self):
        """Start recording"""
        self.is_recording = True
        self.audio_data = []

        def callback(indata, frames, time_info, status):
            if self.is_recording:
                self.audio_data.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=callback
        )
        self.stream.start()
        logger.info("🎤 Recording started...")

    def stop_recording(self) -> str:
        """Stop recording and save"""
        self.is_recording = False
        self.stream.stop()
        self.stream.close()

        if not self.audio_data:
            logger.warning("No audio data recorded")
            return None

        # Concatenate audio data
        audio_array = np.concatenate(self.audio_data, axis=0)

        # Save as temporary file
        temp_file = "temp_recording.wav"
        write(temp_file, self.sample_rate, audio_array)

        logger.info("✓ Recording complete")
        return temp_file

    def transcribe_audio(self, audio_file: str) -> str:
        """
        Transcribe audio using Whisper

        Args:
            audio_file: Audio file path

        Returns:
            Transcribed text
        """
        logger.info("Transcribing audio...")
        result = self.whisper_model.transcribe(audio_file)
        text = result["text"].strip()

        logger.info(f"✓ Transcription complete: {text}")
        return text

    def generate_answer(self, question: str, debug: bool = True) -> tuple:
        """
        Generate answer using intelligent RAG

        Args:
            question: User question
            debug: Whether to output debug information

        Returns:
            (answer, question_type, source_passages)
        """
        logger.info(f"Question: {question}")

        # Call intelligent RAG system
        answer, question_type, passages = self.rag_system.answer_question(
            question, debug=debug
        )

        logger.info(f"Question type: {question_type}")
        logger.info(f"Answer: {answer[:100]}...")

        return answer, question_type, passages

    def text_to_speech(self, text: str, lang: str = 'en') -> str:
        """
        Convert text to speech

        Args:
            text: Text to convert
            lang: Language code

        Returns:
            Audio file path
        """
        logger.info("Generating speech...")

        # Generate speech
        tts = gTTS(text=text, lang=lang, slow=False)

        # Save as temporary file
        output_file = "temp_response.mp3"
        tts.save(output_file)

        logger.info("✓ Speech generation complete")
        return output_file

    def play_audio(self, audio_file: str):
        """Play audio"""
        logger.info("🔊 Playing audio...")

        try:
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()

            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            logger.info("✓ Playback complete")

        except Exception as e:
            logger.error(f"Playback failed: {e}")

    def process_voice_query(self, recording_duration: int = 5, debug: bool = True):
        """
        Process complete voice query workflow

        Args:
            recording_duration: Recording duration (seconds)
            debug: Whether to output debug information
        """
        logger.info("\n" + "=" * 60)
        logger.info("Starting voice query workflow")
        logger.info("=" * 60)

        try:
            # Step 1: Record
            self.start_recording()
            logger.info(f"Please speak (will record for {recording_duration} seconds)...")
            time.sleep(recording_duration)
            audio_file = self.stop_recording()

            if not audio_file:
                logger.error("Recording failed")
                return

            # Step 2: Speech to text (ASR)
            question = self.transcribe_audio(audio_file)

            # Step 3: RAG generates answer
            answer, question_type, passages = self.generate_answer(question, debug=debug)

            # Step 4: Text to speech (TTS)
            response_audio = self.text_to_speech(answer)

            # Step 5: Play answer
            self.play_audio(response_audio)

            # Clean up temporary files
            if os.path.exists(audio_file):
                os.remove(audio_file)
            if os.path.exists(response_audio):
                os.remove(response_audio)

            logger.info("=" * 60)
            logger.info("Query workflow complete")
            logger.info("=" * 60)

            return {
                "question": question,
                "answer": answer,
                "question_type": question_type,
                "passages": passages
            }

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            import traceback
            traceback.print_exc()

    def interactive_mode(self):
        """Interactive mode"""
        logger.info("\n" + "=" * 60)
        logger.info("Voice RAG Interactive Mode")
        logger.info("=" * 60)
        logger.info("Enter 'q' to quit")
        logger.info("Enter 'v' for voice query")
        logger.info("Enter text directly for text query")
        logger.info("=" * 60)

        while True:
            try:
                user_input = input("\nEnter command: ").strip()

                if user_input.lower() == 'q':
                    logger.info("Exiting system")
                    break

                elif user_input.lower() == 'v':
                    # Voice query
                    self.process_voice_query(recording_duration=5, debug=True)

                elif user_input:
                    # Text query
                    logger.info(f"\nQuestion: {user_input}")

                    # Generate answer
                    answer, question_type, passages = self.generate_answer(
                        user_input, debug=True
                    )

                    # Play voice answer
                    response_audio = self.text_to_speech(answer)
                    self.play_audio(response_audio)

                    # Clean up
                    if os.path.exists(response_audio):
                        os.remove(response_audio)

            except KeyboardInterrupt:
                logger.info("\nUser interrupted")
                break
            except Exception as e:
                logger.error(f"Error: {e}")


def main():
    """Main function"""
    # Initialize voice RAG system
    voice_rag = VoiceRAGSystem(use_llm=False)

    # Test text queries
    logger.info("\nTesting text queries:")
    test_questions = [
        "What metaphor does Romeo use to describe Juliet?",
        "How does Tybalt's attitude toward Romeo change?",
        "What would happen if Romeo had a smartphone?"
    ]

    for question in test_questions:
        logger.info(f"\n{'='*60}")
        answer, qtype, passages = voice_rag.generate_answer(question, debug=True)
        logger.info(f"Answer type: {qtype}")
        logger.info(f"Answer: {answer[:100]}...")

    # Start interactive mode
    # voice_rag.interactive_mode()


if __name__ == "__main__":
    # Check if running in correct directory
    if not os.path.exists("data/topics.csv"):
        print("❌ Please run this script in the quantitative_eval directory")
        exit(1)

    main()
