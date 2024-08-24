import asyncio
import os
from enum import Enum
from dataclasses import dataclass
from google.cloud import storage
from google.cloud import speech_v1 as speech
from google.cloud import mediatranscoder_v1 as mediatranscoder
from typing import cast
from urllib.parse import urlparse

PROJECT_ID = "aad-personal"
BUCKET_NAME = "psycho-convos"

class Speaker(Enum):
    ONE = 1
    TWO = 2

@dataclass
class Utterance:
    time_ms: int
    speaker: Speaker
    speech: str

@dataclass
class InputRecording:
    # The Google Storage uri of the input file
    uri: str

    @property
    def file_name(self):
        return self.uri.split("/")[-1]
    
    

async def transcode_mp4(video_file_uri: str, output_bucket: str, is_stereo: bool) -> None:
    video_file_name = video_file_uri.split("/")[-1]
    name, ext = os.path.splitext(video_file_name)
    output_uri = f"gs://{output_bucket}/{name}.wav"


async def transcode_m4a(video_file_name: str) -> None:
    input_uri = ""

async def create_transcription_mp3(audio_file_name: str, speech_client: speech.SpeechAsyncClient) -> list[Utterance]:
    storage_uri = f"gs://{BUCKET_NAME}/{audio_file_name}"
    audio = speech.RecognitionAudio(uri=storage_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3
    )


async def create_transcription_mp4(video_file_name: str, speech_client: speech.SpeechAsyncClient) -> list[Utterance]:
    return []


async def main() -> None:
    storage_client = storage.Client()
    speech_client = speech.SpeechClient()
    bucket = storage_client.bucket(BUCKET_NAME)
    for raw_blob in bucket.list_blobs():
        blob = cast(storage.Blob, raw_blob)
        if blob.name.endswith("mp3"):
            transcription = await create_transcription_mp3(blob.name, speech_client)
        elif blob.name.endswith("mp4"):
            transcription = await create_transcription_mp4(blob.name, speech_client)
        else:
            raise Exception(f"don't know what to do with {blob.name}")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())