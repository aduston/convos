#!/usr/bin/env python

import sys
import os
import time
import boto3
import subprocess

if len(sys.argv) < 2:
    print "Usage: ./runlocal.py <mp3 file>"
    exit(0)

f = sys.argv[1]

if not f.endswith('mp3'):
    print "File should end with mp3"
    exit(0)

if not os.path.exists(f):
    print "File {0} doesn't exist".format(f)
    exit(0)

session = boto3.Session(profile_name='convos')
client = session.client('s3')
s3_key = os.path.basename(f)

with open(f, 'r') as fd:
    print("uploading {0} to s3 as {1}".format(f, s3_key))
    client.put_object(
        Bucket='convo-upload',
        ACL='private',
        Body=fd,
        Key=s3_key)
    print("uploaded {0}".format(f))

print("securely deleting {0}".format(f))
subprocess.call(['srm', f])
