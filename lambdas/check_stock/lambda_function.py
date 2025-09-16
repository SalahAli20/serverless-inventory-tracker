# Check-Stock Lambda function
#
# This function is triggered by DynamoDB Streams when a new record is added.
# It checks if an item has zero stock and sends a notification via SNS.

import json
import boto3

# SNS client
sns = boto3.client('sns')

def lambda_handler(event, context):
    print("Event received by Lambda function: " + json.dumps(event, indent=2))

    for record in event['Records']:
        new_image = record['dynamodb'].get('NewImage', None)

        if new_image:
            count = int(new_image['Count']['N'])
            if count == 0:
                store = new_image['Store']['S']
                item = new_image['Item']['S']

                # Construct message
                message = f"{store} is out of stock of {item}"
                print(message)

                # Find SNS topic ARN for NoStock
                alert_topic = 'NoStock'
                topic_arn = [
                    t['TopicArn'] for t in sns.list_topics()['Topics']
                    if t['TopicArn'].lower().endswith(':' + alert_topic.lower())
                ][0]

                # Publish message to SNS
                sns.publish(
                    TopicArn=topic_arn,
                    Message=message,
                    Subject='Inventory Alert!',
                    MessageStructure='raw'
                )

    return f"Successfully processed {len(event['Records'])} records."
