from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class VersionInfo:
    name: str
    path: Path
    created_at: str | None = None
    based_on: str | None = None


def _is_writable_dir(p: Path) -> bool:
    try:
        p.mkdir(parents=True, exist_ok=True)
        test = p / ".write_test"
        test.write_text("ok", encoding="utf-8")
        test.unlink(missing_ok=True)
        return True
    except Exception:
        return False


def get_versions_root() -> tuple[Path, bool]:
    """
    Returns (root_dir, is_persistent_like).
    Prefers /data when available (HF persistent storage), otherwise uses repo-local storage.
    """
    data_root = Path("/data/shadow_versions")
    if _is_writable_dir(data_root):
        return data_root, True
    local_root = Path("shadow_versions")
    _is_writable_dir(local_root)  # best-effort
    return local_root, False


def list_versions() -> list[VersionInfo]:
    root, _ = get_versions_root()
    infos: list[VersionInfo] = []
    for p in sorted(root.glob("*.json")):
        name = p.stem
        created_at: Optional[str] = None
        based_on: Optional[str] = None
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            meta = data.get("meta", {}) if isinstance(data, dict) else {}
            created_at = meta.get("created_at")
            based_on = meta.get("based_on")
        except Exception:
            pass
        infos.append(VersionInfo(name=name, path=p, created_at=created_at, based_on=based_on))
    return infos


def load_version(name: str) -> dict:
    root, _ = get_versions_root()
    path = root / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def save_version(name: str, payload: dict) -> Path:
    root, _ = get_versions_root()
    path = root / f"{name}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

