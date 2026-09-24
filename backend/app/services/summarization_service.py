"""Provide summarization service components for the application."""

from __future__ import annotations

from typing import Any

from app.services.qwen_service import generate_text


# ============================================================
# SUMMARY PROMPTS
# ============================================================

SUMMARY_PROMPTS = {

    "Brief": """
Summarize the provided document content briefly.

Rules:
- Include only the most important information.
- Preserve the main meaning.
- Do not invent information.
- Do not use outside knowledge.
- Remove unnecessary repetition.
- Return a concise paragraph.
""",

    "Standard": """
Summarize the provided document content clearly and accurately.

Rules:
- Cover the important ideas and topics.
- Preserve the meaning of the source.
- Remove unnecessary repetition.
- Do not invent information.
- Do not add information from outside the source.
- Return a clear and coherent paragraph.
""",

    "Detailed": """
Create a detailed summary of the provided document content.

Rules:
- Cover all important concepts and information.
- Preserve important relationships between topics.
- Do not omit important information.
- Do not invent information.
- Do not use outside knowledge.
- Avoid unnecessary repetition.
- Return a detailed but coherent summary.
""",

    "Key Points": """
Extract the most important points from the provided document content.

Rules:
- Include only information supported by the source.
- Do not invent information.
- Do not add outside knowledge.
- Remove repetition.
- Return concise key points.
""",

    "Action Items": """
Identify actionable tasks or actions explicitly mentioned
in the provided document content.

Rules:
- Include only actions supported by the source.
- Do not invent tasks.
- Do not infer actions that are not stated.
- If there are no action items, return an empty result.
""",
}


VALID_SUMMARY_MODES = set(
    SUMMARY_PROMPTS.keys()
)


