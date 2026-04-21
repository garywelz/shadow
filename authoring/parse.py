from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable


_ZWSP_RE = re.compile(r"[\u200b\u200c\u200d\ufeff]")


def _clean(s: str) -> str:
    return _ZWSP_RE.sub("", s).strip()


_CHAPTER_HEADER_RE = re.compile(
    r"^(chapter\s+\d+|new\s+chapter\b.*|kungur\b.*chapter\b.*)$",
    re.IGNORECASE,
)


def is_chapter_header(line: str) -> bool:
    return bool(_CHAPTER_HEADER_RE.match(_clean(line)))


_DIVIDER_RE = re.compile(r"^\*{3,}\s*$")


def is_segment_divider(line: str) -> bool:
    return bool(_DIVIDER_RE.match(_clean(line)))


@dataclass(frozen=True)
class Segment:
    id: str
    text: str


@dataclass(frozen=True)
class Chapter:
    id: str
    title: str
    segments: list[Segment]


@dataclass(frozen=True)
class Manuscript:
    title: str
    chapters: list[Chapter]
    source_path: str | None = None


def _slugify(value: str) -> str:
    v = _clean(value).lower()
    v = re.sub(r"[^a-z0-9]+", "-", v).strip("-")
    return v or "untitled"


def split_segments(lines: Iterable[str]) -> list[str]:
    segments: list[list[str]] = [[]]
    for line in lines:
        if is_segment_divider(line):
            if segments[-1]:
                segments.append([])
            continue
        segments[-1].append(line)
    out: list[str] = []
    for block in segments:
        text = "\n".join(block).strip()
        if text:
            out.append(text)
    return out


def parse_chapters_from_markdown(text: str, *, manuscript_title: str = "The Shadow of Lillya") -> Manuscript:
    lines = text.splitlines()

    chapters: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for raw in lines:
        if is_chapter_header(raw):
            # flush previous
            if current_title is not None:
                chapters.append((current_title, current_lines))
            current_title = _clean(raw)
            current_lines = []
            continue
        if current_title is None:
            # ignore preamble until first chapter marker
            continue
        current_lines.append(raw)

    if current_title is not None:
        chapters.append((current_title, current_lines))

    parsed: list[Chapter] = []
    for idx, (title, body_lines) in enumerate(chapters, start=1):
        seg_texts = split_segments(body_lines)
        segs: list[Segment] = []
        for sidx, seg_text in enumerate(seg_texts, start=1):
            seg_id = f"{idx:03d}-{sidx:03d}"
            segs.append(Segment(id=seg_id, text=seg_text))
        chap_id = f"ch-{idx:03d}-{_slugify(title)[:40]}"
        parsed.append(Chapter(id=chap_id, title=title, segments=segs))

    # If no explicit chapter headers were found, treat the whole text as one chapter.
    if not parsed:
        seg_texts = split_segments(lines)
        segs = [Segment(id=f"001-{i:03d}", text=t) for i, t in enumerate(seg_texts, start=1)]
        parsed = [Chapter(id="ch-001-draft", title="Draft", segments=segs)]

    return Manuscript(title=manuscript_title, chapters=parsed)


def manuscript_to_dict(m: Manuscript) -> dict:
    return {
        "title": m.title,
        "source_path": m.source_path,
        "chapters": [
            {
                "id": c.id,
                "title": c.title,
                "segments": [{"id": s.id, "text": s.text} for s in c.segments],
            }
            for c in m.chapters
        ],
    }


def dict_to_manuscript(data: dict) -> Manuscript:
    chapters: list[Chapter] = []
    for c in data.get("chapters", []):
        segs = [Segment(id=s["id"], text=s.get("text", "")) for s in c.get("segments", [])]
        chapters.append(Chapter(id=c["id"], title=c.get("title", ""), segments=segs))
    return Manuscript(title=data.get("title", "Manuscript"), chapters=chapters, source_path=data.get("source_path"))


def manuscript_to_markdown(m: Manuscript) -> str:
    parts: list[str] = [f"# {m.title}".strip(), ""]
    for i, c in enumerate(m.chapters, start=1):
        parts.append(f"## {c.title or f'Chapter {i}'}".strip())
        parts.append("")
        for s in c.segments:
            parts.append(s.text.strip())
            parts.append("")
            parts.append("***")
            parts.append("")
    return "\n".join(parts).rstrip() + "\n"

