"""PySide6 desktop application for personality analysis and imitation chat.

Workflow:
1. Select API provider (DeepSeek / Kimi).
2. Enter and validate the API key.
3. Choose between Personality Analysis or Imitation Chat.
4. Run the selected workflow.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from PySide6.QtCore import QSize, Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from api_client import ApiClient, ApiError, format_key_error
from session import Session
from skills import generate_imitation_skill, load_imitation_skill, run_personality_analysis


APP_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
THEME = {
    "bg": "#0b1120",
    "card": "#f8fafc",
    "text": "#0f172a",
    "muted": "#475569",
    "accent": "#005fcc",
    "accent_hover": "#004da3",
    "danger": "#dc2626",
    "success": "#15803d",
    "input_border": "#005fcc",
    "radio_select": "#005fcc",
}


def apply_styles(app: QApplication) -> None:
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(THEME["bg"]))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Base, QColor(THEME["card"]))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#e2e8f0"))
    palette.setColor(QPalette.ColorRole.Text, QColor(THEME["text"]))
    palette.setColor(QPalette.ColorRole.Button, QColor(THEME["accent"]))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
    app.setPalette(palette)

    app.setStyleSheet(
        f"""
        QMainWindow, QWidget {{
            background-color: {THEME["bg"]};
            color: #ffffff;
        }}
        QFrame#card {{
            background-color: {THEME["card"]};
            border-radius: 16px;
        }}
        QLabel {{
            color: #ffffff;
        }}
        QLabel#title {{
            font-size: 26px;
            font-weight: bold;
            color: #ffffff;
        }}
        QLabel#subtitle {{
            font-size: 14px;
            color: #cbd5e1;
        }}
        QLabel#cardTitle {{
            font-size: 20px;
            font-weight: bold;
            color: {THEME["text"]};
        }}
        QLabel#cardSubtitle {{
            font-size: 13px;
            color: {THEME["muted"]};
        }}
        QLabel#optionTitle {{
            font-size: 15px;
            font-weight: bold;
            color: {THEME["text"]};
        }}
        QLabel#optionDesc {{
            font-size: 12px;
            color: {THEME["muted"]};
        }}
        QLabel#error {{
            color: {THEME["danger"]};
            font-size: 13px;
        }}
        QPushButton#primary {{
            background-color: {THEME["accent"]};
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: bold;
            font-size: 13px;
        }}
        QPushButton#primary:hover {{
            background-color: {THEME["accent_hover"]};
        }}
        QPushButton#primary:disabled {{
            background-color: #94a3b8;
        }}
        QPushButton#secondary {{
            background-color: #e2e8f0;
            color: {THEME["text"]};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 13px;
        }}
        QPushButton#secondary:hover {{
            background-color: #cbd5e1;
        }}
        QPushButton#optionCard {{
            background-color: #ffffff;
            color: {THEME["text"]};
            border: 2px solid #cbd5e1;
            border-radius: 12px;
            padding: 20px;
            text-align: left;
        }}
        QPushButton#optionCard:hover {{
            border-color: {THEME["accent"]};
            background-color: #f1f5f9;
        }}
        QLineEdit {{
            background-color: #ffffff;
            color: {THEME["text"]};
            border: 2px solid #cbd5e1;
            border-radius: 8px;
            padding: 10px;
            font-size: 13px;
        }}
        QLineEdit:focus {{
            border-color: {THEME["input_border"]};
        }}
        QTextEdit {{
            background-color: #ffffff;
            color: {THEME["text"]};
            border: 2px solid #cbd5e1;
            border-radius: 8px;
            padding: 8px;
            font-size: 13px;
        }}
        QProgressBar {{
            border: none;
            border-radius: 6px;
            background-color: #334155;
            text-align: center;
            color: #ffffff;
        }}
        QProgressBar::chunk {{
            background-color: {THEME["accent"]};
            border-radius: 6px;
        }}
        QScrollArea {{
            border: none;
        }}
    """
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def show_error(parent: QWidget, message: str) -> None:
    QMessageBox.critical(parent, "Error", message)


def show_info(parent: QWidget, message: str) -> None:
    QMessageBox.information(parent, "Success", message)


def confirm(parent: QWidget, message: str) -> bool:
    reply = QMessageBox.question(parent, "Confirm", message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    return reply == QMessageBox.StandardButton.Yes


# ---------------------------------------------------------------------------
# Worker threads
# ---------------------------------------------------------------------------
class AnalysisWorker(QThread):
    finished = Signal(object)  # Path or ApiError
    progress = Signal(str)

    def __init__(self, client: ApiClient, zip_path: Path) -> None:
        super().__init__()
        self.client = client
        self.zip_path = zip_path

    def run(self) -> None:
        try:
            out_path = run_personality_analysis(self.client, self.zip_path, self.progress.emit)
            self.finished.emit(out_path)
        except Exception as exc:
            self.finished.emit(ApiError(str(exc)))


class ImitationWorker(QThread):
    finished = Signal(object)  # Path or ApiError
    progress = Signal(str)

    def __init__(self, client: ApiClient, profile_path: Path) -> None:
        super().__init__()
        self.client = client
        self.profile_path = profile_path

    def run(self) -> None:
        try:
            skill_dir = generate_imitation_skill(self.client, self.profile_path, self.progress.emit)
            self.finished.emit(skill_dir)
        except Exception as exc:
            self.finished.emit(ApiError(str(exc)))


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------
class ProviderScreen(QWidget):
    selected = Signal()

    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session
        self.selected_provider = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(16)

        title = QLabel("AI API Setup")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Select the provider you want to connect to.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)
        layout.addSpacing(24)

        card = self._build_card()
        layout.addWidget(card, stretch=1)

        self.error_label = QLabel("")
        self.error_label.setObjectName("error")
        layout.addWidget(self.error_label)

        next_btn = QPushButton("Next")
        next_btn.setObjectName("primary")
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_btn.clicked.connect(self._on_next)
        layout.addWidget(next_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def _build_card(self) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(32, 28, 32, 28)
        vbox.setSpacing(12)

        card_title = QLabel("Provider")
        card_title.setObjectName("cardTitle")
        vbox.addWidget(card_title)

        card_sub = QLabel("Choose your API source")
        card_sub.setObjectName("cardSubtitle")
        vbox.addWidget(card_sub)
        vbox.addSpacing(12)

        for value, label, desc in [
            ("deepseek", "DeepSeek", "General-purpose large language model"),
            ("kimi", "Kimi", "Moonshot AI assistant"),
        ]:
            btn = QPushButton(f"<b>{label}</b><br/><span style='color:{THEME['muted']}; font-size:12px;'>{desc}</span>")
            btn.setObjectName("optionCard")
            btn.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.clicked.connect(lambda checked, v=value, b=btn: self._select(v, b))
            vbox.addWidget(btn)

        return card

    def _select(self, provider: str, btn: QPushButton) -> None:
        self.selected_provider = provider
        btn.setChecked(True)
        self.error_label.setText("")

    def _on_next(self) -> None:
        if not self.selected_provider:
            self.error_label.setText("Please select a provider before continuing.")
            return
        self.session.provider = self.selected_provider
        self.selected.emit()


class ApiKeyScreen(QWidget):
    submitted = Signal()
    back = Signal()

    _INSTRUCTIONS = {
        "deepseek": (
            "<ol>"
            "<li>Go to <a href='https://platform.deepseek.com/api_keys'>DeepSeek API Keys</a>.</li>"
            "<li>Sign in and create a new API key.</li>"
            "<li>Copy the key and paste it below.</li>"
            "</ol>"
        ),
        "kimi": (
            "<ol>"
            "<li>Go to <a href='https://platform.moonshot.cn/console/api-keys'>Kimi API Keys</a>.</li>"
            "<li>Sign in and create a new API key.</li>"
            "<li>Copy the key and paste it below.</li>"
            "</ol>"
        ),
    }

    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(16)

        title = QLabel("AI API Setup")
        title.setObjectName("title")
        layout.addWidget(title)

        self.subtitle = QLabel("")
        self.subtitle.setObjectName("subtitle")
        layout.addWidget(self.subtitle)
        layout.addSpacing(24)

        card = self._build_card()
        layout.addWidget(card, stretch=1)

        self.error_label = QLabel("")
        self.error_label.setObjectName("error")
        layout.addWidget(self.error_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        back_btn = QPushButton("Back")
        back_btn.setObjectName("secondary")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.back.emit)
        btn_layout.addWidget(back_btn)

        submit_btn = QPushButton("Save and Continue")
        submit_btn.setObjectName("primary")
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        submit_btn.clicked.connect(self._on_submit)
        btn_layout.addWidget(submit_btn)

        layout.addLayout(btn_layout)

    def _build_card(self) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(32, 28, 32, 28)
        vbox.setSpacing(12)

        self.card_title = QLabel("")
        self.card_title.setObjectName("cardTitle")
        vbox.addWidget(self.card_title)

        self.instructions = QLabel("")
        self.instructions.setObjectName("cardSubtitle")
        self.instructions.setOpenExternalLinks(True)
        self.instructions.setTextFormat(Qt.TextFormat.RichText)
        vbox.addWidget(self.instructions)
        vbox.addSpacing(8)

        key_label = QLabel("API Key")
        key_label.setObjectName("cardSubtitle")
        vbox.addWidget(key_label)

        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("sk-...")
        vbox.addWidget(self.key_input)

        self.toggle_btn = QPushButton("Show")
        self.toggle_btn.setObjectName("secondary")
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.clicked.connect(self._toggle_visibility)
        vbox.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        return card

    def refresh(self) -> None:
        provider = self.session.provider
        self.card_title.setText(f"{provider.capitalize()} API Key")
        self.subtitle.setText(f"Enter your {provider.capitalize()} API key to continue.")
        self.instructions.setText(self._INSTRUCTIONS.get(provider, ""))
        self.key_input.setText(self.session.api_key)
        self.error_label.setText("")

    def _toggle_visibility(self) -> None:
        if self.toggle_btn.isChecked():
            self.key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_btn.setText("Hide")
        else:
            self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_btn.setText("Show")

    def _on_submit(self) -> None:
        key = self.key_input.text().strip()
        if not key:
            self.error_label.setText("Please enter an API key.")
            return

        if len(key) < 8:
            self.error_label.setText("The API key format looks invalid (too short).")
            return

        self.error_label.setText("Validating key...")
        QApplication.processEvents()

        try:
            client = ApiClient(self.session.provider, key)
            client.validate_key()
        except ApiError as exc:
            self.error_label.setText(format_key_error(self.session.provider, exc))
            return

        self.session.api_key = key
        self.session.api_key_hint = self.session.mask_key()
        self.session.save()
        self.submitted.emit()


class MainMenuScreen(QWidget):
    personality = Signal()
    imitation = Signal()
    reset = Signal()

    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(16)

        title = QLabel("What would you like to do?")
        title.setObjectName("title")
        layout.addWidget(title)

        hint = QLabel(f"Connected to {session.provider.capitalize()}  •  Key: {session.api_key_hint}")
        hint.setObjectName("subtitle")
        layout.addWidget(hint)
        layout.addSpacing(24)

        card = QWidget()
        card.setObjectName("card")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(32, 28, 32, 28)
        vbox.setSpacing(16)

        for label, desc, signal in [
            ("Personality Analysis", "Upload a .zip of evidence files to generate a personality profile.", self.personality),
            ("Imitation Chat", "Upload an existing .md profile to create a chat companion.", self.imitation),
        ]:
            btn = QPushButton(f"<b>{label}</b><br/><span style='color:{THEME['muted']}; font-size:12px;'>{desc}</span>")
            btn.setObjectName("optionCard")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(signal.emit)
            vbox.addWidget(btn)

        layout.addWidget(card, stretch=1)

        reset_btn = QPushButton("Reset API Settings")
        reset_btn.setObjectName("secondary")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self.reset.emit)
        layout.addWidget(reset_btn, alignment=Qt.AlignmentFlag.AlignLeft)


class PersonalityAnalysisScreen(QWidget):
    done = Signal()

    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session
        self.worker: AnalysisWorker | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(16)

        title = QLabel("Personality Analysis")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Upload a .zip archive containing chat logs, documents, and images.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)
        layout.addSpacing(24)

        card = self._build_card()
        layout.addWidget(card, stretch=1)

        self.error_label = QLabel("")
        self.error_label.setObjectName("error")
        layout.addWidget(self.error_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.hide()
        layout.addWidget(self.progress)

        self.status_label = QLabel("")
        self.status_label.setObjectName("subtitle")
        layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        back_btn = QPushButton("Back")
        back_btn.setObjectName("secondary")
        back_btn.clicked.connect(self.done.emit)
        btn_layout.addWidget(back_btn)

        self.run_btn = QPushButton("Select .zip and Analyze")
        self.run_btn.setObjectName("primary")
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_btn.clicked.connect(self._select_file)
        btn_layout.addWidget(self.run_btn)

        layout.addLayout(btn_layout)

    def _build_card(self) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(32, 28, 32, 28)
        vbox.setSpacing(12)

        card_title = QLabel("Upload Evidence")
        card_title.setObjectName("cardTitle")
        vbox.addWidget(card_title)

        info = QLabel(
            "Accepted contents: .txt, .md, .log, .json, .csv, images (.jpg/.png/.webp/.heic), "
            "and raw chat exports. Place all files in the root of the zip archive."
        )
        info.setObjectName("cardSubtitle")
        info.setWordWrap(True)
        vbox.addWidget(info)

        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("cardSubtitle")
        vbox.addWidget(self.file_label)

        return card

    def _select_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Evidence Archive", "", "Zip files (*.zip)")
        if not path:
            return
        self.file_label.setText(f"Selected: {Path(path).name}")
        self._run(Path(path))

    def _run(self, zip_path: Path) -> None:
        self.error_label.setText("")
        self.run_btn.setEnabled(False)
        self.progress.show()

        client = ApiClient(self.session.provider, self.session.api_key)
        self.worker = AnalysisWorker(client, zip_path)
        self.worker.progress.connect(self.status_label.setText)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, result: object) -> None:
        self.run_btn.setEnabled(True)
        self.progress.hide()
        self.status_label.setText("")

        if isinstance(result, ApiError):
            self.error_label.setText(str(result))
            return

        out_path = Path(str(result))
        show_info(self, f"Analysis complete. Profile saved to:\n{out_path.name}")
        self._prompt_download(out_path)

    def _prompt_download(self, out_path: Path) -> None:
        target, _ = QFileDialog.getSaveFileName(
            self,
            "Save Personality Profile",
            str(out_path.name),
            "Markdown files (*.md)",
        )
        if target:
            shutil.copy2(out_path, target)
            show_info(self, f"Downloaded to {target}")
        self.done.emit()


class ImitationScreen(QWidget):
    chat_ready = Signal(str)  # skill_dir path
    done = Signal()

    def __init__(self, session: Session) -> None:
        super().__init__()
        self.session = session
        self.worker: ImitationWorker | None = None
        self.generated_skill_dir: Path | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(16)

        title = QLabel("Imitation Chat")
        title.setObjectName("title")
        layout.addWidget(title)

        subtitle = QLabel("Upload a .md personality profile to build a chat companion.")
        subtitle.setObjectName("subtitle")
        layout.addWidget(subtitle)
        layout.addSpacing(24)

        card = self._build_card()
        layout.addWidget(card, stretch=1)

        self.error_label = QLabel("")
        self.error_label.setObjectName("error")
        layout.addWidget(self.error_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.hide()
        layout.addWidget(self.progress)

        self.status_label = QLabel("")
        self.status_label.setObjectName("subtitle")
        layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        back_btn = QPushButton("Back")
        back_btn.setObjectName("secondary")
        back_btn.clicked.connect(self.done.emit)
        btn_layout.addWidget(back_btn)

        self.run_btn = QPushButton("Select .md Profile")
        self.run_btn.setObjectName("primary")
        self.run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_btn.clicked.connect(self._select_file)
        btn_layout.addWidget(self.run_btn)

        layout.addLayout(btn_layout)

    def _build_card(self) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(32, 28, 32, 28)
        vbox.setSpacing(12)

        card_title = QLabel("Upload Profile")
        card_title.setObjectName("cardTitle")
        vbox.addWidget(card_title)

        info = QLabel("Select a Markdown personality profile generated by this app or created manually.")
        info.setObjectName("cardSubtitle")
        info.setWordWrap(True)
        vbox.addWidget(info)

        self.file_label = QLabel("No file selected")
        self.file_label.setObjectName("cardSubtitle")
        vbox.addWidget(self.file_label)

        return card

    def _select_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Personality Profile", "", "Markdown files (*.md)")
        if not path:
            return
        self.file_label.setText(f"Selected: {Path(path).name}")
        self._run(Path(path))

    def _run(self, profile_path: Path) -> None:
        self.error_label.setText("")
        self.run_btn.setEnabled(False)
        self.progress.show()

        client = ApiClient(self.session.provider, self.session.api_key)
        self.worker = ImitationWorker(client, profile_path)
        self.worker.progress.connect(self.status_label.setText)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()

    def _on_finished(self, result: object) -> None:
        self.run_btn.setEnabled(True)
        self.progress.hide()
        self.status_label.setText("")

        if isinstance(result, ApiError):
            self.error_label.setText(str(result))
            return

        self.generated_skill_dir = Path(str(result))
        show_info(self, "Imitation skill generated successfully.")

        if confirm(self, "Launch the chat interface now?"):
            self.chat_ready.emit(str(self.generated_skill_dir))
        else:
            self.done.emit()


class ChatScreen(QWidget):
    done = Signal()

    def __init__(self, session: Session, skill_dir: str) -> None:
        super().__init__()
        self.session = session
        self.skill_dir = Path(skill_dir)
        self.system_prompt = load_imitation_skill(self.skill_dir)
        self.messages: list[Message] = [Message(role="system", content=self.system_prompt)]

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Chat")
        title.setObjectName("title")
        header.addWidget(title)

        back_btn = QPushButton("Back to Menu")
        back_btn.setObjectName("secondary")
        back_btn.clicked.connect(self.done.emit)
        header.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(header)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area, stretch=1)

        input_layout = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Type a message...")
        self.input_box.setMaximumHeight(80)
        input_layout.addWidget(self.input_box, stretch=1)

        send_btn = QPushButton("Send")
        send_btn.setObjectName("primary")
        send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        send_btn.clicked.connect(self._send)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)

        self._append("System", "Chat companion loaded. Start typing to talk.")

    def _append(self, sender: str, text: str) -> None:
        color = THEME["accent"] if sender == "You" else THEME["success"]
        self.chat_area.append(f"<b style='color:{color}'>{sender}:</b> {text}")

    def _send(self) -> None:
        text = self.input_box.toPlainText().strip()
        if not text:
            return
        self.input_box.clear()
        self._append("You", text)
        QApplication.processEvents()

        self.messages.append(Message(role="user", content=text))
        try:
            client = ApiClient(self.session.provider, self.session.api_key)
            reply = client.chat(self.messages, temperature=0.8)
        except ApiError as exc:
            show_error(self, format_key_error(self.session.provider, exc))
            return

        self.messages.append(Message(role="assistant", content=reply))
        self._append("Companion", reply)


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AI Personality & Imitation Companion")
        self.setMinimumSize(840, 620)
        self.resize(960, 700)

        self.session = Session.load()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.provider_screen = ProviderScreen(self.session)
        self.key_screen = ApiKeyScreen(self.session)
        self.menu_screen = MainMenuScreen(self.session)
        self.analysis_screen = PersonalityAnalysisScreen(self.session)
        self.imitation_screen = ImitationScreen(self.session)
        self.chat_screen: ChatScreen | None = None

        self.stack.addWidget(self.provider_screen)
        self.stack.addWidget(self.key_screen)
        self.stack.addWidget(self.menu_screen)
        self.stack.addWidget(self.analysis_screen)
        self.stack.addWidget(self.imitation_screen)

        self.provider_screen.selected.connect(self._show_key_screen)
        self.key_screen.submitted.connect(self._show_menu)
        self.key_screen.back.connect(self._show_provider_screen)
        self.menu_screen.personality.connect(self._show_analysis_screen)
        self.menu_screen.imitation.connect(self._show_imitation_screen)
        self.menu_screen.reset.connect(self._reset_session)
        self.analysis_screen.done.connect(self._show_menu)
        self.imitation_screen.done.connect(self._show_menu)
        self.imitation_screen.chat_ready.connect(self._show_chat_screen)

        self._restore_or_start()

    def _restore_or_start(self) -> None:
        if self.session.provider:
            self.provider_screen.selected_provider = self.session.provider
            if self.session.api_key:
                self._show_menu()
            else:
                self._show_key_screen()
        else:
            self._show_provider_screen()

    def _show_provider_screen(self) -> None:
        self.stack.setCurrentWidget(self.provider_screen)

    def _show_key_screen(self) -> None:
        self.key_screen.refresh()
        self.stack.setCurrentWidget(self.key_screen)

    def _show_menu(self) -> None:
        # Rebuild menu so the hint label stays fresh.
        self.menu_screen.deleteLater()
        self.menu_screen = MainMenuScreen(self.session)
        self.menu_screen.personality.connect(self._show_analysis_screen)
        self.menu_screen.imitation.connect(self._show_imitation_screen)
        self.menu_screen.reset.connect(self._reset_session)
        self.stack.insertWidget(2, self.menu_screen)
        self.stack.setCurrentWidget(self.menu_screen)

    def _show_analysis_screen(self) -> None:
        self.stack.setCurrentWidget(self.analysis_screen)

    def _show_imitation_screen(self) -> None:
        self.stack.setCurrentWidget(self.imitation_screen)

    def _show_chat_screen(self, skill_dir: str) -> None:
        if self.chat_screen:
            self.chat_screen.deleteLater()
        self.chat_screen = ChatScreen(self.session, skill_dir)
        self.chat_screen.done.connect(self._show_menu)
        self.stack.addWidget(self.chat_screen)
        self.stack.setCurrentWidget(self.chat_screen)

    def _reset_session(self) -> None:
        if confirm(self, "Reset API settings and return to the provider selection screen?"):
            self.session.reset()
            self.provider_screen.selected_provider = ""
            self._show_provider_screen()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> int:
    app = QApplication(sys.argv)
    apply_styles(app)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
