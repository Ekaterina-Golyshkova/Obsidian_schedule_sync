"""Загрузка таблицы Google Sheets как CSV (таблица должна быть доступна по ссылке)."""
from __future__ import annotations

import csv
import io
import re
import urllib.error
import urllib.request

SHEET_ID_RE = re.compile(r"/spreadsheets/d/([a-zA-Z0-9_-]+)")
GID_RE = re.compile(r"[#&?]gid=(\d+)")


class FetchError(RuntimeError):
    pass


def parse_url(url: str) -> tuple[str, str]: #Разбивает ссылку на таблицу
    m = SHEET_ID_RE.search(url or "")
    if not m:
        raise FetchError("Не похоже на ссылку на Google Таблицу.")
    g = GID_RE.search(url)
    return m.group(1), (g.group(1) if g else "0")


def export_url(url: str) -> str: #Превращает сссылку в ссылку для скачивания
    sid, gid = parse_url(url)
    return f"https://docs.google.com/spreadsheets/d/{sid}/export?format=csv&gid={gid}"


def fetch_csv_text(url: str, timeout: int = 30) -> str: #Скачивает данные из ссылки и проверяет наличие ошибок
    req = urllib.request.Request(
        export_url(url), headers={"User-Agent": "Mozilla/5.0 (schedule-sync)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
            ctype = r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            raise FetchError(
                "Нет доступа к таблице. Нужен доступ «Все, у кого есть ссылка — Читатель»."
            ) from e
        raise FetchError(f"Ошибка загрузки таблицы: HTTP {e.code}") from e
    except urllib.error.URLError as e:
        raise FetchError(f"Нет соединения с Google: {e.reason}") from e

    text = data.decode("utf-8-sig", errors="replace")
    if "text/html" in ctype or text.lstrip().lower().startswith(("<!doctype", "<html")):
        raise FetchError(
            "Google вернул страницу входа вместо данных: таблица не открыта по ссылке."
        )
    return text


def to_rows(text: str) -> list[list[str]]: #Разбивает текст на столбцы и строки
    return list(csv.reader(io.StringIO(text, newline="")))


def fetch_rows(url: str, timeout: int = 30) -> list[list[str]]: #Объединяет две предудыщие функции
    return to_rows(fetch_csv_text(url, timeout))
