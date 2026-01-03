"""Speech recognition engine using Vosk"""

import json
import queue
import threading
from pathlib import Path
from typing import Callable, Optional
from dataclasses import dataclass

from vosk import Model, KaldiRecognizer

from ..utils.logger import setup_logger


@dataclass
class TranscriptionResult:
    """Result from speech recognition"""
    text: str
    confidence: float
    is_final: bool


class SpeechEngine:
    """Offline speech recognition using Vosk"""

    def __init__(self, model_path: str, language: str):
        """
        Initialize speech engine

        Args:
            model_path: Path to Vosk model directory
            language: Language code
        """
        self.logger = setup_logger(__name__)
        self.model_path = Path(model_path)
        self.language = language

        # Callbacks
        self.on_partial_result: Optional[Callable] = None
        self.on_final_result: Optional[Callable] = None

        # Vosk components
        self.model = None
        self.recognizer = None

        # Processing
        self.audio_queue = queue.Queue()
        self.processing_thread = None
        self.is_processing = False

        self._load_model()
        self._start_processing_thread()

    def _load_model(self):
        """Load Vosk model from disk"""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                "Please download a model first using: python scripts/download_model.py"
            )

        self.logger.info(f"Loading model from {self.model_path}")
        self.model = Model(str(self.model_path))
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.recognizer.SetWords(True)
        self.logger.info("Model loaded successfully")

    def _start_processing_thread(self):
        """Start background thread for audio processing"""
        self.is_processing = True
        self.processing_thread = threading.Thread(
            target=self._process_loop,
            daemon=True
        )
        self.processing_thread.start()

    def process_audio(self, audio_data: bytes):
        """
        Add audio data to processing queue

        Args:
            audio_data: Raw audio bytes (16-bit PCM)
        """
        self.audio_queue.put(audio_data)

    def _process_loop(self):
        """Background processing loop"""
        while self.is_processing:
            try:
                audio_data = self.audio_queue.get(timeout=0.1)
                self._process_chunk(audio_data)
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")

    def _process_chunk(self, audio_data: bytes):
        """
        Process a chunk of audio data

        Args:
            audio_data: Audio bytes to process
        """
        if self.recognizer.AcceptWaveform(audio_data):
            # Final result
            result = json.loads(self.recognizer.Result())
            text = result.get('text', '')

            if text and self.on_final_result:
                self.on_final_result(text)
        else:
            # Partial result
            partial = json.loads(self.recognizer.PartialResult())
            text = partial.get('partial', '')

            if text and self.on_partial_result:
                self.on_partial_result(text)

    def get_final_result(self) -> str:
        """
        Get final result and reset recognizer

        Returns:
            Final transcribed text
        """
        result = json.loads(self.recognizer.FinalResult())
        text = result.get('text', '')
        return text

    def reset(self):
        """Reset recognizer state"""
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.recognizer.SetWords(True)

        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    def set_model(self, model_path: str):
        """
        Switch to a different model

        Args:
            model_path: Path to new model
        """
        self.model_path = Path(model_path)
        self._load_model()

    def shutdown(self):
        """Shutdown the speech engine"""
        self.is_processing = False
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
