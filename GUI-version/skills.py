"""Skill execution helpers for the GUI.

The declarative skill files under `.trae/skills/` are prompt templates. This
module loads them, builds the appropriate system/user prompts, sends them to the
configured API, and writes the results to the `GUI-version` folder tree.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Callable

from api_client import ApiClient, ApiError, Message


PROJECT_ROOT = Path(__file__).resolve().parent
SKILL_ROOT = PROJECT_ROOT.parent / "skills"
TEMP_DIR = PROJECT_ROOT / "temp"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
GENERATED_DIR = PROJECT_ROOT / "skills_generated"


def _read(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _encode_image(path: Path) -> str:
    """Return a base64 data URI for supported image types."""
    import base64
    import mimetypes

    mime, _ = mimetypes.guess_type(str(path))
    if mime is None:
        mime = "application/octet-stream"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def _gather_evidence(extracted_dir: Path) -> list[Message]:
    """Convert extracted evidence files into API messages.

    Text files are appended inline; images are embedded as data URIs.
    """
    messages: list[Message] = []
    text_extensions = {".txt", ".md", ".log", ".json", ".csv"}
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".heic"}

    files = sorted(extracted_dir.iterdir())
    for file in files:
        if not file.is_file():
            continue
        suffix = file.suffix.lower()
        if suffix in text_extensions:
            messages.append(Message(role="user", content=f"--- {file.name} ---\n{file.read_text(encoding='utf-8', errors='ignore')}"))
        elif suffix in image_extensions:
            messages.append(
                Message(
                    role="user",
                    content=f"Image: {file.name}\n![{file.name}]({_encode_image(file)})",
                )
            )
        elif suffix == ".pdf":
            # Best-effort: note that PDF text extraction is not implemented in stdlib.
            messages.append(Message(role="user", content=f"PDF file present: {file.name}. Extracted text is not available in this build."))
        else:
            messages.append(Message(role="user", content=f"Additional file: {file.name}"))

    return messages


def _extract_zip(zip_path: Path) -> Path:
    """Extract a zip archive to a unique temp subfolder and return that path."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = TEMP_DIR / f"evidence_{stamp}"
    dest.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest)

    # Flatten one level if the archive contains a single root folder.
    children = [p for p in dest.iterdir() if not p.name.startswith(".")]
    if len(children) == 1 and children[0].is_dir():
        nested = children[0]
        for item in nested.iterdir():
            shutil.move(str(item), str(dest / item.name))
        nested.rmdir()

    return dest


def _sanitize_filename(name: str) -> str:
    return re.sub(r"[^\w\-]+", "_", name).strip("_") or "profile"


def _subject_alias_from_profile(profile_text: str) -> str:
    match = re.search(r"subject_alias:\s*(.+)", profile_text)
    if match:
        return _sanitize_filename(match.group(1).strip())
    return "subject"


def run_personality_analysis(
    client: ApiClient,
    zip_path: Path,
    progress_callback: Callable[[str], None] | None = None,
) -> Path:
    """Run the personality-analysis skill on a zip of evidence.

    Returns the path to the generated `.md` profile saved in `outputs/`.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    def emit(msg: str) -> None:
        if progress_callback:
            progress_callback(msg)

    emit("Extracting evidence archive...")
    extracted = _extract_zip(zip_path)

    emit("Reading skill instructions...")
    skill_file = SKILL_ROOT / "personality-analysis-skill" / "SKILL.md"
    rubric_file = SKILL_ROOT / "personality-analysis-skill" / "references" / "analysis_rubric.md"
    template_file = SKILL_ROOT / "personality-analysis-skill" / "templates" / "personality_profile.template.md"

    system_prompt = (
        "You are an expert personality analyst. Follow the skill definition below exactly.\n\n"
        + _read(skill_file)
    )
    if rubric_file.exists():
        system_prompt += "\n\n--- Analysis Rubric ---\n" + _read(rubric_file)
    if template_file.exists():
        system_prompt += "\n\n--- Output Template ---\n" + _read(template_file)

    evidence_messages = _gather_evidence(extracted)
    if not evidence_messages:
        raise ApiError("No usable evidence files found in the archive.")

    emit("Analyzing personality (this may take a moment)...")
    messages = [Message(role="system", content=system_prompt)] + evidence_messages
    messages.append(
        Message(
            role="user",
            content=(
                "Using all evidence above, produce the complete personality profile "
                "following the required schema and output template exactly."
            ),
        )
    )
    profile_text = client.chat(messages, temperature=0.4)

    alias = _subject_alias_from_profile(profile_text)
    out_path = OUTPUT_DIR / f"{alias}_personality_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    out_path.write_text(profile_text, encoding="utf-8")

    emit(f"Saved profile to {out_path.name}")
    return out_path


def generate_imitation_skill(
    client: ApiClient,
    profile_path: Path,
    progress_callback: Callable[[str], None] | None = None,
) -> Path:
    """Generate an imitation-skill directory from a personality profile.

    Returns the path to the generated skill folder under `skills_generated/`.
    """
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    def emit(msg: str) -> None:
        if progress_callback:
            progress_callback(msg)

    emit("Reading imitation skill template...")
    skill_file = SKILL_ROOT / "imitation-skill-generator" / "SKILL.md"
    template_file = SKILL_ROOT / "imitation-skill-generator" / "templates" / "imitation-skill.template.md"

    profile_text = profile_path.read_text(encoding="utf-8")
    alias = _subject_alias_from_profile(profile_text)

    system_prompt = (
        "You are an expert prompt engineer. Follow the skill generator definition below exactly.\n\n"
        + _read(skill_file)
    )
    if template_file.exists():
        system_prompt += "\n\n--- Skill Template ---\n" + _read(template_file)

    emit("Building imitation skill...")
    messages = [
        Message(role="system", content=system_prompt),
        Message(role="user", content=f"Profile file: {profile_path.name}\n\n{profile_text}"),
        Message(
            role="user",
            content=(
                "Generate the complete imitation SKILL.md for this profile, using the template above. "
                "The skill should faithfully replicate the subject's voice in a chat. "
                "Return only the SKILL.md content."
            ),
        ),
    ]
    skill_text = client.chat(messages, temperature=0.3)

    skill_dir = GENERATED_DIR / f"imitation-{alias}"
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(skill_text, encoding="utf-8")

    ref_dir = skill_dir / "references"
    ref_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(profile_path, ref_dir / f"{alias}_personality_profile.md")

    emit(f"Saved imitation skill to {skill_dir.name}")
    return skill_dir


def load_imitation_skill(skill_dir: Path) -> str:
    """Load the raw SKILL.md content from a generated imitation skill folder."""
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        raise ApiError("Generated imitation skill is missing its SKILL.md file.")
    return _read(skill_file)
