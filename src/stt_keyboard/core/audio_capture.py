"""Audio capture from microphone"""

import queue
import threading
import numpy as np
import sounddevice as sd
from typing import Callable, List, Optional
from dataclasses import dataclass

from ..utils.logger import setup_logger


@dataclass
class AudioDevice:
    """Information about an audio input device"""
    id: int
    name: str
    channels: int
    sample_rate: int


class AudioCaptureManager:
    """Manages audio input capture from microphone"""

    def __init__(self, sample_rate: int = 16000, channels: int = 1,
                 device_id: Optional[int] = None):
        """
        Initialize audio capture manager

        Args:
            sample_rate: Audio sample rate (16000 for Vosk)
            channels: Number of audio channels (1 for mono)
            device_id: Specific device ID or None for default
        """
        self.logger = setup_logger(__name__)
        self.sample_rate = sample_rate
        self.channels = channels
        self.device_id = device_id

        self.stream = None
        self.is_recording = False
        self.callback = None

        # Buffer for audio data
        self.audio_queue = queue.Queue()
        self.processing_thread = None

    def get_available_devices(self) -> List[AudioDevice]:
        """
        Get list of available audio input devices

        Returns:
            List of audio devices
        """
        devices = []
        for idx, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:
                devices.append(AudioDevice(
                    id=idx,
                    name=device['name'],
                    channels=device['max_input_channels'],
                    sample_rate=int(device['default_samplerate'])
                ))
        return devices

    def set_device(self, device_id: int):
        """
        Set the audio input device

        Args:
            device_id: Device ID to use
        """
        self.device_id = device_id
        self.logger.info(f"Audio device set to: {device_id}")

    def start_stream(self, callback: Callable[[bytes], None]):
        """
        Start capturing audio from microphone

        Args:
            callback: Function to call with audio data chunks
        """
        if self.is_recording:
            self.logger.warning("Already recording")
            return

        self.callback = callback
        self.is_recording = True

        # Start processing thread
        self.processing_thread = threading.Thread(
            target=self._process_audio,
            daemon=True
        )
        self.processing_thread.start()

        # Start audio stream
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                device=self.device_id,
                callback=self._audio_callback,
                blocksize=8000,
                dtype=np.int16
            )
            self.stream.start()
            self.logger.info("Audio stream started")

        except Exception as e:
            self.logger.error(f"Failed to start audio stream: {e}")
            self.is_recording = False
            raise

    def stop_stream(self):
        """Stop audio capture"""
        if not self.is_recording:
            return

        self.is_recording = False

        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Wait for processing thread to finish
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=1.0)

        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        self.logger.info("Audio stream stopped")

    def _audio_callback(self, indata, frames, time_info, status):
        """
        Callback from sounddevice for audio data

        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Time information
            status: Status flags
        """
        if status:
            self.logger.warning(f"Audio callback status: {status}")

        if self.is_recording:
            # Convert to bytes and add to queue
            audio_bytes = indata.tobytes()
            self.audio_queue.put(audio_bytes)

    def _process_audio(self):
        """Process audio from queue in separate thread"""
        while self.is_recording:
            try:
                # Get audio data with timeout
                audio_data = self.audio_queue.get(timeout=0.1)

                # Call user callback
                if self.callback:
                    self.callback(audio_data)

            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing audio: {e}")
