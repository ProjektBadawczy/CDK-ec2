from aws_cdk.aws_s3_assets import Asset

from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    Stack,
)
from constructs import Construct

class CdkEc2Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # VPC
        vpc = ec2.Vpc(self, "VPC",
                      nat_gateways=0,
                      subnet_configuration=[ec2.SubnetConfiguration(name="public", subnet_type=ec2.SubnetType.PUBLIC)]
                      )

        # AMI
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )

        # Instance Role and SSM Managed Policy
        role = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"))

        # Create a security group that allows HTTP traffic on port 80 for our
        # containers without modifying the security group on the instance
        security_group = ec2.SecurityGroup(
            self, "group",
            vpc=vpc,
            allow_all_outbound=True
        )
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(80)
        )

        # Instance for applications
        instance_applications = ec2.Instance(self, "Instance_applications",
            instance_type=ec2.InstanceType("t3.nano"),
            machine_image=amzn_linux,
            vpc = vpc,
            role = role
            )

        # Instance for JMeter
        instance_testing = ec2.Instance(self, "Instance_testing",
            instance_type=ec2.InstanceType("t3.nano"),
            machine_image=amzn_linux,
            vpc = vpc,
            role = role
            )

        # Script in S3 as Asset
        asset = Asset(self, "Asset", path="../configure.sh")

        local_path = instance_applications.user_data.add_s3_download_command(
            bucket=asset.bucket,
            bucket_key=asset.s3_object_key
        )

        # Userdata executes script from S3
        instance_applications.user_data.add_execute_file_command(
            file_path=local_path
            )
        asset.grant_read(instance_applications.role)

