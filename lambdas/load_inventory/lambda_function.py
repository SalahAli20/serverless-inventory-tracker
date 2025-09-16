# Load-Inventory Lambda function
#
# This function is invoked when an object is uploaded to an S3 bucket.
# It downloads the file, reads inventory records, and inserts them into DynamoDB.

import json
import urllib.parse
import boto3
import csv

# Connect to AWS resources
s3 = boto3.resource('s3')
dynamodb = boto3.resource('dynamodb')

# Reference to DynamoDB table
inventory_table = dynamodb.Table('Inventory')

def lambda_handler(event, context):
    print("Event received by Lambda function: " + json.dumps(event, indent=2))

    # Get bucket and object details from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

    local_filename = '/tmp/inventory.csv'

    try:
        # Download the file locally
        s3.meta.client.download_file(bucket, key, local_filename)
    except Exception as e:
        print(f"Error downloading file {key} from bucket {bucket}: {e}")
        raise e

    row_count = 0
    try:
        # Read CSV file and insert into DynamoDB
        with open(local_filename) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                row_count += 1
                print(row['store'], row['item'], row['count'])
                try:
                    inventory_table.put_item(
                        Item={
                            'Store': row['store'],
                            'Item': row['item'],
                            'Count': int(row['count'])
                        }
                    )
                except Exception as e:
                    print(f"Unable to insert data into DynamoDB table: {e}")

        return f"{row_count} records inserted into DynamoDB."
    except Exception as e:
        print(f"Error processing file: {e}")
        raise e
