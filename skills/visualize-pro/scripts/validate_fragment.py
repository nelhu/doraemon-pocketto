#!/usr/bin/env python3
"""Read-only structural validator for Visualize Pro HTML fragments."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
MAX_BYTES = 2 * 1024 * 1024
DOCUMENT_TAGS = {"html", "head", "body"}
FORBIDDEN_TAGS = {"base", "embed", "iframe", "link", "object"}
VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
NETWORK_APIS = {
    "fetch": re.compile(r"\bfetch\s*\("),
    "XMLHttpRequest": re.compile(r"\bXMLHttpRequest\b"),
    "WebSocket": re.compile(r"\bWebSocket\s*\("),
    "EventSource": re.compile(r"\bEventSource\s*\("),
    "sendBeacon": re.compile(r"\bsendBeacon\s*\("),
    "dynamic import": re.compile(r"\bimport\s*\("),
}
REMOTE_CSS_PATTERN = re.compile(
    r"(?:url\(\s*['\"]?\s*https?://|@import\s+(?:url\()?['\"]?\s*https?://)",
    re.I,
)


class FragmentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[str] = []
        self.ids: list[str] = []
        self.urls: list[str] = []
        self.depth = 0
        self.top_level_elements: list[tuple[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        self.tags.append(lowered)
        attributes = {name.lower(): value for name, value in attrs}
        if self.depth == 0:
            self.top_level_elements.append((lowered, attributes.get("id")))
        for name, value in attrs:
            if name.lower() == "id" and value:
                self.ids.append(value)
            if name.lower() in {"href", "poster", "src", "srcset"} and value:
                self.urls.append(value.strip())
        if lowered not in VOID_TAGS:
            self.depth += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS:
            self.depth = max(0, self.depth - 1)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() not in VOID_TAGS:
            self.depth = max(0, self.depth - 1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fragment", type=Path, help="Path to the HTML fragment")
    return parser.parse_args()


def validate(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not path.is_file():
        return [f"file not found: {path}"], warnings
    if path.suffix.lower() != ".html":
        errors.append("fragment must use a .html extension")

    size = path.stat().st_size
    if size > MAX_BYTES:
        errors.append(f"fragment is {size} bytes; maximum is {MAX_BYTES}")

    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return errors + ["fragment is not valid UTF-8"], warnings

    parser = FragmentParser()
    try:
        parser.feed(source)
    except Exception as exc:  # HTMLParser errors are rare but should stay visible.
        errors.append(f"could not parse fragment: {exc}")

    if re.search(r"<!doctype\b", source, re.I):
        errors.append("doctype is forbidden; write an HTML fragment")
    forbidden_tags = sorted(DOCUMENT_TAGS.intersection(parser.tags))
    if forbidden_tags:
        errors.append(f"document tags are forbidden: {', '.join(forbidden_tags)}")
    forbidden_embeds = sorted(FORBIDDEN_TAGS.intersection(parser.tags))
    if forbidden_embeds:
        errors.append(f"embedded or external document tags are forbidden: {', '.join(forbidden_embeds)}")
    if re.search(r"<script\b[^>]*\bsrc\s*=", source, re.I):
        errors.append("external script sources are forbidden")

    if len(parser.top_level_elements) != 1:
        errors.append(
            "fragment needs exactly one top-level root element; "
            f"found {len(parser.top_level_elements)}"
        )
    elif not parser.top_level_elements[0][1]:
        errors.append("the top-level root element needs a unique id")
    duplicate_ids = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
    if duplicate_ids:
        errors.append(f"duplicate id values: {', '.join(duplicate_ids)}")

    known_ids = set(parser.ids)
    referenced_ids = set(
        re.findall(
            r"(?:getElementById|querySelector)\s*\(\s*['\"]#?([A-Za-z][\w:.-]*)['\"]\s*\)",
            source,
        )
    )
    missing_ids = sorted(referenced_ids - known_ids)
    if missing_ids:
        errors.append(f"JavaScript references missing id values: {', '.join(missing_ids)}")

    for api, pattern in NETWORK_APIS.items():
        if pattern.search(source):
            errors.append(f"runtime network API is forbidden: {api}")

    for url in parser.urls:
        lowered = url.lower()
        if (
            lowered.startswith("#")
            or lowered.startswith("data:")
            or lowered.startswith("blob:")
        ):
            continue
        errors.append(f"external or navigational resource is forbidden: {url}")
    if REMOTE_CSS_PATTERN.search(source):
        errors.append("remote CSS resources are forbidden")

    css_checks = {
        "position: fixed": r"position\s*:\s*fixed\b",
        "100vh": r"\b100vh\b",
        "100vw": r"\b100vw\b",
    }
    for label, pattern in css_checks.items():
        if re.search(pattern, source, re.I):
            errors.append(f"forbidden layout pattern: {label}")

    if re.search(r"overflow(?:-y)?\s*:\s*(?:auto|scroll)\b", source, re.I):
        warnings.append(
            "internal vertical scrolling detected; inline widgets should use natural "
            "height and let the renderer report intrinsic height"
        )

    if "\\n" in source or '\\"' in source:
        warnings.append("source contains escaped newline or quote sequences; verify it was not double-escaped")
    if "<svg" in source.lower() and not re.search(r"<title(?:\s|>)", source, re.I):
        warnings.append("SVG has no <title>; add an accessible name")
    if "<script" in source.lower() and "prefers-reduced-motion" not in source:
        warnings.append("scripted visual does not mention prefers-reduced-motion")
    if not re.search(r"aria-label(?:ledby)?\s*=", source, re.I):
        warnings.append("no aria-label or aria-labelledby found on the fragment")

    return errors, warnings


def main() -> int:
    args = parse_args()
    errors, warnings = validate(args.fragment.expanduser().resolve())

    for message in warnings:
        print(f"WARNING: {message}")
    for message in errors:
        print(f"ERROR: {message}")

    if errors:
        print(f"FAIL: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1

    print(f"PASS: 0 errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
