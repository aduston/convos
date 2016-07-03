#!/usr/bin/env python

import zipfile
import os
import os.path
import boto3
import tempfile
import secrets

def _make_zip(zip_file):
    data_dir = os.path.dirname(os.path.realpath(__file__))
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as deployment:
        for f in os.listdir(data_dir):
            if f.endswith('.py') or f in ['ffmpeg', 'encrypted_creds.json']:
                deployment.write(os.path.join(data_dir, f), f)
        site_packages_dir = os.path.abspath(os.path.join(
            data_dir, '..', 'venv', 'lib', 'python2.7', 'site-packages'))
        for root, dirs, files in os.walk(site_packages_dir):
            for f in files:
                full_path = os.path.join(root, f)
                site_packages_relpath = os.path.relpath(full_path, site_packages_dir)
                if not site_packages_relpath.startswith('boto'):
                    relpath = os.path.relpath(full_path, site_packages_dir)
                    deployment.write(full_path, relpath)

def _update_function(client, function_name, zip_file_bytes):
    client.update_function_code(
        FunctionName=function_name,
        ZipFile=zip_file_bytes,
        Publish=True)

def _update_all():
    secrets.write_creds_file()
    zip_file_bytes = None
    with tempfile.TemporaryFile() as temp_file:
        _make_zip(temp_file)
        temp_file.seek(0)
        zip_file_bytes = temp_file.read()
    client = boto3.client('lambda')
    function_names = ["SpeechToTextCallback"]
    for function_name in function_names:
        _update_function(client, function_name, zip_file_bytes)

def _make_zip_file():
    with open('lambda.zip', 'wb') as f:
        _make_zip(f)
        
if __name__ == '__main__':
    _update_all()
