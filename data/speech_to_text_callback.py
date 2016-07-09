import boto3
import logging
import json
import requests
import secrets
import session_store
import google_drive
import watson_output_processor

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle_callback(event, context):
    secrets.load_creds()
    if event["method"] == "GET":
        query = event['query']
        if 'challenge_string' in query:
            return query['challenge_string']
        else:
            return "no challenge string, but that's okay!"
    else:
        body = event['body']
        shard_id, timestamp, side = body['user_token'].split(':')
        shard_id, timestamp = int(shard_id), int(timestamp)
        transcript_id = body['id']
        logger.info(
            "Callback with shard_id {0}, timestamp {1}, side {2}, " \
            "transcript_id {3}".format(
                shard_id, timestamp, side, transcript_id))
        record = session_store.recording_complete(
            transcript_id, shard_id, timestamp, side)
        if record is not None:
            _process(record)

def _process(record):
    timestamp = int(record['Timestamp']['N'])
    logger.info("Processing record with timestamp {0}".format(timestamp))
    left_output = _get_watson_output(record['LeftId']['S'])
    right_output = _get_watson_output(record['RightId']['S'])
    readable_file = '/tmp/{0}.txt'.format(timestamp)
    with open(readable_file, 'w') as f:
        watson_output_processor.create_readable_transcript(
            left_output, right_output, f)
    google_drive.save_file(readable_file, 'text/plain')
    logger.info("Saved readable file for {0} to GDrive".format(timestamp))
    # TODO: send a notification
    # TODO: save json to S3.

def _get_watson_output(recognition_id):
    url = "https://stream.watsonplatform.net/speech-to-text/" \
          "api/v1/recognitions/{0}".format(recognition_id)
    r = requests.get(
        url, auth=(secrets.watson_username, secrets.watson_password))
    return r.json()
