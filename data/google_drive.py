import secrets
from apiclient import discovery
from oauth2client import client
import oauth2client
import boto3
import json
import os
import httplib2

FOLDER_ID = '0ByRPCyLgUZBTZy1GbDliY3Z5Yms'

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
    secrets.load()
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
    secrets.load()
    token_expiry, access_token, refresh_token = _get_access_token_record()
    if creds.token_expiry != token_expiry or creds.access_token != access_token:
        _set_access_token_record(token_expiry, access_token, refresh_token)

def save_file(file_name, mime_type):
    # note this function is idempotent, and therefore potentially
    # destructive. in other words, it will try to delete any files
    # with this name from the directory prior to creating a new one.
    credentials = _get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    files = service.files()
    gdrive_file_name = os.path.basename(file_name)
    _delete_existing(gdrive_file_name, files)
    f = files.create(
        body={
            'parents': [FOLDER_ID],
            'name': gdrive_file_name,
            'viewersCanCopyContent': True,
            'mimeType': mime_type
        },
        media_body=file_name).execute()
    print("created {0}".format(f['id']))
    _save_credentials(credentials)
    return f['id']

def _delete_existing(file_name, files):
    query = "name = '{0}' and '{1}' in parents".format(file_name, FOLDER_ID)
    file_listing = files.list(q=query).execute()
    file_ids = [f['id'] for f in file_listing['files']]
    for file_id in file_ids:
        print("deleting {0}".format(file_id))
        files.delete(fileId=file_id).execute()

if __name__ == '__main__':
    print save_file('../talk/20050630.mp3', 'audio/mpeg')
