"""Provide section detection service components for the application."""

import re
from typing import Any


NUMBERED_HEADING_PATTERN = re.compile(
    r"^(?:\d+(?:\.\d+)*[\.)]?\s+)"
)


def looks_like_heading(text: str) -> bool:
    """
    Detect likely headings in PDF/TXT text.
    """

    text = text.strip()

    if not text:
        return False

    if len(text) > 150:
        return False

    # Numbered headings:
    # 1 Introduction
    # 1.1 Methodology
    # 2.3 Results
    if NUMBERED_HEADING_PATTERN.match(text):
        return True

    # Markdown-like headings
    if text.startswith("#"):
        return True

    # Avoid normal long sentences.
    if text.endswith("."):
        return False

    words = text.split()

    if len(words) > 12:
        return False

    # Short title-like text
    if len(words) <= 8:
        uppercase_words = sum(
            1
            for word in words
            if word.isupper()
        )

        if uppercase_words >= max(
            1,
            len(words) // 2,
        ):
            return True

    return False


def detect_heading_level(
    text: str,
    style: str | None = None,
) -> int:
    """
    Determine heading hierarchy.
    """

    if style:
        match = re.search(
            r"Heading\s+(\d+)",
            style,
            flags=re.IGNORECASE,
        )

        if match:
            return int(match.group(1))

    match = re.match(
        r"^(\d+(?:\.\d+)*)",
        text.strip(),
    )

    if match:
        number = match.group(1)

        return number.count(".") + 1

    return 1


def detect_sections(
    document: dict[str, Any],
) -> dict[str, Any]:
    """
    Detect document sections while preserving
    page and heading metadata.
    """

    sections = []

    current_section = None

    # -----------------------------------------
    # DOCX-style structured elements
    # -----------------------------------------

    if document.get("elements"):

        for element in document["elements"]:

            text = element.get(
                "text",
                "",
            ).strip()

            if not text:
                continue

            if element.get("type") == "heading":

                if current_section:
                    sections.append(
                        current_section
                    )

                current_section = {
                    "section_id": len(sections) + 1,
                    "title": text,
                    "level": detect_heading_level(
                        text,
                        element.get("style"),
                    ),
                    "page_number": element.get(
                        "page_number"
                    ),
                    "content": [],
                }

            else:

                if current_section is None:

                    current_section = {
                        "section_id": 1,
                        "title": "Introduction",
                        "level": 1,
                        "page_number": None,
                        "content": [],
                    }

                current_section[
                    "content"
                ].append(text)

        if current_section:
            sections.append(
                current_section
            )

    # -----------------------------------------
    # PDF / TXT
    # -----------------------------------------

    else:

        for page in document.get(
            "pages",
            [],
        ):

            page_number = page.get(
                "page_number"
            )

            text = page.get(
                "text",
                "",
            )

            paragraphs = [
                paragraph.strip()
                for paragraph in re.split(
                    r"\n\s*\n",
                    text,
                )
                if paragraph.strip()
            ]

            for paragraph in paragraphs:

                lines = paragraph.splitlines()

                for line in lines:

                    line = line.strip()

                    if not line:
                        continue

                    if looks_like_heading(line):

                        if current_section:
                            sections.append(
                                current_section
                            )

                        current_section = {
                            "section_id": len(
                                sections
                            ) + 1,
                            "title": line,
                            "level": detect_heading_level(
                                line
                            ),
                            "page_number": page_number,
                            "content": [],
                        }

                    else:

                        if current_section is None:

                            current_section = {
                                "section_id": 1,
                                "title": "Introduction",
                                "level": 1,
                                "page_number": page_number,
                                "content": [],
                            }

                        current_section[
                            "content"
                        ].append(line)

    if current_section:
        sections.append(
            current_section
        )

    # -----------------------------------------
    # Build section text
    # -----------------------------------------

    for section in sections:

        section["text"] = "\n\n".join(
            section["content"]
        )

    return {
        **document,
        "sections": sections,
        "section_count": len(sections),
    }
