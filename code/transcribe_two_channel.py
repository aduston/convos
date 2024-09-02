"""
Functions for transcribing two-channel audio files using speech_v2. speech_v2
doesn't support diarization, it seems. Since single-channel recordings require
diarization, use the v1 API for those.
"""

import asyncio
import json
import logging
import os
from typing import cast
from google.cloud import storage
from google.cloud.speech_v2 import SpeechAsyncClient
from google.cloud.speech_v2.types import cloud_speech

logger = logging.getLogger(__name__)
PROJECT_ID = "aad-personal"
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
    output_bucket_name: str,
    config: cloud_speech.RecognitionConfig
) -> cloud_speech.BatchRecognizeRequest:
    """
    Returns a BatchRecognizeRequest object with the given blob and config
    """
    blob_uri = f"gs://{blob.bucket.name}/{blob.name}"
    # FIXME
    print(blob_uri)
    print(blob.exists())
    file_metadata = cloud_speech.BatchRecognizeFileMetadata(uri=blob_uri)
    return cloud_speech.BatchRecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
        config=config,
        files=[file_metadata],
        recognition_output_config=cloud_speech.RecognitionOutputConfig(
            gcs_output_config=cloud_speech.GcsOutputConfig(
                uri=f"gs://{output_bucket_name}/transcript_test/"
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


async def transcribe(
    blob: storage.Blob,
    output_bucket_name: str,
    model: str = "latest_long"
) -> None:
    """
    Transcribes the audio file in the given blob. The audio file needs
    to have two channels, one channel per speaker.
    """
    config = create_two_channel_recognition_config(model)
    request = create_recognize_request(blob, output_bucket_name, config)
    client = SpeechAsyncClient()
    logger.info("Sending request to the Google Speech-to-Text API")
    operation = await client.batch_recognize(request=request, timeout=300)
    logger.info("Waiting for response")
    response = await operation.result(timeout=300)
    response = cast(cloud_speech.BatchRecognizeResponse, response)
    for audio_uri, result in response.results.items():
        log_experiment_locally(
            audio_uri,
            request,
            result.uri,
            response.total_billed_duration.seconds,
        )


async def test_main() -> None:
    storage_client = storage.Client()
    bucket = storage_client.bucket("psycho-convos")
    blob = bucket.blob("normalized/20230209_135719.wav")
    output_bucket_name = "convo-transcriptions"
    await transcribe(blob, output_bucket_name)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_main())
