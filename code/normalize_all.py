"""
Runs the normalization process for all audio files in the input bucket.

The normalization process is defined in the audio_normalizer directory.

In order to run this, one must have a service account key stored locally,
with the GOOGLE_APPLICATION_CREDENTIALS environment variable pointing to it.
"""

import asyncio
import urllib
from urllib.parse import urlencode

import google.auth.transport.requests
import google.oauth2.id_token

# ENDPOINT is output by the gcloud run deploy command in the audio_normalizer
# README file
ENDPOINT = "https://audio-normalizer-299102048728.us-central1.run.app"


async def main() -> None:
    """
    Send request to the audio-normalizer service
    """
    params = {
        "input_file_uri": "gs://psycho-convos/20161128.mp3",
        "output_wav_file_uri": "gs://psycho-convos/normalized/20161128.wav",
        "output_info_file_uri":
            "gs://psycho-convos/normalized/20161128_info.txt"
    }
    url = f"{ENDPOINT}/?{urlencode(params)}"
    req = urllib.request.Request(url, method="GET")
    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, ENDPOINT)
    req.add_header("Authorization", f"Bearer {id_token}")
    response = urllib.request.urlopen(req)
    code = response.getcode()
    if code != 200:
        raise ValueError(f"Failed to normalize audio files: {code}")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
