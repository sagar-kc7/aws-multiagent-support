cat > ~/aws-multiagent-support/README.md << 'READMEEOF'
# CloudNest Multi-Agent Support System

A production-style multi-agent customer support platform built on AWS, using a supervisor agent that routes user questions to specialized sub-agents, each grounded in its own knowledge base via retrieval-augmented generation (RAG).

Built as a hands-on portfolio project to apply AWS's core generative AI services after completing the AWS Certified AI Practitioner course.

## Architecture

User Query -> Supervisor Agent (AgentCore Runtime, Strands, Claude Haiku 4.5)
Supervisor routes via tool-calling to three specialists:
Technical Agent, Billing Agent, Refunds Agent (each an AgentCore Runtime, Strands)
Each specialist queries its own Bedrock Knowledge Base (Technical KB, Billing KB, Refunds KB)
Each Knowledge Base is backed by Pinecone (vector store), fed from S3 (source documents)

## Tech Stack

- Agent framework: Strands Agents SDK (AWS-native)
- Agent runtime: Amazon Bedrock AgentCore Runtime
- LLM: Claude Haiku 4.5 via Amazon Bedrock
- Retrieval: Amazon Bedrock Knowledge Bases
- Vector store: Pinecone (serverless, free tier)
- Embeddings: Amazon Titan Embed Text v2 (1024-dim)
- Document storage: Amazon S3
- Infrastructure as Code: AWS CDK (Python) for core infra; AgentCore CLI-managed CDK for agent deployment
- Secrets: AWS Secrets Manager

## Why this architecture

- Domain-scoped retrieval: separating billing, technical, and refunds into distinct Knowledge Bases keeps each specialist's context clean and reduces irrelevant retrieval.
- Supervisor pattern over a single mega-agent: each specialist stays focused and independently testable; adding a fourth domain later means adding one more agent, not restructuring a monolithic prompt.
- Multi-domain handling: a single user message spanning two domains (e.g. "my API key broke and I want a refund") is routed to multiple specialists and synthesized into one response, demonstrated in testing.
- Cost-conscious choices: Pinecone's free tier replaces Amazon OpenSearch Serverless (which has a high always-on cost floor) as the Knowledge Base vector store, keeping the whole project inside a $120 AWS credit budget.

## Project Structure

aws-multiagent-support/
  aws_multiagent_support/    CDK: S3 buckets + Bedrock Knowledge Bases
  kb-docs/                   Source documents per domain (billing, technical, refunds)
  technicalAgent/            Strands agent + AgentCore deployment config
  billingAgent/              Strands agent + AgentCore deployment config
  refundsAgent/              Strands agent + AgentCore deployment config
  supervisorAgent/           Strands agent that routes to the three specialists

Each *Agent/ directory follows the same shape:

  app/<name>Agent/
    main.py           Agent entrypoint, tool registration, system prompt
    model/load.py     Bedrock model configuration
    skills/           Custom tools (KB retrieval or specialist invocation)
  agentcore/           AgentCore CLI-managed deployment config

## Setup

### Prerequisites

- AWS account with Bedrock model access enabled (Claude Haiku 4.5, Titan Embeddings)
- AWS CLI configured with an IAM user (not root)
- Node.js 20+, Python 3.10+, AWS CDK, AgentCore CLI (npm install -g @aws/agentcore)
- A free Pinecone account

### 1. Deploy core infrastructure (S3 + Knowledge Bases)

    python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    cdk bootstrap
    cdk deploy

### 2. Populate the Knowledge Bases

    aws bedrock-agent start-ingestion-job --knowledge-base-id KB_ID --data-source-id DATA_SOURCE_ID

(repeat for each of the three Knowledge Bases)

### 3. Deploy the specialist agents

    cd technicalAgent && agentcore deploy
    cd ../billingAgent && agentcore deploy
    cd ../refundsAgent && agentcore deploy

Each specialist agent's execution role needs bedrock:Retrieve scoped to its own Knowledge Base ARN, granted via an inline IAM policy after deployment.

### 4. Deploy the supervisor

    cd ../supervisorAgent && agentcore deploy

The supervisor's execution role needs bedrock-agentcore:InvokeAgentRuntime scoped to all three specialist Runtime ARNs and their /runtime-endpoint/* sub-resources.

### 5. Test

    agentcore invoke "My API key stopped working and I also want to know if I can get a refund since I only used the product for 5 days"

## Notable engineering challenges

- Bedrock Agents Classic is closed to new accounts (as of July 2026): pivoted the entire agent layer from CDK-declared Bedrock Agents to Amazon Bedrock AgentCore + Strands Agents SDK mid-build.
- IAM action namespace mismatches: the API service is bedrock-agent-runtime, but the IAM action for Knowledge Base retrieval is bedrock:Retrieve, not bedrock-agent-runtime:Retrieve. Diagnosed by reading raw CloudWatch logs for the exact AccessDeniedException message rather than assuming.
- ARN sub-resource scoping: IAM permission checks for InvokeAgentRuntime are evaluated against the /runtime-endpoint/DEFAULT sub-resource, not the bare Runtime ARN, so both forms were required in the policy.
- SSE response parsing: AgentCore Runtime responses stream as Server-Sent Events (data: {json} per line), not plain newline-delimited JSON, which required adjusting the supervisor's response-parsing logic after inspecting raw output via curl.

## Cost

Built entirely within a $120 AWS free-tier credit (45-day window):

- Bedrock model and embedding calls: pay-per-token, negligible at dev-scale usage
- AgentCore Runtime: pay-per-invocation
- S3, Secrets Manager: pennies
- Pinecone: free tier (avoided Amazon OpenSearch Serverless's high always-on cost floor)

## Author

Sagar K.C. - github.com/sagar-kc7
READMEEOF