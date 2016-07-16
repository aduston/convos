#!/usr/bin/env python

import zipfile
import os
import os.path
import boto3
import tempfile
import secrets

def _make_zip(zip_file, include_ffmpeg):
    data_dir = os.path.dirname(os.path.realpath(__file__))
    files_to_include = ['encrypted_secrets.json']
    if include_ffmpeg:
        files_to_include.append('ffmpeg')
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as deployment:
        for f in os.listdir(data_dir):
            if f.endswith('.py') or f in files_to_include:
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
    secrets.write_secrets_file()
    zip_bytes = {
        True: _zip_file_bytes(True),
        False: _zip_file_bytes(False)
    }
    client = boto3.client('lambda')
    functions = [
        dict(name="SpeechToTextCallback", include_ffmpeg=False),
        dict(name="AudioUploadResponder", include_ffmpeg=True)
    ]
    for function in functions:
        _update_function(
            client, function['name'], zip_bytes[function['include_ffmpeg']])

def _zip_file_bytes(include_ffmpeg):
    with tempfile.TemporaryFile() as temp_file:
        _make_zip(temp_file, include_ffmpeg)
        temp_file.seek(0)
        return temp_file.read()

def _make_zip_file():
    with open('lambda.zip', 'wb') as f:
        _make_zip(f)
        
if __name__ == '__main__':
    _update_all()
