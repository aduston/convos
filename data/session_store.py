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
            'LeftId': { 'S': left_id },
            'LeftComplete': { 'BOOL': False },
            'RightId': { 'S': right_id },
            'RightComplete': { 'BOOL': False }
        })

def _key(shard_id, timestamp):
    return {
        'ShardId': { 'N': str(shard_id) },
        'Timestamp': { 'N': str(timestamp) }
    }

def update_session_record(shard_id, timestamp, side, side_id, side_complete):
    client = boto3.client('dynamodb')
    update_expression = \
        "SET {0}Id = :side_id, {0}Complete = :side_complete".format(
            side.title())
    client.update_item(
        TableName='Sessions',
        Key=_key(shard_id, timestamp),
        UpdateExpression=update_expression,
        ExpressionAttributeValues={
            ':side_id': { 'S': side_id },
            ':side_complete': { 'BOOL': side_complete }
        })

def recording_complete(transcript_id, shard_id, timestamp, side):
    # returns record if both sides are done.
    update_session_record(shard_id, timestamp, side, transcript_id, True)
    condition_expression = "LeftComplete = :true AND " \
                           "RightComplete = :true AND " \
                           "attribute_not_exists(ProcessingStartedAt)"
    client = boto3.client('dynamodb')
    try:
        item = client.update_item(
            TableName='Sessions',
            Key=_key(shard_id, timestamp),
            UpdateExpression="SET ProcessingStartedAt = :now",
            ConditionExpression=condition_expression,
            ReturnValues='ALL_NEW',
            ExpressionAttributeValues={
                ':true': { 'BOOL': True },
                ':now': { 'N': str(int(time.time())) }
            })
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return None
        else:
            raise
    else:
        return item['Attributes']

def recording_processing_complete():
    # TODO: write me
    pass

if __name__ == '__main__':
    save_session_record(0, 123, 'a', 'None')
    update_session_record(0, 123, 'right', 'b', False)
    print recording_complete('a', 0, 123, 'left')
    print recording_complete('b', 0, 123, 'right')
