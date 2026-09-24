"""Provide document pipeline service components for the application."""

import time
from typing import Any

from app.services.document_cleaning_service import (
    clean_document,
)

from app.services.chunking_service import (
    create_chunks,
)

from app.services.summarization_service import (
    SummarizationService,
)

from app.services.structured_extraction_service import (
    StructuredExtractionService,
)


class DocumentPipelineService:
    """
    Complete document processing pipeline.

    Pipeline:

        Document
            ↓
        Cleaning
            ↓
        Complete Document Text
            ↓
        Chunking
            ↓
        Summarization
            ↓
        Structured Extraction
            ↓
        Final Result

    Section detection is intentionally not used here.
    The complete cleaned document text is the source
    of truth for summarization and extraction.
    """

    def __init__(self, model, processor):

        """Initialize the instance."""

        self.model = model
        self.processor = processor

        self.summarizer = SummarizationService(
            model=self.model,
            processor=self.processor,
        )

        self.extractor = StructuredExtractionService(
            model=self.model,
            processor=self.processor,
        )

    def process(
        self,
        document: dict[str, Any],
        summary_mode: str = "Standard",
        extract_structured: bool = True,
    ) -> dict[str, Any]:

        """Process."""

        start_time = time.perf_counter()

        # =====================================================
        # STEP 1 — DOCUMENT CLEANING
        # =====================================================

        cleaned_document = clean_document(
            document
        )

        # =====================================================
        # STEP 2 — GET COMPLETE DOCUMENT TEXT
        # =====================================================

        source_text = str(
            cleaned_document.get(
                "text",
                "",
            )
        ).strip()

        if not source_text:
            raise ValueError(
                "No usable text was extracted from the document."
            )

        print(
            f"[PIPELINE] Document text extracted: "
            f"{len(source_text.split())} words"
        )

        # =====================================================
        # STEP 3 — CHUNK COMPLETE DOCUMENT
        # =====================================================

        chunks = create_chunks(
            cleaned_document
        )

        if not chunks:
            raise ValueError(
                "No usable text chunks were created."
            )

        print(
            f"[PIPELINE] Created {len(chunks)} document chunks."
        )

        # =====================================================
        # STEP 4 — DOCUMENT SUMMARIZATION
        # =====================================================

        summary_result = (
            self.summarizer.summarize_document(
                chunks=chunks,
                mode=summary_mode,
            )
        )

        # =====================================================
        # STEP 5 — STRUCTURED EXTRACTION
        # =====================================================

        structured_data = {}

        if extract_structured:

            structured_data = (
                self.extractor.extract(
                    text=source_text,
                    include_semantic=True,
                )
            )

        # =====================================================
        # STEP 6 — PROCESSING TIME
        # =====================================================

        processing_time = (
            time.perf_counter()
            - start_time
        )

        # =====================================================
        # STEP 7 — EXTRACT STRUCTURED FIELDS
        # =====================================================

        key_points = structured_data.get(
            "key_points",
            [],
        )

        entities = structured_data.get(
            "entities",
            [],
        )

        decisions = structured_data.get(
            "decisions",
            [],
        )

        action_items = structured_data.get(
            "action_items",
            [],
        )

        warnings = structured_data.get(
            "warnings",
            [],
        )

        # =====================================================
        # STEP 8 — FINAL RESULT
        # =====================================================

        return {

            "summary_mode": summary_mode,

            "summary": summary_result.get(
                "summary",
                "",
            ),

            "key_points": key_points,

            "section_summaries": [],

            "entities": entities,

            "decisions": decisions,

            "action_items": action_items,

            "chunk_count": len(chunks),

            "chunk_summaries": summary_result.get(
                "chunk_summaries",
                [],
            ),

            "model_used": "Qwen3-VL-2B-Instruct",

            "status": "completed",

            "processing_time": round(
                processing_time,
                3,
            ),

            "warnings": warnings,
        }
