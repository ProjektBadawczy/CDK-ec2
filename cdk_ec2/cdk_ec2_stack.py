import aws_cdk as core

from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    Stack
)
from constructs import Construct


class CdkEc2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # VPC
        vpc = ec2.Vpc(self, "VPC",
                      nat_gateways=0,
                      subnet_configuration=
                      [ec2.SubnetConfiguration(name="public", subnet_type=ec2.SubnetType.PUBLIC)]
                      )

        # AMI
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2022,
            edition=ec2.AmazonLinuxEdition.STANDARD
        )

        # Instance Role and SSM Managed Policy
        role = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"))

        # Create a security group that allows HTTP traffic on port 80 for our
        # containers without modifying the security group on the instance
        security_group = ec2.SecurityGroup(
            self, "SecurityGroup",
            vpc=vpc,
            allow_all_outbound=True
        )

        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80),
        )

        # Applications
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(8001),
        )

        # SSH connection
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22),
        )

        instance_type = core.CfnParameter(self, "instanceType", type="String",
                                          description="The instance type for EC2 machines")

        # Instance for applications
        instance_applications = ec2.Instance(self, "InstanceApplications",
            instance_type=ec2.InstanceType(instance_type.value_as_string),
            machine_image=amzn_linux,
            vpc=vpc,
            role=role,
            security_group=security_group,
            key_name="ssh-key"
            )

        # Instance for JMeter
        instance_testing = ec2.Instance(self, "InstanceTesting",
            instance_type=ec2.InstanceType(instance_type.value_as_string),
            machine_image=amzn_linux,
            vpc=vpc,
            role=role,
            security_group=security_group,
            key_name="ssh-key"
            )

