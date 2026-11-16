"""Sherlock (github.com/sherlock-project/sherlock) ni ishga tushirib,
topilgan profillarni oqim (stream) ko'rinishida qaytaradi."""
import asyncio
import re
import shutil
import sys
import tempfile
from typing import AsyncIterator

from config import MAX_PARALLEL_SEARCHES, SHERLOCK_TIMEOUT

USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{2,40}$")
FOUND_RE = re.compile(r"^\[\+\]\s*([^:]+):\s*(https?://\S+)")

_semaphore = asyncio.Semaphore(MAX_PARALLEL_SEARCHES)
_active_users: set[int] = set()


class SearchBusy(Exception):
    pass


def is_valid_username(username: str) -> bool:
    return bool(USERNAME_RE.match(username))


def _sherlock_cmd(username: str) -> list[str]:
    base = [shutil.which("sherlock")] if shutil.which("sherlock") else [sys.executable, "-m", "sherlock_project"]
    return base + [username, "--print-found", "--no-color", "--timeout", str(SHERLOCK_TIMEOUT)]


async def search(username: str, user_id: int) -> AsyncIterator[dict]:
    """Har bir topilgan profil uchun {"site": ..., "url": ...} beradi."""
    if not is_valid_username(username):
        raise ValueError("Username noto'g'ri")
    if user_id in _active_users:
        raise SearchBusy("Sizda allaqachon qidiruv ketyapti")

    _active_users.add(user_id)
    try:
        async with _semaphore:
            with tempfile.TemporaryDirectory() as tmp:  # sherlock .txt faylini shu yerga yozadi
                proc = await asyncio.create_subprocess_exec(
                    *_sherlock_cmd(username),
                    cwd=tmp,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                try:
                    assert proc.stdout
                    async for raw in proc.stdout:
                        m = FOUND_RE.match(raw.decode(errors="ignore").strip())
                        if m:
                            yield {"site": m.group(1).strip(), "url": m.group(2)}
                    await proc.wait()
                finally:
                    if proc.returncode is None:
                        proc.kill()
                        await proc.wait()
    finally:
        _active_users.discard(user_id)
