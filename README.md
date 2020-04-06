# scp-validator #

## Outline ##

This solution uses CloudTrail and Lambda to alert on any activity outside of approved regions/services.

## Deployment ##

1. Set your Cloudtrail name and subscription email in `parameters.env`.
1. Set your LOCAL_REGIONS, WHITELISTED_REGIONS, and WHITELISTED_SERVICES in `lambda_function.py`.
1. Package and deploy the solution: `sam package --template-file master.yaml --output-template-file package.yaml --s3-bucket jk-sls-bucket && sam deploy --template-file package.yaml --stack-name lambda-alert2  --parameter-overrides "$(cat parameters.env)" --capabilities CAPABILITY_IAM`

## Details ##

The stack takes the following as inputs:

 * The name of an existing Cloudtrail trail
 * An email address

It will create:

 * A Cloudwatch Logs LogGroup with a filter that matches any mutable API call
 * A Lambda function to check whether these events are occurring in any region/service that hasn't been whitelisted
 * A Lambda function to run once on deployment and link the Cloudtrail trail with the Cloudwatch Logs LogGroup
 * An SNS topic with the input email address as a subscriber