from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
)
from constructs import Construct
from cdklabs.generative_ai_cdk_constructs import bedrock
from cdklabs.generative_ai_cdk_constructs.pinecone import PineconeVectorStore


class AwsMultiagentSupportStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Phase 2: S3 buckets holding source docs per domain ---
        self.billing_bucket = self._create_kb_bucket("BillingDocsBucket", "billing")
        self.technical_bucket = self._create_kb_bucket("TechnicalDocsBucket", "technical")
        self.refunds_bucket = self._create_kb_bucket("RefundsDocsBucket", "refunds")

        # --- Phase 3: Bedrock Knowledge Bases, each backed by its own Pinecone index ---
        self.billing_kb = self._create_knowledge_base(
            "BillingKB",
            bucket=self.billing_bucket,
            pinecone_url="https://billing-kb-uf8q7hz.svc.aped-4627-b74a.pinecone.io",
            instruction="Use this knowledge base to answer questions about CloudNest billing, subscriptions, payments, and invoicing.",
        )
        self.technical_kb = self._create_knowledge_base(
            "TechnicalKB",
            bucket=self.technical_bucket,
            pinecone_url="https://technical-kb-uf8q7hz.svc.aped-4627-b74a.pinecone.io",
            instruction="Use this knowledge base to answer technical support questions about CloudNest's product, API, and integrations.",
        )
        self.refunds_kb = self._create_knowledge_base(
            "RefundsKB",
            bucket=self.refunds_bucket,
            pinecone_url="https://refunds-kb-uf8q7hz.svc.aped-4627-b74a.pinecone.io",
            instruction="Use this knowledge base to answer questions about CloudNest refunds and cancellations.",
        )

    def _create_kb_bucket(self, construct_id: str, domain: str) -> s3.Bucket:
        bucket = s3.Bucket(
            self,
            construct_id,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
        s3_deployment.BucketDeployment(
            self,
            f"{construct_id}Deployment",
            sources=[s3_deployment.Source.asset(f"./kb-docs/{domain}")],
            destination_bucket=bucket,
        )
        return bucket

    def _create_knowledge_base(
        self, construct_id: str, bucket: s3.Bucket, pinecone_url: str, instruction: str
    ) -> bedrock.VectorKnowledgeBase:
        vector_store = PineconeVectorStore(
            connection_string=pinecone_url,
            credentials_secret_arn="arn:aws:secretsmanager:us-east-1:027758599866:secret:pinecone-api-key-L7sIJn",
            text_field="text",
            metadata_field="metadata",
        )

        kb = bedrock.VectorKnowledgeBase(
            self,
            construct_id,
            embeddings_model=bedrock.BedrockFoundationModel.TITAN_EMBED_TEXT_V2_1024,
            vector_store=vector_store,
            instruction=instruction,
        )

        kb.add_s3_data_source(bucket=bucket)

        return kb