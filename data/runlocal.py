#!/usr/bin/env python

import sys
import os
import time
import boto3
import re

if len(sys.argv) < 3:
    print "Usage: ./runlocal.py <mp3 file> <YYYYMMDD>"
    exit(0)

f = sys.argv[1]
timestamp = sys.argv[2]

if not f.endswith('mp3'):
    print "File should end with mp3"
    exit(0)

if not os.path.exists(f):
    print "File {0} doesn't exist".format(f)
    exit(0)

create_time = time.ctime(os.path.getctime(f))
client = boto3.client('s3')
s3_key = "{0}.mp3".format(timestamp)

with open(f, 'r') as fd:
    print("uploading {0} to s3...".format(f))
    client.put_object(
        Bucket='convo-upload',
        ACL='private',
        Body=fd,
        Key=s3_key)
    print("uploaded {0}".format(f))
