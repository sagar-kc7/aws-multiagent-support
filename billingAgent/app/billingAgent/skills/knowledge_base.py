import boto3
from strands import tool

_bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

BILLING_KB_ID = "T7LWJK5A5H"


@tool
def search_billing_knowledge_base(query: str) -> str:
    """
    Search CloudNest's billing knowledge base for information about
    subscriptions, payments, invoices, and billing cycles.
    Use this whenever a user asks a billing-related question.

    Args:
        query: The user's billing question, or a focused search phrase.

    Returns:
        Relevant excerpts from CloudNest's billing documentation.
    """
    response = _bedrock_agent_runtime.retrieve(
        knowledgeBaseId=BILLING_KB_ID,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {"numberOfResults": 3}
        },
    )

    chunks = response.get("retrievalResults", [])
    if not chunks:
        return "No relevant information found in the billing knowledge base."

    formatted = []
    for chunk in chunks:
        text = chunk.get("content", {}).get("text", "")
        score = chunk.get("score", 0)
        formatted.append(f"[relevance: {score:.2f}] {text}")

    return "\n\n".join(formatted)
