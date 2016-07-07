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
        timestamp, side = body['user_token'].split('.')
        transcript_id = body['id']
        _save_transcript_results(transcript_id, timestamp, side)
        return "ok"

def _save_transcript_results(transcript_id, timestamp, side):
    # TODO: write me
    pass
