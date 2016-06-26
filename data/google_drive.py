import secrets
from apiclient import discovery
from oauth2client import client
import oauth2client
import boto3
import json
import os
import httplib2

def _get_access_token_record():
    client = boto3.client('dynamodb')
    response = client.get_item(
        TableName='GDriveCreds',
        Key={
            'Id': { 'N': '1' },
        },
        ConsistentRead=True)
    value = json.loads(secrets.decrypt(response['Item']['Record']['S']))
    return value['token_expiry'], value['access_token'], value['refresh_token']

def _set_access_token_record(token_expiry, access_token, refresh_token):
    encrypted = secrets.encrypt(json.dumps(dict(
        token_expiry=token_expiry,
        access_token=access_token,
        refresh_token=refresh_token
    )))
    client = boto3.client('dynamodb')
    client.put_item(
        TableName='GDriveCreds',
        Item={
            'Id': { 'N': '1' },
            'Record': { 'S': encrypted },
        })

def _get_credentials():
    secrets.load_creds()
    token_expiry, access_token, refresh_token = _get_access_token_record()
    return client.OAuth2Credentials(
        access_token,
        secrets.gdrive_client_id,
        secrets.gdrive_client_secret,
        refresh_token,
        token_expiry,
        "https://accounts.google.com/o/oauth2/token",
        "convo-saver",
        scopes=["https://www.googleapis.com/auth/drive.file"])

def _save_credentials(creds):
    secrets.load_creds()
    token_expiry, access_token, refresh_token = _get_access_token_record()
    if creds.token_expiry != token_expiry or creds.access_token != access_token:
        _set_access_token_record(token_expiry, access_token, refresh_token)

def save_file(file_name, mime_type):
    credentials = _get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    f = service.files().create(
        body={
            'parents': ['0ByRPCyLgUZBTZy1GbDliY3Z5Yms'],
            'name': os.path.basename(file_name),
            'viewersCanCopyContent': True,
            'mimeType': mime_type
        },
        media_body=file_name).execute()
    _save_credentials(credentials)
    return f.get('id')

if __name__ == '__main__':
    print save_file('../talk/simpletest.mp3', 'audio/mpeg')
