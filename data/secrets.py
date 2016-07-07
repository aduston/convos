#!/usr/bin/env python

import os
import sys
import json
import boto3
import base64

KMS_KEY_ID = '2bf1fe02-ebaa-4f21-b3a3-066dcb08da01'

# these get set by load_creds
_creds_read = False
watson_password = None
watson_username = None
callback_url = None
gdrive_client_id = None
gdrive_client_secret = None
callback_url = None

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

def write_creds_file():
    # writes a creds file that you can just check into source control
    raw_creds = None
    with open(os.path.join(os.path.dirname(__file__), 'creds.json'), 'r') as inf:
        with open('encrypted_creds.json', 'w') as outf:
            outf.write(encrypt(inf.read()))

def load_creds():
    global _creds_read
    if _creds_read:
        return
    module = sys.modules[__name__]
    with open(os.path.join(os.path.dirname(__file__), 'encrypted_creds.json'), 'r') as f:
        decrypted = decrypt(f.read())
        creds = json.loads(decrypted)
        for name, value in creds.iteritems():
            setattr(module, name, value)
    _creds_read = True

if __name__ == '__main__':
    write_creds_file()
