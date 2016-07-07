import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle_callback(event, context):
    logger.info(json.dumps(event))
    if event["method"] == "GET":
        query = event['query']
        if 'challenge_string' in query:
            return query['challenge_string']
        else:
            return "no challenge string, but that's okay!"
    else:
        body = event['body']
        shard_id, timestamp, side = body['user_token'].split(':')
        transcript_id = body['id']
        can_process = session_store.recording_complete(
            transcript_id, int(shard_id), int(timestamp), side)
        if can_process:
            _process(int(shard_id), int(timestamp))

def _process(shard_id, timestamp):
    # TODO: write me
    pass
