import boto3
import botocore
import os
from awsconfig import talkbucket

talkdir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '..', 'talk')

client = boto3.client('s3')

def upload_file(full_path, file_name):
    exists = True
    try:
        client.head_object(
            Bucket=talkbucket,
            Key=file_name)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            exists = False
        else:
            raise e
    if exists:
        print "{0} already in S3".format(file_name)
    else:
        with open(full_path, 'r') as fd:
            client.put_object(
                Bucket=talkbucket,
                ACL='private',
                Body=fd,
                Key=file_name)
        print "Successfully uploaded {0} to S3".format(file_name)

for f in os.listdir(talkdir):
    if f.startswith("Psycho"):
        full_path = os.path.join(talkdir, f)
        upload_file(full_path, f)
