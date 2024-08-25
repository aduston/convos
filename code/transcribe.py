"""
Iterates over a bucket of normalized audio/info files produced by the
audio-normalizer service and transcribes them using the Google
Speech-to-Text API
"""

import asyncio
import os
from typing import cast
from google.cloud import storage
from google.cloud.speech_v2 import SpeechAsyncClient
from google.cloud.speech_v2.types import cloud_speech
from google.protobuf import json_format

PROJECT_ID = "aad-personal"
BUCKET_NAME = "psycho-convos"


async def transcribe(
    blob: storage.Blob,
    storage_client: storage.Client,
    model: str = "long"
) -> None:
    """
    Transcribes the audio file in the given blob. The model parameter
    is "long" by default, but can also be set to "telephony", which
    might work better for our audio.
    """
    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["en-US"],
        model=model
    )
    blob_uri = f"gs://{blob.bucket.name}/{blob.name}"
    file_metadata = cloud_speech.BatchRecognizeFileMetadata(uri=blob_uri)
    request = cloud_speech.BatchRecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
        config=config,
        files=[file_metadata],
        recognition_output_config=cloud_speech.RecognitionOutputConfig(
            inline_response_config=cloud_speech.InlineOutputConfig(),
        ),
        processing_strategy=(
            # according to https://t.ly/ZWMas, "Dynamic batching enables lower
            # cost transcription for higher latency"
            cloud_speech.BatchRecognizeRequest.ProcessingStrategy.
            DYNAMIC_BATCHING
        ),
    )
    client = SpeechAsyncClient()
    operation = await client.batch_recognize(request=request, timeout=300)
    response = await operation.result()
    response = cast(cloud_speech.BatchRecognizeResponse, response)
    for audio_uri, result in response.results.items():
        print("Error: ", result.error)
        bucket_name = audio_uri.split('/')[2]
        file_name = os.path.basename(audio_uri).replace(".wav", "_.txt")
        output_blob = storage.Blob(f"transcriptions/{file_name}", bucket_name)
        transcript_json = json_format.MessageToJson(result.transcript)
        output_blob.upload_from_string(
            data=transcript_json,
            client=storage_client)


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
        await transcribe(blob, storage_client)
        break


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
