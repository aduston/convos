"""
Functions for transcribing single-channel audio using speech_v1. speech_v1
supports diarization.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import cast
from google.cloud import storage
from google.cloud.speech_v1 import SpeechAsyncClient
from google.cloud.speech_v1.types import cloud_speech

EXPERIMENT_LOG_DIR = "/Users/aduston/convo_experiments"


def create_recognition_config(model: str) -> cloud_speech.RecognitionConfig:
    diarization_config = cloud_speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=1,
        max_speaker_count=2
    )
    return cloud_speech.RecognitionConfig(
        language_code="en-US",
        profanity_filter=False,
        enable_automatic_punctuation=True,
        diarization_config=diarization_config,
        model=model,
        use_enhanced=True,
    )


def create_recognize_request(
    blob: storage.Blob,
    output_uri: str,
    config: cloud_speech.RecognitionConfig
) -> cloud_speech.LongRunningRecognizeRequest:
    return cloud_speech.LongRunningRecognizeRequest(
        config=config,
        audio=cloud_speech.RecognitionAudio(
            uri=f"gs://{blob.bucket.name}/{blob.name}"),
        output_config=cloud_speech.TranscriptOutputConfig(
            gcs_uri=output_uri,
        )
    )


def log_experiment_locally(
    audio_uri: str,
    request: cloud_speech.LongRunningRecognizeRequest,
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
            "request":
                cloud_speech.LongRunningRecognizeRequest.to_dict(request),
            "output_uri": output_uri,
            "billed_duration_seconds": billed_duration_seconds}, indent=4))


async def transcribe(
    blob: storage.Blob,
    output_uri: str,
    model: str = "latest_long"
) -> None:
    """
    Transcribes the audio file in the blob. If the audio file has
    two channels, using the transcribe_two_channel API instead.
    """
    config = create_recognition_config(model)
    request = create_recognize_request(blob, output_uri, config)
    client = SpeechAsyncClient()
    print("Sending request to the Google Speech-to-Text API")
    operation = await client.long_running_recognize(
        request=request,
        timeout=600
    )
    print("Waiting for operation to complete...")
    response = await operation.result(timeout=600)
    response = cast(cloud_speech.LongRunningRecognizeResponse, response)
    log_experiment_locally(
        f"gs://{blob.bucket.name}/{blob.name}",
        request,
        output_uri,
        response.total_billed_time.seconds
    )


async def test_main() -> None:
    storage_client = storage.Client()
    bucket = storage_client.bucket("psycho-convos")
    blob = bucket.blob("normalized/20230209_135719.wav")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_uri = f"gs://convo-transcriptions/20230209_135719_{timestamp}.wav"
    await transcribe(blob, output_uri, "video")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_main())
