#!/usr/bin/env python3
"""User-owned settings profile for local scene image generation.

This module deliberately keeps the prompt/profile file outside tracked source
defaults. The GUI is the intended writer; generation scripts should only read it.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import stat
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = REPO_ROOT / "art" / "generated" / "local_scene_pipeline"
LOCKED_PROFILE_PATH = PROFILE_DIR / "scene_image_gui_profile.locked.json"
LEGACY_GUI_SETTINGS_PATH = PROFILE_DIR / "gui_settings.json"

PROFILE_KIND = "samandem_scene_image_gui_locked_profile"
PROFILE_NOTICE = (
    "User-owned prompt/settings profile. Codex and scripts should not edit this "
    "file directly. Use scripts/local_scene_image_gui.py to change it."
)


def set_writable(path: Path) -> None:
    if path.exists():
        path.chmod(stat.S_IREAD | stat.S_IWRITE)


def set_readonly(path: Path) -> None:
    if path.exists():
        path.chmod(stat.S_IREAD)


def unwrap_profile(data: dict[str, Any]) -> dict[str, Any]:
    settings = data.get("settings")
    if isinstance(settings, dict):
        return dict(settings)
    return dict(data)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Settings profile must be a JSON object: {path}")
    return data


def load_profile(path: Path = LOCKED_PROFILE_PATH) -> dict[str, Any]:
    if path.exists():
        return unwrap_profile(read_json(path))
    if LEGACY_GUI_SETTINGS_PATH.exists():
        return unwrap_profile(read_json(LEGACY_GUI_SETTINGS_PATH))
    return {}


def save_locked_profile(settings: dict[str, Any], path: Path = LOCKED_PROFILE_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    set_writable(path)
    payload = {
        "profile_kind": PROFILE_KIND,
        "notice": PROFILE_NOTICE,
        "owner": os.environ.get("USERNAME") or os.environ.get("USER") or "user",
        "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "settings": settings,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    set_readonly(path)
    return path


def ensure_locked_profile(default_settings: dict[str, Any], path: Path = LOCKED_PROFILE_PATH) -> tuple[Path, dict[str, Any]]:
    if path.exists():
        return path, load_profile(path)
    settings = dict(default_settings)
    if LEGACY_GUI_SETTINGS_PATH.exists():
        settings.update(load_profile(LEGACY_GUI_SETTINGS_PATH))
    return save_locked_profile(settings, path), settings
