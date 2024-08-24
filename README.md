# Summary

Saving particular conversations in searchable, analyzable text.

# audio_info_function details

Conversations have been saved in .mp3, .m4a, and .mp4 formats in a storage bucket. To obtain audio information, we run ffprobe through a Google Cloud function. To deploy:

```
cd audio_info_function
docker build -t audio_info_function .
gcloud functions deploy ffmpeg-function \
    --runtime "nodejs16" \
    --entry-point "main" \
    --trigger-http \
    --memory 128M \
    --source "audio_info_function:latest"
```

