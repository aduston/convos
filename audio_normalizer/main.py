"""
Used to normalize audio files.
"""


import os
import subprocess
import tempfile
from flask import Flask, request
from google.cloud import storage

app = Flask(__name__)


def info_for_file(file_name: str) -> str:
    """
    Output when run on a .m4a: https://pastebin.com/Dakr7hjS
    .mp4: https://pastebin.com/NQ8azUiV
    .mp3: https://pastebin.com/TSvwQ9E4

    Notice each has the following fields:

    * duration
    * bit_rate
    * sample_rate
    * channels
    * channel_layout
    """
    try:
        result = subprocess.run(
            [
                'ffprobe',
                '-i',
                file_name,
                '-show_streams',
                '-select_streams',
                'a:0'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return result.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        return e.stderr.decode("utf-8")


def convert_to_wav(input_file_name: str, output_file_name: str) -> None:
    """
    Converts to LINEAR16 format
    """
    subprocess.run(
        [
            'ffmpeg',
            '-y',
            '-i',
            input_file_name,
            '-acodec',
            'pcm_s16le',
            output_file_name
        ],
        check=True
    )


def process_normalize_request(
        input_file_uri: str,
        output_wav_file_uri: str,
        output_info_file_uri: str,
        ) -> None:
    """
    Downloads the input file, normalizes it, and obtains audio info.
    Uploads both the normalized file and audio info.
    """
    storage_client = storage.Client()
    output_wav_blob = storage.Blob.from_string(
        output_wav_file_uri, storage_client)
    output_info_blob = storage.Blob.from_string(
        output_info_file_uri, storage_client)
    with tempfile.NamedTemporaryFile() as input_temp_file, \
            tempfile.NamedTemporaryFile(suffix=".wav") as output_temp_file:
        storage_client.download_blob_to_file(
            input_file_uri, input_temp_file)
        info = info_for_file(input_temp_file.name)
        output_info_blob.upload_from_string(info)
        convert_to_wav(input_temp_file.name, output_temp_file.name)
        output_wav_blob.upload_from_file(output_temp_file)


@app.route("/")
def normalize():
    """
    Flask endpoint for normalizing audio files.
    """
    input_file_uri = request.args.get("input_file_uri")
    output_wav_file_uri = request.args.get("output_wav_file_uri")
    output_info_file_uri = request.args.get("output_info_file_uri")
    process_normalize_request(
        input_file_uri, output_wav_file_uri, output_info_file_uri)
    return "OK"


if __name__ == '__main__':
    app.run(
        debug=True,
        host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
