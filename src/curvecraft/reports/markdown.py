"""Markdown report helpers."""

from os import PathLike
from pathlib import Path


def write_markdown_report(path: str | PathLike[str], content: str) -> Path:
    """Write Markdown content to a file and return its path."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path
