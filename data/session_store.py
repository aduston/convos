#!/usr/bin/env python

import boto3
import botocore
import time

def save_session_record(shard_id, timestamp, left_id, right_id):
    client = boto3.client('dynamodb')
    client.put_item(
        TableName='Sessions',
        Item={
            'ShardId': { 'N': str(shard_id) },
            'Timestamp': { 'N': str(timestamp) },
            'Recordings': { 'M': {
                'left': { 'M': {
                    'Id': { 'S': left_id },
                    'Complete': { 'BOOL': False }
                }},
                'right': { 'M': {
                    'Id': { 'S': right_id },
                    'Complete': { 'BOOL': False }
                }}
            }}
        })

def recording_complete(transcript_id, shard_id, timestamp, side):
    # returns True if both sides are done.
    key = {
        'ShardId': { 'N': str(shard_id) },
        'Timestamp': { 'N': str(timestamp) }
    }
    client = boto3.client('dynamodb')
    client.update_item(
        TableName='Sessions', Key=key,
        UpdateExpression="SET #complete = :true",
        ExpressionAttributeNames={
            '#complete': 'Recordings.{0}.Complete'.format(side)
        },
        ExpressionAttributeValues={ ':true': { 'BOOL': True }})
    condition_expression = "#leftcomplete = :true AND " \
                           "#rightcomplete = :true AND " \
                           "attribute_not_exists(ProcessingStartedAt)"
    try:
        client.update_item(
            TableName='Sessions', Key=key,
            UpdateExpression="SET ProcessingStartedAt = :now",
            ConditionExpression=condition_expression,
            ExpressionAttributeNames={
                '#leftcomplete': 'Recordings.left.Complete',
                '#rightcomplete': 'Recordings.right.Complete'
            },
            ExpressionAttributeValues={
                ':true': { 'BOOL': True },
                ':now': { 'N': str(int(time.time())) }
            })
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return False
        else:
            raise
    else:
        return True

def recording_processing_complete():
    # TODO: write me
    pass

if __name__ == '__main__':
    save_session_record(0, 123, 'a', 'b')
    print recording_complete('a', 0, 123, 'left')
    print recording_complete('b', 0, 123, 'right')
