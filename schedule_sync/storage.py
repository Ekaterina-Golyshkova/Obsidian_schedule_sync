"""Настройки профилей и снимки расписания (JSON в ~/.schedule_sync)."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

DEFAULT_URL = (
    "https://docs.google.com/spreadsheets/d/1GyQ6IklpcoT7Sir6C7rNU9aNErDX1HWBg7Y1EK5T-nA"
    "/edit?gid=739453176#gid=739453176"
)


def data_dir() -> Path:                                                                                 #Определяет папку, в которой программа будет хранить все свои данные.
    p = Path(os.environ.get("SCHEDULE_SYNC_HOME") or Path.home() / ".schedule_sync")                    #Если пользователь не указал специальную папку через переменную окружения, используется домашняя директория пользователя
    p.mkdir(parents=True, exist_ok=True)
    return p


@dataclass
class Profile:                                      #Описывает профиль пользователя
    name: str
    sheet_url: str = DEFAULT_URL
    group: str = ""
    vault_path: str = ""
    folder: str = "Расписание"
    enabled: bool = True
    notify: bool = True


@dataclass
class Settings:                                     #Базовые настройки нашей программы
    interval_minutes: int = 30
    profiles: list[Profile] = field(default_factory=list)

    def get(self, name: str) -> Optional[Profile]:
        return next((p for p in self.profiles if p.name == name), None)


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def load_settings() -> Settings:
    f = data_dir() / "config.json"
    if not f.exists():
        return Settings()
    try:
        raw = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Settings()
    known = Profile.__dataclass_fields__.keys()
    profiles = [Profile(**{k: v for k, v in p.items() if k in known}) for p in raw.get("profiles", [])]
    return Settings(int(raw.get("interval_minutes", 30)), profiles)


def save_settings(s: Settings) -> None:
    _atomic_write(
        data_dir() / "config.json",
        json.dumps(
            {"interval_minutes": s.interval_minutes, "profiles": [asdict(p) for p in s.profiles]},
            ensure_ascii=False, indent=2,
        ),
    )


def _slug(name: str) -> str:
    return re.sub(r"[^\w.-]+", "_", name, flags=re.UNICODE).strip("_") or "profile"


def load_snapshot(profile: Profile) -> Optional[dict]:
    f = data_dir() / f"state_{_slug(profile.name)}.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def save_snapshot(profile: Profile, lessons: list[dict], updated: str) -> None:
    f = data_dir() / f"state_{_slug(profile.name)}.json"
    _atomic_write(
        f,
        json.dumps({"group": profile.group, "updated": updated, "lessons": lessons},
                   ensure_ascii=False),
    )
