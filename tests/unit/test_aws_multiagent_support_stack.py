import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_multiagent_support.aws_multiagent_support_stack import AwsMultiagentSupportStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_multiagent_support/aws_multiagent_support_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsMultiagentSupportStack(app, "aws-multiagent-support")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
