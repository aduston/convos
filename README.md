# Summary

Saving particular conversations in searchable, analyzable text.

# Data Model

Conversations are modeled as Sessions that involve two speakers. Each Session has a start time and is uniquely identified by its timestamp. Data that gets stored for each session:

* Record in Dynamo. We use timestamp as a key, no range. For now the record includes the start time and duration, but will likely include other properties in the future.
* Raw Audio file in S3. We store two audio files, one in MP3 format and another in Ogg format using the Opus codec. Duplicated in Google Drive.
* Transcript in JSON in S3. Format of this file described in greater detail below.
* Nicely-formatted transcript in S3 and Google Drive.

# Data Flow

After recording an mp3, a script (`runlocal.py`) is run locally to upload the file to S3 using an S3 account that is allowed only to write.

Once the file is uploaded to S3, the `AudioUploadResponder` Lambda function (`audio_upload_responder.py`) runs, which:

1. Converts mp3 to two-channel Ogg with Opus codec using ffmpeg.
2. Call the Speech-to-Text Service (currently using Watson), passing the `SpeechToTextCallback` Lambda endpoint as a callback.
3. Insert record into DynamoDB. This record contains the job ID from Watson.
4. Saves raw audio to Google Drive.

The `SpeechToTextCallback` Lambda function is executed by the callback.

1. When AWS Lambda executes, check the "finished" state of the Dynamo DB record. If finished, exit. If not, proceed.
2. In AWS Lambda execution, create JSON transcript and nicely-formatted transcript. Add these to S3 and Google Drive.
3. Mark DynamoDB record as finished.

