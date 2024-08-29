`audio_normalizer` is a tiny Flask-based web service that gets deployed as a Cloud Run service. Its job is to take input audio files in a bucket, obtain information on them using ffprobe, convert them to linear16 using ffmpeg, and then save both the information and converted audio to a target bucket.

To build locally, push, and deploy the service:

```
export IMAGE_URL=us-central1-docker.pkg.dev/aad-personal/dockers/audio_normalizer:latest
docker build . --platform linux/amd64 --tag $IMAGE_URL
docker push $IMAGE_URL
gcloud run deploy audio-normalizer --image $IMAGE_URL --region us-central1 --no-allow-unauthenticated --memory=1G
```



To call this, see normalize_all.py.