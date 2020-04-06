import json
import boto3
import gzip
import base64
import os

def lambda_handler(event, context):

    LOCAL_REGIONS=['ap-southeast-2']
    WHITELISTED_REGIONS=['us-west-2']
    WHITELISTED_SERVICES=['iam.amazonaws.com','route53.amazonaws.com','cloudfront.amazonaws.com','cloudtrail.amazonaws.com']
    
    # Create an SNS client
    sns = boto3.client('sns')
    topicarn = os.environ['SNS_TOPIC']
    
    cw_data = event['awslogs']['data']
    compressed_payload = base64.b64decode(cw_data)
    uncompressed_payload = gzip.decompress(compressed_payload)
    payload = json.loads(uncompressed_payload)
    
    alert_flag = False
    
    # Iterate through events to see if any have occurred in non-approved regions
    log_events = payload['logEvents']
    for log_event in log_events:
        message = log_event['message']
        json_msg = json.loads(message)
        region = json_msg['awsRegion']
        service = json_msg['eventSource']
        print(f'LogEvent: {region}')
        print(f'LogEvent: {service}')
    
        if region in LOCAL_REGIONS:
            print('Skipping local region...')
        elif region in WHITELISTED_REGIONS:
            if service in WHITELISTED_SERVICES:
                print('Skipping whitelisted services in whitelisted region...')
            else:
                print('WARNING: Non-approved service in whitelisted region!')
                alert_flag = True
        else:
            print('WARNING: Non-approved service in non-whitelisted region!')
            alert_flag = True
    
    # If an event has occurred in a non-approved region, raise an alert
    if alert_flag:
        response = sns.publish(
            TopicArn=topicarn,    
            Message=json.dumps(message),    
        )
        output = 'WARNING: Activity found in non-approved regions.'
    else:
        output = 'Activity occurring in approved regions.'
    
    return {
        'statusCode': 200,
        'body': json.dumps(output)
    }