"""Provide chunking service components for the application."""

from typing import Any


DEFAULT_CHUNK_SIZE = 1200
DEFAULT_OVERLAP = 150


def split_words(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:

    """Split words."""

    words = text.split()

    if not words:
        return []

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than 0."
        )

    if overlap < 0:
        raise ValueError(
            "overlap cannot be negative."
        )

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words),
        )

        chunk = " ".join(
            words[start:end]
        )

        if chunk.strip():
            chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


def create_chunks(
    document: dict[str, Any],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[dict[str, Any]]:
    """
    Split the complete document text into chunks.

    The complete document text is used directly.

    Section detection is not required.

    Example:

        1379 words
        chunk_size = 1200
        overlap = 150

        Chunk 1:
            words 1 - 1200

        Chunk 2:
            words 1051 - 1379

    No document text is discarded.
    """

    text = str(
        document.get(
            "text",
            "",
        )
    ).strip()

    if not text:
        return []

    text_chunks = split_words(
        text=text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    chunks = []

    for index, chunk_text in enumerate(
        text_chunks
    ):

        chunks.append(
            {
                "chunk_id": index + 1,

                "chunk_index": index,

                "text": chunk_text,

                "word_count": len(
                    chunk_text.split()
                ),
            }
        )

    return chunks
