#!/usr/bin/env python

import os
import subprocess
import logging
import boto3
import secrets
import requests
import urllib
import google_drive
import tempfile
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond_to_file(mp3_file):
    # for running locally
    secrets.load_creds()
    timestamp = os.path.basename(mp3_file).split(".")[0]
    left, right = _newogg("left"), _newogg("right")
    try:
        _split_and_convert_to_ogg(mp3_file, left, right)
    except subprocess.CalledProcessError, e:
        logger.error(e.output)
        return
    left_id = _call_watson(left, "{0}:left".format(timestamp))
    right_id = _call_watson(right, "{0}.right".format(timestamp))
    _save_record(left_id, timestamp, 'left')
    _save_record(right_id, timestamp, 'right')
    _save_mp3_to_gdrive(mp3_file)

def respond_to_s3(key):
    # for running from AWS lambda
    # see
    # https://aws.amazon.com/blogs/compute/running-executables-in-aws-lambda/
    secrets.load_creds()
    os.environ["PATH"] = "{0}:{1}".format(
        os.environ["PATH"], os.environ["LAMBDA_TASK_ROOT"])
    logger.info("Set path to {0}".format(os.environ["PATH"]))

def _save_record(transcript_id, timestamp, side):
    client = boto3.client('dynamodb')
    client.put_item(
        TableName='Recordings',
        Item={
            'Id': { 'S': transcript_id },
            'Timestamp': { 'S': timestamp },
            'Side': { 'S': side },
            'CurrentTime': { 'N': time.time() }
        })

def _save_mp3_to_gdrive(mp3_file):
    google_drive.save_file(mp3_file)

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

def _newogg(prefix):
    file_name = "/tmp/{0}.ogg".format(prefix)
    try:
        os.remove(file_name)
    except:
        pass
    return file_name

if __name__ == '__main__':
    logging.basicConfig()
    mp3_file = os.path.join(os.path.dirname(__file__), '..', 'talk', 'simpletest.mp3')
    mp3_file = os.path.abspath(mp3_file)
    respond_to_file(mp3_file)
