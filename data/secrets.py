#!/usr/bin/env python

import os
import sys
import json
import boto3
import base64

KMS_KEY_ID = '2bf1fe02-ebaa-4f21-b3a3-066dcb08da01'

# these get set by load
_secrets_read = False
watson_password = None
watson_username = None
gdrive_client_id = None
gdrive_client_secret = None
callback_url = None
upload_s3_bucket = None
target_s3_bucket = None

def encrypt(plaintext):
    client = boto3.client('kms')
    response = client.encrypt(
        KeyId=KMS_KEY_ID,
        Plaintext=plaintext)
    return base64.b64encode(response['CiphertextBlob'])

def decrypt(encrypted):
    client = boto3.client('kms')
    response = client.decrypt(
        CiphertextBlob=base64.b64decode(encrypted))
    return response['Plaintext']

def write_secrets_file():
    # writes a creds file that you can just check into source control
    raw_creds = None
    with open(os.path.join(os.path.dirname(__file__), 'secrets.json'), 'r') as inf:
        with open('encrypted_secrets.json', 'w') as outf:
            outf.write(encrypt(inf.read()))

def load():
    global _secrets_read
    if _secrets_read:
        return
    module = sys.modules[__name__]
    with open(os.path.join(os.path.dirname(__file__), 'encrypted_secrets.json'), 'r') as f:
        secrets_obj = json.loads(decrypt(f.read()))
        for name, value in secrets_obj.iteritems():
            setattr(module, name, value)
    _secrets_read = True

if __name__ == '__main__':
    write_secrets_file()
