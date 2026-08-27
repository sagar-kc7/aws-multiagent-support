import json
import uuid
import boto3
from strands import tool

_agentcore_client = boto3.client("bedrock-agentcore", region_name="us-east-1")

TECHNICAL_AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-1:027758599866:runtime/technicalAgent_technicalAgent-0lTzarHlcT"
BILLING_AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-1:027758599866:runtime/billingAgent_billingAgent-ac2mJN727m"
REFUNDS_AGENT_ARN = "arn:aws:bedrock-agentcore:us-east-1:027758599866:runtime/refundsAgent_refundsAgent-JDexaD63RI"


def _invoke_specialist(agent_arn: str, question: str) -> str:
    """Invoke a deployed AgentCore specialist agent and extract its final text answer."""
    response = _agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=str(uuid.uuid4()) + "-" * 8,  # AgentCore requires session IDs >= 33 chars
        payload=json.dumps({"prompt": question}).encode("utf-8"),
    )

    raw = response["response"].read()
    text_parts = []

    # The specialist streams Bedrock Converse-style events as newline-delimited JSON.
        # The specialist streams Server-Sent Events: each line is "data: {json}".
    for line in raw.decode("utf-8").splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        json_str = line[len("data:"):].strip()
        if not json_str:
            continue
        try:
            event = json.loads(json_str)
        except json.JSONDecodeError:
            continue
        delta = event.get("event", {}).get("contentBlockDelta", {}).get("delta", {})
        if "text" in delta:
            text_parts.append(delta["text"])

    answer = "".join(text_parts).strip()
    return answer if answer else "The specialist agent did not return a text answer."


@tool
def ask_billing_specialist(question: str) -> str:
    """
    Delegate a question to the billing specialist agent for anything about
    payments, subscriptions, invoices, or billing cycles.

    Args:
        question: The user's billing-related question, in their own words.

    Returns:
        The billing specialist's answer.
    """
    return _invoke_specialist(BILLING_AGENT_ARN, question)


@tool
def ask_technical_specialist(question: str) -> str:
    """
    Delegate a question to the technical specialist agent for anything about
    the API, integrations, login, or product functionality.

    Args:
        question: The user's technical support question, in their own words.

    Returns:
        The technical specialist's answer.
    """
    return _invoke_specialist(TECHNICAL_AGENT_ARN, question)


@tool
def ask_refunds_specialist(question: str) -> str:
    """
    Delegate a question to the refunds specialist agent for anything about
    refund eligibility, processing times, or cancellation policy.

    Args:
        question: The user's refunds/cancellation question, in their own words.

    Returns:
        The refunds specialist's answer.
    """
    return _invoke_specialist(REFUNDS_AGENT_ARN, question)
