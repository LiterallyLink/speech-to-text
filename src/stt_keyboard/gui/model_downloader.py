"""Model downloader GUI dialog"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QProgressBar, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
import urllib.request
import zipfile
import tempfile

from ..utils.logger import setup_logger


# Available models - simplified list
MODELS = {
    "English (US) - Small (40MB)": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "name": "vosk-model-small-en-us-0.15",
        "language": "en-US"
    },
    "English (US) - Large (1.8GB)": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
        "name": "vosk-model-en-us-0.22",
        "language": "en-US"
    },
    "Spanish - Small (39MB)": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip",
        "name": "vosk-model-small-es-0.42",
        "language": "es"
    },
    "French - Small (41MB)": {
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip",
        "name": "vosk-model-small-fr-0.22",
        "language": "fr"
    },
}


class DownloadThread(QThread):
    """Thread for downloading and extracting models"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str, str)  # model_path, language
    error = pyqtSignal(str)

    def __init__(self, url, model_name, models_dir, language):
        super().__init__()
        self.url = url
        self.model_name = model_name
        self.models_dir = Path(models_dir)
        self.language = language
        self.logger = setup_logger(__name__)

    def run(self):
        try:
            # Create models directory
            self.models_dir.mkdir(parents=True, exist_ok=True)

            # Download
            self.progress.emit(0, "Downloading model...")
            zip_path = self.models_dir / f"{self.model_name}.zip"

            def report_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                if total_size > 0:
                    percent = min(100, int((downloaded * 100) / total_size))
                    mb_downloaded = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    self.progress.emit(
                        percent,
                        f"Downloading: {mb_downloaded:.1f}/{mb_total:.1f} MB"
                    )

            urllib.request.urlretrieve(self.url, zip_path, reporthook=report_progress)

            # Extract
            self.progress.emit(100, "Extracting model...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.models_dir)

            # Clean up zip
            zip_path.unlink()

            model_path = str(self.models_dir / self.model_name)
            self.progress.emit(100, "Complete!")
            self.finished.emit(model_path, self.language)

        except Exception as e:
            self.logger.error(f"Download error: {e}")
            self.error.emit(str(e))


class ModelDownloaderDialog(QDialog):
    """Dialog for downloading speech recognition models"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(__name__)
        self.downloaded_model_path = None
        self.downloaded_language = None

        self.setWindowTitle("Download Speech Model")
        self.setMinimumWidth(500)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Info label
        info_label = QLabel(
            "No speech recognition model found!\n\n"
            "Please select a model to download. The 'Small' models are recommended "
            "for most users (faster, lower resource usage)."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Select Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(MODELS.keys())
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self._start_download)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.download_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def _start_download(self):
        """Start downloading the selected model"""
        selected = self.model_combo.currentText()
        model_info = MODELS[selected]

        self.download_btn.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)

        # Start download thread
        models_dir = Path("models")
        self.download_thread = DownloadThread(
            model_info["url"],
            model_info["name"],
            models_dir,
            model_info["language"]
        )
        self.download_thread.progress.connect(self._on_progress)
        self.download_thread.finished.connect(self._on_finished)
        self.download_thread.error.connect(self._on_error)
        self.download_thread.start()

    def _on_progress(self, percent, message):
        """Update progress bar"""
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)

    def _on_finished(self, model_path, language):
        """Download completed"""
        self.downloaded_model_path = model_path
        self.downloaded_language = language

        QMessageBox.information(
            self,
            "Download Complete",
            f"Model downloaded successfully!\n\nPath: {model_path}"
        )
        self.accept()

    def _on_error(self, error_msg):
        """Download failed"""
        QMessageBox.critical(
            self,
            "Download Failed",
            f"Failed to download model:\n\n{error_msg}"
        )
        self.download_btn.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)

    def get_model_info(self):
        """Get downloaded model info"""
        return self.downloaded_model_path, self.downloaded_language
