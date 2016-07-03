#!/usr/bin/env python

import os
import subprocess
import logging
import boto3
import secrets
import requests
import urllib
import google_Drive

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond_to_file(mp3_file):
    # for running locally
    timestamp = os.path.basename(mp3_file).split(".")[0]
    left_file, right_file = "/tmp/left.ogg", "/tmp/right.ogg"
    _split_and_convert_to_ogg(mp3_file, left_file, right_file)
    left_job_id = _call_watson(left_file)
    right_job_id = _call_watson(right_file)
    _save_record(timestamp, left_job_id, right_job_id)
    _save_mp3_to_gdrive(mp3_file)

def respond_to_s3(key):
    # for running from AWS lambda
    # see https://aws.amazon.com/blogs/compute/running-executables-in-aws-lambda/
    os.environ["PATH"] = "{0}:{1}".format(os.environ["PATH"], os.environ["LAMBDA_TASK_ROOT"])
    logger.info("Set path to {0}".format(os.environ["PATH"]))

def _save_record(timestamp, left_job_id, right_job_id):
    client = boto3.client('dynamodb')
    client.put_item(
        TableName='recordings',
        Item={
            'left_job_id': left_job_id,
            'right_job_id': right_job_id
        })

def _save_mp3_to_gdrive(mp3_file):
    google_drive.save_file(mp3_file)

def _call_watson(ogg_file):
    watson_opts = dict(
        continuous="true",
        inactivity_timeout="-1",
        timestamps="true",
        smart_formatting="false",
        profanity_filter="false"
    )
    if secrets.callback_url is not None:
        watson_opts['callback_url'] = secrets.callback_url
        watson_opts['events'] = 'recognitions.completed'
    url = "https://stream.watsonplatform.net/speech-to-text/api/v1/recognitions"
    url = "{0}?{1}".format(url, urllib.urlencode(watson_opts))

    logger.info("Calling watson url {0}".format(url))
    
    with open(ogg_file, 'r') as f:
        r = requests.post(
            url,
            auth=(secrets.watson_username, secrets.watson_password),
            headers={ 'Content-Type': 'audio/ogg;codecs=opus' },
            data=f)

    if r.status_code == 201:
        return r.json()
    else:
        raise Exception("{0}: {1}".format(r.status_code, r.text))

def _split_and_convert_to_ogg(file_name, left_file, right_file):
    cmd = ["ffmpeg",
           "-i", file_name,
           "-acodec", "libopus",
           "-map_channel", "0.0.0", "/tmp/left.ogg",
           "-map_channel", "0.0.1", "/tmp/right.ogg"]
    output = subprocess.check_output(
        cmd,
        stderr=subprocess.STDOUT,
        shell=True)
    logger.info("Ran ffmpeg, got output: {0}".format(output))
