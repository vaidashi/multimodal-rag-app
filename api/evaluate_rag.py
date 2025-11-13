import os
import asyncio
from dotenv import load_dotenv
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from index import vector_search_rag

load_dotenv()


def create_evaluation_dataset() -> pd.DataFrame:
    """Creates a synthetic dataset for RAG evaluation."""
    data = {
        "question": [
            "What is Project Alpha's main goal?",
            "Who is the client for the project discussed?",
            "What technologies does Project Alpha use?",
            "Who is the project manager?",
        ],
        "ground_truth": [
            "Project Alpha's main goal is to develop a new customer relationship management (CRM) platform.",
            "The client for Project Alpha is Globex Corporation.",
            "The project uses Python for the backend and React for the frontend.",
            "The project is managed by Sarah.",
        ],
    }
    return pd.DataFrame(data)


def create_test_document() -> str:
    """Creates a sample document to be ingested for the test."""
    return """
    Project Alpha: A technical overview.
    The primary objective of Project Alpha is to develop a new customer relationship management (CRM) platform.
    This platform will be built using modern technologies. The backend will be implemented in Python,
    while the frontend will utilize the React library. The project is managed by Sarah, a senior engineer.
    The main stakeholder and client for this project is Globex Corporation, who have provided detailed requirements.
    """


async def run_rag_pipeline(df: pd.DataFrame, filename: str) -> list:
    """Runs the RAG pipeline for each question in the DataFrame."""
    results = []

    for _, row in df.iterrows():
        question = row["question"]
        print(f"\nRunning pipeline for question: '{question}'")

        # Invoke RAG tool function directly
        rag_result = vector_search_rag.invoke({"query": question, "filename": filename})

        print(f"  - Answer: {rag_result['answer'][:100]}...")
        print(f"  - Number of sources retrieved: {len(rag_result['sources'])}")
        if rag_result["sources"]:
            print(
                f"  - First source preview: {rag_result['sources'][0]['text'][:100]}..."
            )

        results.append(
            {
                "user_input": question,  # Changed from "question" to match RAGAS expectation
                "response": rag_result[
                    "answer"
                ],  # Changed from "answer" to match RAGAS expectation
                "retrieved_contexts": [
                    source["text"] for source in rag_result["sources"]
                ],  # Changed from "contexts"
                "reference": row[
                    "ground_truth"
                ],  # Changed from "ground_truth" to match RAGAS expectation
            }
        )
    return results


async def main():
    """Main function to run the evaluation."""
    # 1. Create a test document and simulate its ingestion
    # In a real scenario, you would have already ingested this document.
    # For this script, we assume a document named 'evaluation_doc.txt' exists in Pinecone.
    # You MUST run the ingest endpoint with this content before running the evaluation.
    test_doc_content = create_test_document()
    test_doc_filename = "evaluation_doc.txt"
    print("--- RAG Evaluation Pipeline ---")
    print(
        f"Please ensure you have ingested a document named '{test_doc_filename}' with the following content:"
    )
    print("---------------------------------")
    print(test_doc_content)
    print("---------------------------------")
    input("Press Enter to continue once the document is ingested...")

    # 2. Create the evaluation dataset
    eval_df = create_evaluation_dataset()

    # 3. Run the RAG pipeline on the dataset
    rag_results = await run_rag_pipeline(eval_df, test_doc_filename)

    # 4. Convert results to a Hugging Face Dataset object
    rag_dataset = Dataset.from_pandas(pd.DataFrame(rag_results))

    # 5. Define metrics and run evaluation
    # Create OpenAI LLM for RAGAS evaluation
    evaluator_llm = ChatOpenAI(model="gpt-4o", temperature=0)
    evaluator_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    metrics = [
        faithfulness,  # How factually consistent is the answer with the context?
        answer_relevancy,  # How relevant is the answer to the question?
        context_precision,  # Are the retrieved contexts relevant?
        context_recall,  # Did we retrieve all the necessary contexts?
    ]

    print("Running Ragas evaluation...")
    result = evaluate(
        dataset=rag_dataset,
        metrics=metrics,
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
    )

    print("Evaluation Complete!")
    print(result)

    # Convert to DataFrame for better display
    result_df = result.to_pandas()
    print(result_df)


if __name__ == "__main__":
    asyncio.run(main())
