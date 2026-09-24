import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from app.core.qwen import load_qwen_model
from app.services.qwen_service import generate_text
from app.utils.pdf_processor import extract_pdf_content


MAX_WORKERS = 2

CHUNK_SIZE = 1200
OVERLAP = 150


# ============================================================
# DOCUMENT PATH
# ============================================================

DOCUMENT_PATH = r"C:/Users/itidol/Desktop/Jaimi/AI Image Description & Document Summarization — Complete Task List.pdf"


# ============================================================
# CHUNKING
# ============================================================

def split_words(text, chunk_size=1200, overlap=150):

    words = text.split()

    if not words:
        return []

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words)
        )

        chunk = " ".join(
            words[start:end]
        )

        chunks.append(chunk)

        if end >= len(words):
            break

        start = end - overlap

    return chunks


# ============================================================
# PROMPT
# ============================================================

def build_prompt(text):

    return f"""
You are summarizing a document.

Use ONLY the provided document text.

Do not use outside knowledge.
Do not invent facts.
Do not add information that is not present in the text.

Create a concise factual summary of this chunk.

DOCUMENT TEXT:
{text}

SUMMARY:
"""


# ============================================================
# SINGLE CHUNK
# ============================================================

def summarize_chunk(
    model,
    processor,
    chunk,
    chunk_number,
):

    start = time.perf_counter()

    prompt = build_prompt(chunk)

    summary = generate_text(
        model=model,
        processor=processor,
        prompt=prompt,
        max_new_tokens=300,
    )

    elapsed = time.perf_counter() - start

    return {
        "chunk_id": chunk_number,
        "word_count": len(chunk.split()),
        "summary": summary.strip(),
        "time": elapsed,
    }


# ============================================================
# SEQUENTIAL
# ============================================================

def run_sequential(
    model,
    processor,
    chunks,
):

    print("\n" + "=" * 70)
    print("SEQUENTIAL TEST")
    print("=" * 70)

    start = time.perf_counter()

    results = []

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):

        print(
            f"\nProcessing chunk "
            f"{index}/{len(chunks)}..."
        )

        result = summarize_chunk(
            model,
            processor,
            chunk,
            index,
        )

        results.append(result)

        print(
            f"Chunk {index} completed in "
            f"{result['time']:.2f} seconds"
        )

    total_time = (
        time.perf_counter() - start
    )

    return results, total_time


# ============================================================
# MULTITHREADED
# ============================================================

def run_multithreaded(
    model,
    processor,
    chunks,
):

    print("\n" + "=" * 70)
    print(
        f"MULTITHREADED TEST "
        f"({MAX_WORKERS} WORKERS)"
    )
    print("=" * 70)

    start = time.perf_counter()

    results = []

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = {
            executor.submit(
                summarize_chunk,
                model,
                processor,
                chunk,
                index,
            ): index
            for index, chunk
            in enumerate(chunks, start=1)
        }

        for future in as_completed(
            futures
        ):

            chunk_id = futures[future]

            try:

                result = future.result()

                results.append(result)

                print(
                    f"Chunk {chunk_id} completed in "
                    f"{result['time']:.2f} seconds"
                )

            except Exception as e:

                print(
                    f"Chunk {chunk_id} FAILED: {e}"
                )

    results.sort(
        key=lambda x: x["chunk_id"]
    )

    total_time = (
        time.perf_counter() - start
    )

    return results, total_time


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("QWEN MULTITHREADING DOCUMENT TEST")
    print("=" * 70)

    # --------------------------------------------------------
    # Validate path
    # --------------------------------------------------------

    path = Path(DOCUMENT_PATH)

    if not path.exists():

        print(
            f"\nERROR: File not found:\n{path}"
        )

        return

    print(
        f"\nDocument: {path}"
    )

    # --------------------------------------------------------
    # Extract using your existing PDF processor
    # --------------------------------------------------------

    print(
        "\nExtracting document text..."
    )

    document = extract_pdf_content(path)

    text = document.get(
        "text",
        ""
    ).strip()

    if not text:

        print(
            "\nERROR: No text extracted."
        )

        return

    print(
        f"Extracted words: "
        f"{len(text.split())}"
    )

    # --------------------------------------------------------
    # Create chunks
    # --------------------------------------------------------

    chunks = split_words(
        text,
        chunk_size=CHUNK_SIZE,
        overlap=OVERLAP,
    )

    print(
        f"Number of chunks: "
        f"{len(chunks)}"
    )

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):

        print(
            f"  Chunk {index}: "
            f"{len(chunk.split())} words"
        )

    # --------------------------------------------------------
    # Load Qwen
    # --------------------------------------------------------

    print(
        "\nLoading Qwen model..."
    )

    model, processor = load_qwen_model()

    print(
        "Qwen model loaded."
    )

    # --------------------------------------------------------
    # Sequential
    # --------------------------------------------------------

    sequential_results, sequential_time = (
        run_sequential(
            model,
            processor,
            chunks,
        )
    )

    # --------------------------------------------------------
    # Multithreading
    # --------------------------------------------------------

    threaded_results, threaded_time = (
        run_multithreaded(
            model,
            processor,
            chunks,
        )
    )

    # --------------------------------------------------------
    # Comparison
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL COMPARISON")
    print("=" * 70)

    print(
        f"\nSequential      : "
        f"{sequential_time:.2f} seconds"
    )

    print(
        f"Multithreaded   : "
        f"{threaded_time:.2f} seconds"
    )

    if threaded_time < sequential_time:

        improvement = (
            (
                sequential_time
                - threaded_time
            )
            / sequential_time
        ) * 100

        print(
            f"\nMultithreading was "
            f"{improvement:.2f}% faster."
        )

    elif threaded_time > sequential_time:

        slowdown = (
            (
                threaded_time
                - sequential_time
            )
            / sequential_time
        ) * 100

        print(
            f"\nMultithreading was "
            f"{slowdown:.2f}% slower."
        )

    else:

        print(
            "\nBoth approaches took "
            "approximately the same time."
        )


if __name__ == "__main__":
    main()