class SummarizationService:
    """
    Document summarization service.

    Pipeline:

        Complete Document Text
                ↓
            Chunks
                ↓
        Summarize Every Chunk
                ↓
        Hierarchical Synthesis
                ↓
        Final Document Summary

    Important:
    - No section detection is required.
    - No arbitrary document word limit.
    - No document text is silently discarded.
    - Every non-empty chunk is summarized.
    - Large documents are processed hierarchically.
    """

    def __init__(
        self,
        model,
        processor,
        chunk_size: int = 1200,
        overlap: int = 150,
        synthesis_group_size: int = 8,
    ):

        """Initialize the instance."""

        self.model = model
        self.processor = processor

        self.chunk_size = chunk_size
        self.overlap = overlap
        self.synthesis_group_size = (
            synthesis_group_size
        )

    # ============================================================
    # MAIN DOCUMENT SUMMARIZATION
    # ============================================================

    def summarize_document(
        self,
        chunks: list[dict[str, Any]],
        mode: str = "Standard",
    ) -> dict[str, Any]:
        """
        Summarize the complete document.

        Every supplied chunk is processed.

        There is NO global document word limit.
        """

        if mode not in VALID_SUMMARY_MODES:
            raise ValueError(
                f"Unsupported summary mode: {mode}. "
                f"Supported modes: "
                f"{sorted(VALID_SUMMARY_MODES)}"
            )

        if not chunks:
            raise ValueError(
                "No document chunks available "
                "for summarization."
            )

        print(
            "[SUMMARIZATION] Starting document "
            f"summarization with {len(chunks)} chunks..."
        )

        # --------------------------------------------------------
        # STEP 1 — SUMMARIZE EVERY CHUNK
        # --------------------------------------------------------

        chunk_summaries: list[
            dict[str, Any]
        ] = []

        for position, chunk in enumerate(
            chunks,
            start=1,
        ):

            chunk_text = str(
                chunk.get(
                    "text",
                    "",
                )
            ).strip()

            if not chunk_text:

                print(
                    "[SUMMARIZATION] Skipping empty "
                    f"chunk {position}."
                )

                continue

            print(
                "[SUMMARIZATION] Processing chunk "
                f"{position}/{len(chunks)}..."
            )

            summary = self.summarize_chunk(
                chunk=chunk,
                mode=mode,
            )

            chunk_summaries.append(
                {
                    "chunk_id": chunk.get(
                        "chunk_id"
                    ),

                    "chunk_index": chunk.get(
                        "chunk_index",
                        position - 1,
                    ),

                    "word_count": chunk.get(
                        "word_count",
                        len(
                            chunk_text.split()
                        ),
                    ),

                    "summary": summary,
                }
            )

        if not chunk_summaries:
            raise ValueError(
                "No chunk summaries were generated."
            )

        # --------------------------------------------------------
        # STEP 2 — COLLECT CHUNK SUMMARIES
        # --------------------------------------------------------

        summary_texts = [
            str(
                item.get(
                    "summary",
                    "",
                )
            ).strip()

            for item in chunk_summaries

            if item.get("summary")
            and str(
                item.get(
                    "summary",
                    "",
                )
            ).strip()
        ]

        if not summary_texts:
            raise ValueError(
                "Chunk summarization produced "
                "no usable summaries."
            )

        # --------------------------------------------------------
        # STEP 3 — FINAL SYNTHESIS
        # --------------------------------------------------------

        if len(summary_texts) == 1:

            # No additional Qwen call is required
            # when the document contains one chunk.

            final_summary = summary_texts[0]

        else:

            print(
                "[SUMMARIZATION] Starting "
                "hierarchical synthesis..."
            )

            final_summary = (
                self.hierarchical_summarize(
                    summaries=summary_texts,
                    mode=mode,
                    group_size=(
                        self.synthesis_group_size
                    ),
                )
            )

        print(
            "[SUMMARIZATION] Document "
            "summarization completed."
        )

        # --------------------------------------------------------
        # STEP 4 — RETURN RESULT
        # --------------------------------------------------------

        return {
            "summary": final_summary,

            "summary_mode": mode,

            "chunk_summaries": (
                chunk_summaries
            ),

            "chunk_count": len(
                chunk_summaries
            ),
        }

    # ============================================================
    # CHUNK SUMMARIZATION
    # ============================================================

    def summarize_chunk(
        self,
        chunk: dict[str, Any],
        mode: str = "Standard",
    ) -> str:
        """
        Summarize one complete chunk using Qwen.
        """

        if mode not in VALID_SUMMARY_MODES:
            raise ValueError(
                f"Unsupported summary mode: {mode}"
            )

        text = str(
            chunk.get(
                "text",
                "",
            )
        ).strip()

        if not text:
            return ""

        prompt = self._build_chunk_prompt(
            text=text,
            mode=mode,
        )

        try:

            summary = generate_text(
                model=self.model,
                processor=self.processor,
                prompt=prompt,
                max_new_tokens=(
                    self._get_chunk_max_tokens(
                        mode
                    )
                ),
            )

        except Exception as exc:

            raise RuntimeError(
                "Failed to summarize chunk "
                f"{chunk.get('chunk_id')}: {exc}"
            ) from exc

        summary = str(
            summary
        ).strip()

        if not summary:
            raise RuntimeError(
                "Qwen returned an empty summary "
                f"for chunk {chunk.get('chunk_id')}."
            )

        return summary

    # ============================================================
    # CHUNK PROMPT
    # ============================================================

    def _build_chunk_prompt(
        self,
        text: str,
        mode: str,
    ) -> str:
        """
        Build prompt for an individual document chunk.
        """

        instruction = SUMMARY_PROMPTS[
            mode
        ]

        return f"""
You are summarizing one part of a complete document.

SUMMARY REQUIREMENT:
{instruction}

IMPORTANT SOURCE-GROUNDING RULES:

- The DOCUMENT CHUNK below is the only source of truth.
- Use ONLY information explicitly present in the chunk.
- Do not use information from the filename.
- Do not use outside knowledge.
- Do not guess missing information.
- Do not fabricate facts.
- Do not invent organizations, companies, products,
  systems, applications, projects, or use cases.
- Do not convert a list of topics into a fictional story.
- If the chunk contains only headings or topic names,
  summarize only those topics.
- Preserve important technical terminology.
- Do not add information that is not present in the source.
- Do not create separate date or number extraction fields.

SUMMARY MODE:
{mode}

DOCUMENT CHUNK:
{text}

OUTPUT:
Return only the summary.
""".strip()

    # ============================================================
    # HIERARCHICAL SUMMARIZATION
    # ============================================================

    def hierarchical_summarize(
        self,
        summaries: list[str],
        mode: str = "Standard",
        group_size: int = 8,
    ) -> str:
        """
        Combine chunk summaries hierarchically.

        Example:

            Chunk summaries
                  ↓
            Groups of summaries
                  ↓
            Group summaries
                  ↓
            Final summary
        """

        if not summaries:
            return ""

        if len(summaries) == 1:
            return summaries[0]

        if group_size < 2:
            raise ValueError(
                "group_size must be at least 2."
            )

        current_level = [
            str(summary).strip()
            for summary in summaries
            if str(summary).strip()
        ]

        level = 1

        while len(current_level) > 1:

            print(
                "[SUMMARIZATION] Synthesis level "
                f"{level}: "
                f"{len(current_level)} summaries..."
            )

            next_level: list[str] = []

            for start in range(
                0,
                len(current_level),
                group_size,
            ):

                group = current_level[
                    start:start + group_size
                ]

                if len(group) == 1:

                    next_level.append(
                        group[0]
                    )

                    continue

                group_summary = self.synthesize(
                    summaries=group,
                    mode=mode,
                )

                next_level.append(
                    group_summary
                )

            current_level = next_level

            level += 1

        return current_level[0]

    # ============================================================
    # SYNTHESIS
    # ============================================================

    def synthesize(
        self,
        summaries: list[str],
        mode: str = "Standard",
    ) -> str:
        """
        Combine multiple chunk summaries into
        one summary.
        """

        if not summaries:
            return ""

        valid_summaries = [
            str(summary).strip()
            for summary in summaries
            if str(summary).strip()
        ]

        if not valid_summaries:
            return ""

        combined = "\n\n".join(
            f"Summary {index}:\n{summary}"

            for index, summary in enumerate(
                valid_summaries,
                start=1,
            )
        )

        prompt = (
            self._build_synthesis_prompt(
                combined=combined,
                mode=mode,
            )
        )

        try:

            result = generate_text(
                model=self.model,
                processor=self.processor,
                prompt=prompt,
                max_new_tokens=(
                    self._get_synthesis_max_tokens(
                        mode
                    )
                ),
            )

        except Exception as exc:

            raise RuntimeError(
                "Failed during hierarchical "
                f"synthesis: {exc}"
            ) from exc

        result = str(
            result
        ).strip()

        if not result:
            raise RuntimeError(
                "Qwen returned an empty result "
                "during synthesis."
            )

        return result

    # ============================================================
    # SYNTHESIS PROMPT
    # ============================================================

    def _build_synthesis_prompt(
        self,
        combined: str,
        mode: str,
    ) -> str:

        """Build synthesis prompt."""

        if mode == "Brief":

            instruction = """
Create one concise final summary.
Keep only the most important information.
"""

        elif mode == "Standard":

            instruction = """
Create one complete and balanced final summary.
Cover the major information represented across
all provided summaries.
"""

        elif mode == "Detailed":

            instruction = """
Create a detailed final summary.
Preserve all major concepts represented across
the provided summaries.
Do not unnecessarily repeat information.
"""

        elif mode == "Key Points":

            instruction = """
Combine the important information into concise
key points.
Do not invent additional points.
"""

        elif mode == "Action Items":

            instruction = """
Combine only the actionable items represented
in the provided summaries.

Do not invent actions.

If no actionable items are present,
return an empty result.
"""

        else:

            instruction = """
Create an accurate final summary from the
provided summaries.
"""

        return f"""
You are creating the final summary of a complete document.

TASK:
{instruction}

IMPORTANT RULES:
- Use ONLY information contained in the provided summaries.
- Do not introduce outside knowledge.
- Do not invent facts.
- Do not introduce information that is not represented
  in the provided summaries.
- Merge overlapping information intelligently.
- Remove unnecessary repetition.
- Preserve important technical terminology.
- The final summary must represent the complete
  available document.
- Do not create separate date or number extraction fields.

SUMMARY MODE:
{mode}

PROVIDED SUMMARIES:
{combined}

OUTPUT:
Return only the final summary.
""".strip()

    # ============================================================
    # TOKEN SETTINGS
    # ============================================================

    @staticmethod
    def _get_chunk_max_tokens(
        mode: str,
    ) -> int:

        """Get chunk max tokens."""

        if mode == "Brief":
            return 220

        if mode == "Standard":
            return 400

        if mode == "Detailed":
            return 600

        if mode == "Key Points":
            return 400

        if mode == "Action Items":
            return 300

        return 220

    @staticmethod
    def _get_synthesis_max_tokens(
        mode: str,
    ) -> int:

        """Get synthesis max tokens."""

        if mode == "Brief":
            return 280

        if mode == "Standard":
            return 500

        if mode == "Detailed":
            return 750

        if mode == "Key Points":
            return 500

        if mode == "Action Items":
            return 400

        return 260
