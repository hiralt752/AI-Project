
from app.services.document_service import process_document
from app.services.document_pipeline_service import DocumentPipelineService


FILE_PATH = r"C:/Users/itidol/Downloads/AIML_documentation.pdf"


def main():

    # -----------------------------------------
    # 1. Extract document
    # -----------------------------------------

    document = process_document(FILE_PATH)

    print("\n========== EXTRACTION ==========")
    print("File type:", document.get("file_type"))
    print("Page count:", document.get("page_count"))
    print("Text length:", len(document.get("text", "")))


    # -----------------------------------------
    # 2. Create pipeline
    # -----------------------------------------

    pipeline = DocumentPipelineService()


    # -----------------------------------------
    # 3. Process document
    # -----------------------------------------

    result = pipeline.process(
        document=document,
        summary_mode="Standard",
        extract_structured=True,
    )


    # -----------------------------------------
    # 4. Display result
    # -----------------------------------------

    print("\n========== SUMMARY RESULT DEBUG ==========")
    print("Summary:", result.get("summary"))
    print("Chunk summaries:", result.get("chunk_summaries"))
    print("Chunk summaries type:", type(result.get("chunk_summaries")))
    print("Chunk summaries count:", len(result.get("chunk_summaries", [])))

    print("\n========== SUMMARY ==========")
    print(result["summary"])


    print("\n========== SUMMARY MODE ==========")
    print(result["summary_mode"])


    print("\n========== CHUNK COUNT ==========")
    print(result["chunk_count"])


    print("\n========== SECTION COUNT ==========")
    print(result["section_count"])


    print("\n========== CHUNK SUMMARIES ==========")

    for index, summary in enumerate(
        result["chunk_summaries"],
        start=1,
    ):
        print(f"\n--- Chunk {index} ---")
        print(summary)


    print("\n========== STRUCTURED DATA ==========")

    structured = result["structured_data"]

    print("\nRAW:")
    print(structured)

    print("\nEntities:")
    print(structured.get("entities", []))

    print("\nDates:")
    print(structured.get("dates", []))

    print("\nNumbers:")
    print(structured.get("numbers", []))

    print("\nDecisions:")
    print(structured.get("decisions", []))

    print("\nAction Items:")
    print(structured.get("action_items", []))

    print("\nKey Points:")
    print(structured.get("key_points", []))

    print("\nSection Summaries:")
    print(structured.get("section_summaries", []))


    print("\n========== PROCESSING TIME ==========")
    print(result["processing_time"], "seconds")


if __name__ == "__main__":
    main()