#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_ec2.cdk_ec2_stack import CdkEc2Stack


app = cdk.App()
CdkEc2Stack(app, "CdkEc2Stack", env=cdk.Environment(account='736936197866', region='us-east-1'))
app.synth()
