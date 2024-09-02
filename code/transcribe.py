"""
Iterates over a bucket of normalized audio/info files produced by the
audio-normalizer service and transcribes them using the Google
Speech-to-Text API
"""

import asyncio
from typing import cast
from google.cloud import storage
import transcribe_two_channel

BUCKET_NAME = "psycho-convos"


async def main() -> None:
    """
    Iterates over all .wav files in the normalized directory and transcribes
    them
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    for raw_blob in bucket.list_blobs(match_glob="normalized/*.wav"):
        blob = cast(storage.Blob, raw_blob)
        blob_uri = f"gs://{blob.bucket.name}/{blob.name}"
        print(f"Transcribing {blob_uri}")
        await transcribe_two_channel.transcribe(blob, "FIXME bucket name")
        break


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
