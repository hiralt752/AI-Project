"""Provide checksum components for the application."""

import hashlib


async def calculate_sha256(file) -> str:

    """Calculate the SHA-256 checksum of an uploaded file."""

    sha256 = hashlib.sha256()

    while True:

        chunk = await file.read(1024 * 1024)

        if not chunk:
            break

        sha256.update(chunk)

    await file.seek(0)

    return sha256.hexdigest()
