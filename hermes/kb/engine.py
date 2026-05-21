"""
Knowledge Base Engine — Karpathy's LLM Wiki pattern.

Persistent, compounding, cross-referenced knowledge base.
Every page has bidirectional links. Contradictions are flagged, not hidden.
Synthesis pages tie individual facts into understanding.
"""

import os
import re
import time
from pathlib import Path
from datetime import datetime
from typing import Optional


WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
CONTRADICTION_MARKER = "⚠️ CONTRADICTION:"


class KbEngine:
    """
    LLM Wiki pattern implementation.

    Usage:
        kb = KbEngine("/home/hermes/.hermes/kb")
        kb.write("vulnerability-classes/web2/sqli/time-based", content)
        kb.read("vulnerability-classes/web2/sqli/time-based")
        links = kb.get_backlinks("vulnerability-classes/web2/sqli")
    """

    def __init__(self, base_dir: str = "hermes/kb"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def read(self, page_path: str) -> Optional[str]:
        """Read a wiki page by path (relative to kb/)."""
        full_path = self._resolve(page_path)
        if not full_path.exists():
            return None
        return full_path.read_text()

    def write(self, page_path: str, content: str, author: str = "prometheus") -> str:
        """
        Write or update a wiki page. Auto-adds metadata header.
        Returns the full resolved path.
        """
        full_path = self._resolve(page_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata header if not present
        if not content.startswith("# "):
            title = page_path.split("/")[-1].replace("-", " ").replace(".md", "").title()
            metadata = (
                f"# {title}\n\n"
                f"*Last updated: {datetime.utcnow().isoformat()} | Author: {author}*\n\n"
            )
            content = metadata + content

        # Extract and validate wiki links
        links = WIKI_LINK_RE.findall(content)

        full_path.write_text(content)

        # If this is an update to an existing page, detect contradictions
        if full_path.exists():
            old_text = full_path.read_text()
            # Flag if key claims changed dramatically
            old_links = set(WIKI_LINK_RE.findall(old_text))
            new_links = set(links)
            removed = old_links - new_links
            if removed:
                # Don't block the write, but could log a warning
                pass

        full_path.write_text(content)
        return str(full_path)

    def append_section(self, page_path: str, heading: str, section_content: str) -> None:
        """Append a new section to an existing page."""
        existing = self.read(page_path) or ""
        new_section = f"\n\n## {heading}\n\n{section_content}\n"
        self.write(page_path, existing + new_section)

    def flag_contradiction(self, page_path: str, contradiction_note: str) -> None:
        """Flag a contradiction on a wiki page."""
        flag = f"\n\n{CONTRADICTION_MARKER} {contradiction_note}\n"
        existing = self.read(page_path) or ""
        if CONTRADICTION_MARKER not in existing:
            self.write(page_path, existing + flag)

    def resolve_contradiction(self, page_path: str, resolution: str) -> None:
        """Resolve a contradiction by replacing all flags."""
        content = self.read(page_path) or ""
        content = re.sub(
            rf"{re.escape(CONTRADICTION_MARKER)}.*?\n",
            f"✅ RESOLVED: {resolution}\n",
            content,
        )
        self.write(page_path, content)

    def get_backlinks(self, page_path: str) -> list[str]:
        """Find all pages that link to the given page."""
        page_name = page_path.split("/")[-1].replace(".md", "")
        referrers = []

        for md_file in self.base_dir.rglob("*.md"):
            if md_file == self._resolve(page_path):
                continue
            try:
                text = md_file.read_text()
                if page_name.lower() in text.lower():
                    referrers.append(str(md_file.relative_to(self.base_dir)))
            except Exception:
                pass

        return sorted(referrers)

    def get_orphans(self) -> list[str]:
        """Find pages with no incoming links."""
        all_pages = [
            str(p.relative_to(self.base_dir))
            for p in self.base_dir.rglob("*.md")
            if p.name != "index.md"
        ]

        orphans = []
        for page in all_pages:
            backlinks = self.get_backlinks(page)
            if not backlinks:
                orphans.append(page)

        return sorted(orphans)

    def search(self, query: str) -> list[dict]:
        """Full-text search across knowledge base."""
        results = []
        query_lower = query.lower()

        for md_file in self.base_dir.rglob("*.md"):
            try:
                text = md_file.read_text()
                if query_lower in text.lower():
                    # Find the matching line
                    lines = text.split("\n")
                    matches = [line.strip() for line in lines if query_lower in line.lower()]

                    results.append({
                        "page": str(md_file.relative_to(self.base_dir)),
                        "matches": matches[:5],  # First 5 matches
                        "match_count": len(matches),
                    })
            except Exception:
                pass

        return sorted(results, key=lambda r: r["match_count"], reverse=True)

    def get_index(self) -> dict:
        """Get KB index with page statistics."""
        pages = []
        for md_file in self.base_dir.rglob("*.md"):
            try:
                text = md_file.read_text()
                pages.append({
                    "path": str(md_file.relative_to(self.base_dir)),
                    "size": len(text),
                    "links_out": len(WIKI_LINK_RE.findall(text)),
                    "has_contradictions": CONTRADICTION_MARKER in text,
                })
            except Exception:
                pass

        return {
            "total_pages": len(pages),
            "total_size": sum(p["size"] for p in pages),
            "pages": sorted(pages, key=lambda p: p["path"]),
        }

    def _resolve(self, page_path: str) -> Path:
        """Resolve a page path, ensuring .md extension."""
        path = self.base_dir / page_path
        if not path.suffix:
            path = path.with_suffix(".md")
        return path
