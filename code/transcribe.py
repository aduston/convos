"""
Iterates over a bucket of normalized audio/info files produced by the
audio-normalizer service and transcribes them using the Google
Speech-to-Text API
"""

import asyncio
import json
import os
from typing import cast
from google.cloud import storage
from google.cloud.speech_v2 import SpeechAsyncClient
from google.cloud.speech_v2.types import cloud_speech

PROJECT_ID = "aad-personal"
BUCKET_NAME = "psycho-convos"
EXPERIMENT_LOG_DIR = "/Users/aduston/convo_experiments"


def create_two_channel_recognition_config(
        model: str) -> cloud_speech.RecognitionConfig:
    """
    Returns a RecognitionConfig object with the given model
    """
    # Note that diarization appears to not be supported for v2.
    # So we can only use v2 when there are two channels
    # (one channel per speaker)
    features = cloud_speech.RecognitionFeatures(
        profanity_filter=False,
        enable_automatic_punctuation=True,
        multi_channel_mode=(
            cloud_speech.RecognitionFeatures.MultiChannelMode.
            SEPARATE_RECOGNITION_PER_CHANNEL
        ),
    )
    return cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        features=features,
        language_codes=["en-US"],
        model=model
    )


def create_recognize_request(
    blob: storage.Blob,
    config: cloud_speech.RecognitionConfig
) -> cloud_speech.BatchRecognizeRequest:
    """
    Returns a BatchRecognizeRequest object with the given blob and config
    """
    blob_uri = f"gs://{blob.bucket.name}/{blob.name}"
    file_metadata = cloud_speech.BatchRecognizeFileMetadata(uri=blob_uri)
    return cloud_speech.BatchRecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
        config=config,
        files=[file_metadata],
        recognition_output_config=cloud_speech.RecognitionOutputConfig(
            gcs_output_config=cloud_speech.GcsOutputConfig(
                uri=f"gs://{blob.bucket.name}/transcriptions/"
            )
        ),
        processing_strategy=(
            # according to https://t.ly/ZWMas, "Dynamic batching enables lower
            # cost transcription for higher latency"
            cloud_speech.BatchRecognizeRequest.ProcessingStrategy.
            DYNAMIC_BATCHING
        ),
    )


def log_experiment_locally(
    audio_uri: str,
    request: cloud_speech.BatchRecognizeRequest,
    output_uri: str,
    billed_duration_seconds: int
) -> None:
    """
    Writes a file to local filesystem with the experiment details
    """
    output_file_name = os.path.join(
        EXPERIMENT_LOG_DIR,
        output_uri.split("/")[-1].replace(".json", ".txt"))
    with open(output_file_name, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "audio_uri": audio_uri,
            "request": cloud_speech.BatchRecognizeRequest.to_dict(request),
            "output_uri": output_uri,
            "billed_duration_seconds": billed_duration_seconds}, indent=4))


async def transcribe_two_channel(
    blob: storage.Blob,
    model: str = "latest_long"
) -> None:
    """
    Transcribes the audio file in the given blob. The audio file needs
    to have two channels, one channel per speaker.
    """
    config = create_two_channel_recognition_config(model)
    request = create_recognize_request(blob, config)
    client = SpeechAsyncClient()
    operation = await client.batch_recognize(request=request, timeout=300)
    response = await operation.result()
    response = cast(cloud_speech.BatchRecognizeResponse, response)
    for audio_uri, result in response.results.items():
        print("Error: ", result.error)
        print(audio_uri)
        print(result.uri)
        log_experiment_locally(
            audio_uri,
            request,
            result.uri,
            response.total_billed_duration.seconds,
        )


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
        await transcribe_two_channel(blob)
        break


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
