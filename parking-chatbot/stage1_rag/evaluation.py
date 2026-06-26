import time
from typing import List, Dict
from stage1_rag.vector_store import get_or_build_vector_store
from stage1_rag.rag_chain import create_rag_chain

# ---------------------------------------------------------------------------
# Ground-truth test set
# ---------------------------------------------------------------------------
TEST_QUESTIONS = [
    {
        "question": "What are the working hours on Saturday?",
        "expected_keywords": ["saturday", "07:00", "22:00"],
    },
    {
        "question": "How much does it cost to park for one day?",
        "expected_keywords": ["20", "daily", "day"],
    },
    {
        "question": "Where is the parking facility located?",
        "expected_keywords": ["main street", "city center", "central station"],
    },
    {
        "question": "What is the maximum vehicle height allowed?",
        "expected_keywords": ["2.1", "meter"],
    },
    {
        "question": "How do I make a reservation?",
        "expected_keywords": ["name", "car", "date", "administrator"],
    },
    {
        "question": "Is there parking available for electric vehicles?",
        "expected_keywords": ["electric", "charging", "floor"],
    },
    {
        "question": "What is the monthly subscription price?",
        "expected_keywords": ["250", "monthly"],
    },
]


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def precision_at_k(retrieved_docs: list, relevant_keywords: List[str], k: int = 3) -> float:
    """
    Precision@K: fraction of top-K retrieved docs that contain at least one
    relevant keyword.
    """
    top_k = retrieved_docs[:k]
    if not top_k:
        return 0.0
    relevant_count = sum(
        1
        for doc in top_k
        if any(kw.lower() in doc.page_content.lower() for kw in relevant_keywords)
    )
    return relevant_count / k


def recall_at_k(retrieved_docs: list, relevant_keywords: List[str], k: int = 3) -> float:
    """
    Recall@K: fraction of relevant keywords found in the combined text of top-K docs.
    """
    top_k = retrieved_docs[:k]
    combined = " ".join(doc.page_content.lower() for doc in top_k)
    found = sum(1 for kw in relevant_keywords if kw.lower() in combined)
    return found / len(relevant_keywords) if relevant_keywords else 0.0


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_evaluation() -> Dict:
    """Run the full evaluation suite and print a report."""
    print("Loading vector store...")
    vector_store = get_or_build_vector_store()
    chain = create_rag_chain(vector_store)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    results = []
    total_latency = 0.0

    print("\n" + "=" * 60)
    print("RAG Evaluation Report")
    print("=" * 60)

    for test in TEST_QUESTIONS:
        question = test["question"]
        expected = test["expected_keywords"]

        start = time.time()
        response = chain.invoke(question)
        latency = time.time() - start
        total_latency += latency

        docs = retriever.invoke(question)
        p_k = precision_at_k(docs, expected)
        r_k = recall_at_k(docs, expected)

        result = {
            "question": question,
            "response": response,
            "latency_s": round(latency, 2),
            "precision_at_3": round(p_k, 2),
            "recall_at_3": round(r_k, 2),
        }
        results.append(result)

        print(f"Q: {question}")
        print(f"A: {response[:180]}...")
        print(f"   Latency: {latency:.2f}s  |  P@3: {p_k:.2f}  |  R@3: {r_k:.2f}")
        print()

    n = len(TEST_QUESTIONS)
    avg_latency = total_latency / n
    avg_precision = sum(r["precision_at_3"] for r in results) / n
    avg_recall = sum(r["recall_at_3"] for r in results) / n

    print("=" * 60)
    print(f"Summary over {n} questions:")
    print(f"  Avg Latency  : {avg_latency:.2f}s")
    print(f"  Avg P@3      : {avg_precision:.2f}")
    print(f"  Avg R@3      : {avg_recall:.2f}")
    print("=" * 60)

    return {
        "results": results,
        "summary": {
            "avg_latency_s": avg_latency,
            "avg_precision_at_3": avg_precision,
            "avg_recall_at_3": avg_recall,
        },
    }


if __name__ == "__main__":
    run_evaluation()
