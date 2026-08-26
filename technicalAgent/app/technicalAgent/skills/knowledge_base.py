import boto3
from strands import tool

_bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

TECHNICAL_KB_ID = "KDMA6DWRRZ"


@tool
def search_technical_knowledge_base(query: str) -> str:
    """
    Search CloudNest's technical support knowledge base for information about
    the API, integrations, login issues, product functionality, and troubleshooting.
    Use this whenever a user asks a technical support question.

    Args:
        query: The user's technical question, or a focused search phrase.

    Returns:
        Relevant excerpts from CloudNest's technical documentation.
    """
    response = _bedrock_agent_runtime.retrieve(
        knowledgeBaseId=TECHNICAL_KB_ID,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {"numberOfResults": 3}
        },
    )

    chunks = response.get("retrievalResults", [])
    if not chunks:
        return "No relevant information found in the technical knowledge base."

    formatted = []
    for chunk in chunks:
        text = chunk.get("content", {}).get("text", "")
        score = chunk.get("score", 0)
        formatted.append(f"[relevance: {score:.2f}] {text}")

    return "\n\n".join(formatted)
