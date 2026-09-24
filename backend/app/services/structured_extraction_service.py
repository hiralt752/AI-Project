"""Provide structured extraction service components for the application."""


import json
import re

from app.services.qwen_service import (
    generate_text,
)


class StructuredExtractionService:
    """
    Extract structured information from the complete
    processed document text.

    Extraction includes:
        - Entities
        - Decisions
        - Action Items
        - Key Points

    Dates and numbers are intentionally not returned.

    Missing information is represented by empty lists.
    """

    def __init__(
        self,
        model,
        processor,
    ):
        """
        Initialize the structured extraction service.

        Args:
            model: Loaded Qwen model used for structured extraction.
            processor: Qwen processor used to prepare model inputs.
        """
        self.model = model
        self.processor = processor

    # =========================================================
    # QWEN SEMANTIC EXTRACTION
    # =========================================================

    def extract_semantic_information(
        self,
        text: str,
    ) -> dict[str, list]:
        """
        Use Qwen to extract structured semantic information
        from the complete document text.

        The extraction includes entities, decisions, action items,
        and key points. Only information explicitly supported by
        the document is returned.

        Args:
            text: Complete cleaned document text.

        Returns:
            Dictionary containing entities, decisions, action items,
            and key points. Empty lists are returned when information
            is not available or extraction fails.
        """

        empty_result = {
            "entities": [],
            "decisions": [],
            "action_items": [],
            "key_points": [],
        }

        if not text or not text.strip():
            return empty_result

        prompt = f"""
You are a structured document information extraction system.

Analyze ONLY the document text provided below.

Return ONLY valid JSON using exactly this structure:

{{
    "entities": [],
    "decisions": [],
    "action_items": [],
    "key_points": []
}}

EXTRACTION RULES:

1. ENTITIES

Extract important entities explicitly present in the document.

Include meaningful:
- People
- Organizations
- Companies
- Locations
- Products
- Technologies
- Programming languages
- Frameworks
- Libraries
- Databases
- Tools
- Important projects

Rules for entities:
- Extract all relevant entities explicitly present in the source text.
- Do not omit relevant entities because of a count limit.
- Each unique entity must appear ONLY ONCE.
- Remove duplicate occurrences of the same entity.
- Do not repeat entities mentioned multiple times.
- Do not include generic words unless they are meaningful entities.
- Use only information explicitly present in the source text.

2. DECISIONS

Extract all decisions explicitly stated in the document.

Rules:
- Do not infer decisions.
- Do not create decisions from general statements.
- Include every explicitly stated decision.
- If the document contains no explicit decisions, return [].

3. ACTION ITEMS

Extract all explicitly mentioned:
- Tasks
- Actions
- Recommendations
- Responsibilities
- Follow-up activities

Rules:
- Do not invent tasks.
- Do not convert general information into an action item.
- Include every explicitly stated action item.
- If the document contains no explicit action items, return [].

4. KEY POINTS

Extract all important factual points from the document.

Rules:
- Use only information explicitly present in the source.
- Include all meaningful factual points.
- Do not omit important information because of a count limit.
- Keep each key point concise.
- Do not unnecessarily repeat the same information.

IMPORTANT OUTPUT RULES:

- Use ONLY information from the source text.
- Do not invent information.
- Do not infer missing information.
- Do not use outside knowledge.
- Do not use the filename.
- Do not extract separate dates.
- Do not extract separate numbers.
- Every field MUST contain a JSON array.
- If a category is not present, return [].
- Do not repeat any item within the same field.
- Return ONLY valid JSON.
- Do not return Markdown.
- Do not add explanations before or after the JSON.
- Make sure the JSON is completely closed before finishing.

DOCUMENT TEXT:

{text}
"""

        try:
            response = generate_text(
                self.model,
                self.processor,
                prompt,
                max_new_tokens=1536,
            )

            print("\n" + "=" * 80)
            print("RAW STRUCTURED QWEN RESPONSE")
            print("=" * 80)
            print(response)
            print("=" * 80)

        except Exception as exc:
            print(
                "Structured Qwen extraction failed: "
                f"{exc}"
            )

            return empty_result

        return self._parse_qwen_json(
            response
        )

    # =========================================================
    # JSON PARSER
    # =========================================================

    def _parse_qwen_json(
        self,
        response: str,
    ) -> dict[str, list]:
        """
        Safely parse the JSON response generated by Qwen.

        Markdown code fences are removed before parsing. If the
        complete response is not valid JSON, the method attempts
        to extract a JSON object from the response. If the JSON
        is truncated, completed array values are recovered.

        Args:
            response: Raw text returned by Qwen.

        Returns:
            Dictionary containing normalized extraction fields.
            Empty lists are returned when the response cannot
            be parsed or recovered.
        """

        empty_result = {
            "entities": [],
            "decisions": [],
            "action_items": [],
            "key_points": [],
        }

        if not response:
            return empty_result

        response = response.strip()

        # -----------------------------------------------------
        # Remove markdown code fences
        # -----------------------------------------------------

        response = re.sub(
            r"^```json\s*",
            "",
            response,
            flags=re.IGNORECASE,
        )

        response = re.sub(
            r"^```\s*",
            "",
            response,
        )

        response = re.sub(
            r"\s*```$",
            "",
            response,
        )

        response = response.strip()

        # -----------------------------------------------------
        # Try normal JSON parsing
        # -----------------------------------------------------

        try:
            data = json.loads(
                response
            )

        except json.JSONDecodeError:

            # -------------------------------------------------
            # Try extracting JSON object
            # -------------------------------------------------

            start = response.find("{")
            end = response.rfind("}")

            if start != -1 and end > start:

                json_text = response[
                    start:end + 1
                ]

                try:
                    data = json.loads(
                        json_text
                    )

                except json.JSONDecodeError:
                    data = None

            else:
                data = None

            # -------------------------------------------------
            # Recover completed values from truncated JSON
            # -------------------------------------------------

            if data is None:

                print(
                    "[STRUCTURED EXTRACTION] "
                    "Incomplete JSON detected. "
                    "Attempting recovery..."
                )

                recovered = (
                    self._recover_truncated_json(
                        response
                    )
                )

                if recovered:
                    print(
                        "[STRUCTURED EXTRACTION] "
                        "Recovered structured data "
                        "from incomplete JSON."
                    )

                    return self._normalize_recovered_result(
                        recovered
                    )

                print(
                    "[STRUCTURED EXTRACTION] "
                    "Unable to recover structured data."
                )

                return empty_result

        # -----------------------------------------------------
        # Ensure dictionary
        # -----------------------------------------------------

        if not isinstance(
            data,
            dict,
        ):
            return empty_result

        # -----------------------------------------------------
        # Normalize fields
        # -----------------------------------------------------

        entities = self._ensure_list(
            data.get("entities")
        )

        decisions = self._ensure_list(
            data.get("decisions")
        )

        action_items = self._ensure_list(
            data.get("action_items")
        )

        key_points = self._ensure_list(
            data.get("key_points")
        )

        return {
            "entities": self._clean_list(
                entities
            ),
            "decisions": self._clean_list(
                decisions
            ),
            "action_items": self._clean_list(
                action_items
            ),
            "key_points": self._clean_list(
                key_points
            ),
        }

    # =========================================================
    # TRUNCATED JSON RECOVERY
    # =========================================================

    def _recover_truncated_json(
        self,
        response: str,
    ) -> dict[str, list]:
        """
        Recover completed string values from truncated JSON.

        If Qwen stops generating before the JSON is completely
        closed, already completed array values are recovered.
        """

        recovered = {}

        fields = [
            "entities",
            "decisions",
            "action_items",
            "key_points",
        ]

        for field in fields:

            values = (
                self._extract_completed_array_values(
                    response,
                    field,
                )
            )

            if values:
                recovered[field] = values

        return recovered

    # =========================================================
    # ARRAY VALUE RECOVERY
    # =========================================================

    @staticmethod
    def _extract_completed_array_values(
        response: str,
        field: str,
    ) -> list:
        """
        Extract completed JSON string values from one array.

        Only properly closed string values are returned.
        """

        pattern = (
            rf'"{re.escape(field)}"\s*:\s*\['
        )

        match = re.search(
            pattern,
            response,
            flags=re.IGNORECASE,
        )

        if not match:
            return []

        array_text = response[
            match.end():
        ]

        values = []

        # -----------------------------------------------------
        # Find complete JSON strings only.
        # -----------------------------------------------------

        string_pattern = re.compile(
            r'"((?:\\.|[^"\\])*)"'
        )

        for string_match in string_pattern.finditer(
            array_text
        ):

            value = string_match.group(1)

            try:
                value = json.loads(
                    '"' + value + '"'
                )

            except json.JSONDecodeError:
                continue

            value = value.strip()

            if not value:
                continue

            if value not in values:
                values.append(
                    value
                )

        return values

    # =========================================================
    # NORMALIZE RECOVERED RESULT
    # =========================================================

    def _normalize_recovered_result(
        self,
        data: dict[str, list],
    ) -> dict[str, list]:
        """
        Normalize recovered values from truncated JSON.
        """

        return {
            "entities": self._clean_list(
                data.get(
                    "entities",
                    [],
                )
            ),
            "decisions": self._clean_list(
                data.get(
                    "decisions",
                    [],
                )
            ),
            "action_items": self._clean_list(
                data.get(
                    "action_items",
                    [],
                )
            ),
            "key_points": self._clean_list(
                data.get(
                    "key_points",
                    [],
                )
            ),
        }

    # =========================================================
    # COMPLETE EXTRACTION
    # =========================================================

    def extract(
        self,
        text: str,
        include_semantic: bool = True,
    ) -> dict[str, list]:
        """
        Perform structured extraction from the complete
        cleaned document text.

        Section detection is not required because the complete
        document text is used as the source for extraction.

        Args:
            text: Complete cleaned document text.
            include_semantic: Whether semantic extraction should
                be performed.

        Returns:
            Dictionary containing entities, decisions, action items,
            and key points.
        """

        text = text or ""

        semantic = {
            "entities": [],
            "decisions": [],
            "action_items": [],
            "key_points": [],
        }

        if (
            include_semantic
            and text.strip()
        ):
            semantic = (
                self.extract_semantic_information(
                    text
                )
            )

        return {
            "entities": semantic.get(
                "entities",
                [],
            ),
            "decisions": semantic.get(
                "decisions",
                [],
            ),
            "action_items": semantic.get(
                "action_items",
                [],
            ),
            "key_points": semantic.get(
                "key_points",
                [],
            ),
        }

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _ensure_list(
        value,
    ) -> list:
        """
        Convert a value into a list.

        Args:
            value: Value that should be normalized to a list.

        Returns:
            The original list if the value is already a list,
            a single-item list for other non-null values, or an
            empty list for None.
        """

        if value is None:
            return []

        if isinstance(
            value,
            list,
        ):
            return value

        return [value]

    @staticmethod
    def _clean_list(
        values: list,
    ) -> list:
        """
        Remove empty values and duplicate items from a list.

        Values that are not strings are converted to strings before
        whitespace normalization.

        Args:
            values: List of extracted values.

        Returns:
            Cleaned list containing unique non-empty string values.
        """

        cleaned = []

        for value in values:

            if value is None:
                continue

            if not isinstance(
                value,
                str,
            ):
                value = str(
                    value
                )

            value = value.strip()

            if not value:
                continue

            if value not in cleaned:
                cleaned.append(
                    value
                )

        return cleaned