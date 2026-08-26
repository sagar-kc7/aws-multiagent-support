import boto3
from strands import tool

_bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

REFUNDS_KB_ID = "O7YPBMATXH"


@tool
def search_refunds_knowledge_base(query: str) -> str:
    """
    Search CloudNest's refunds and cancellations knowledge base for information
    about refund eligibility, processing times, and cancellation policy.
    Use this whenever a user asks a refund or cancellation question.

    Args:
        query: The user's refund/cancellation question, or a focused search phrase.

    Returns:
        Relevant excerpts from CloudNest's refunds documentation.
    """
    response = _bedrock_agent_runtime.retrieve(
        knowledgeBaseId=REFUNDS_KB_ID,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {"numberOfResults": 3}
        },
    )

    chunks = response.get("retrievalResults", [])
    if not chunks:
        return "No relevant information found in the refunds knowledge base."

    formatted = []
    for chunk in chunks:
        text = chunk.get("content", {}).get("text", "")
        score = chunk.get("score", 0)
        formatted.append(f"[relevance: {score:.2f}] {text}")

    return "\n\n".join(formatted)
