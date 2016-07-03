import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle_callback(event, context):
    # gets:
    #
    # {
    #     "headers": {},
    #     "params": {},
    #     "method": "GET",
    #     "query": {}
    # }
    logger.info(json.dumps(event))
    if event["method"] == "GET":
        query = event['query']
        if 'challenge_string' in query:
            return query['challenge_string']
        else:
            return "no challenge string, but that's okay!"
    else:
        return "ok"
