#!/usr/bin/env python

import os
import subprocess
import logging
import boto3
import secrets
import requests
import urllib
import google_drive
import session_store
import tempfile
import time
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond_to_file(mp3_file):
    # for running locally
    secrets.load()
    timestamp = int(os.path.basename(mp3_file).split(".")[0])
    left, right = _newogg("left", timestamp), _newogg("right", timestamp)
    try:
        _split_and_convert_to_ogg(mp3_file, left, right)
    except subprocess.CalledProcessError, e:
        logger.error(e.output)
        return
    shard_id = timestamp % 16
    logger.info("sending left side of {0} to watson".format(timestamp))
    left_id = _call_watson(left, "{0}:{1}:left".format(shard_id, timestamp))
    session_store.save_session_record(shard_id, timestamp, left_id, 'None')
    logger.info("sending right side of {0} to watson".format(timestamp))
    right_id = _call_watson(right, "{0}:{1}:right".format(shard_id, timestamp))
    session_store.update_session_record(
        shard_id, timestamp, 'right', right_id, False)
    logger.info("saving {0} to gdrive".format(timestamp))
    google_drive.save_file(mp3_file, 'audio/mpeg')
    logger.info("done with {0}".format(timestamp))
    # TODO: save mp3 to s3?

def lambda_handler(event, context):
    secrets.load()
    # https://aws.amazon.com/blogs/compute/running-executables-in-aws-lambda/
    logger.info("Received event: {0}".format(json.dumps(event)))
    os.environ["PATH"] = "{0}:{1}".format(
        os.environ["PATH"], os.environ["LAMBDA_TASK_ROOT"])
    logger.info("Set path to {0}".format(os.environ["PATH"]))
    s3_record = event['Records'][0]['s3']
    bucket = s3_record['bucket']['name']
    key = urllib.unquote_plus(s3_record['object']['key']).decode('utf8')
    respond_to_s3(bucket, key)

def respond_to_s3(bucket, key):
    s3 = boto3.client('s3')
    temp_file = "/tmp/{0}".format(key)
    logger.info("going to try to download {0}/{1}".format(bucket, key))
    s3.download_file(bucket, key, temp_file)
    respond_to_file(temp_file)
    # TODO: delete key from bucket?

def _call_watson(ogg_file, label):
    watson_opts = dict(
        continuous="true",
        inactivity_timeout="-1",
        timestamps="true",
        smart_formatting="false",
        profanity_filter="false",
        callback_url=secrets.callback_url,
        user_token=label,
        events='recognitions.completed'
    )
    url = "https://stream.watsonplatform.net/speech-to-text" \
          "/api/v1/recognitions?{0}".format(
              urllib.urlencode(watson_opts))

    logger.info("Calling watson url {0}".format(url))
    
    with open(ogg_file, 'r') as f:
        r = requests.post(
            url,
            auth=(secrets.watson_username, secrets.watson_password),
            headers={ 'Content-Type': 'audio/ogg;codecs=opus' },
            data=f)

    if r.status_code == 201:
        return r.json()['id']
    else:
        raise Exception("{0}: {1}".format(r.status_code, r.text))

def _split_and_convert_to_ogg(file_name, left_file, right_file):
    cmd = ["ffmpeg",
           "-i", file_name,
           "-acodec", "libopus",
           "-map_channel", "0.0.0", left_file,
           "-map_channel", "0.0.1", right_file]
    logger.info("going to run {0}".format(' '.join(cmd)))
    output = subprocess.check_output(
        cmd,
        stderr=subprocess.STDOUT)
    logger.info("Ran ffmpeg, got output: {0}".format(output))

def _newogg(prefix, timestamp):
    file_name = "/tmp/{0}{1}.ogg".format(prefix, timestamp)
    try:
        os.remove(file_name)
    except:
        pass
    return file_name

if __name__ == '__main__':
    logging.basicConfig()
    mp3_file = os.path.join(os.path.dirname(__file__), '..', 'talk', '20050630.mp3')
    mp3_file = os.path.abspath(mp3_file)
    respond_to_file(mp3_file)
