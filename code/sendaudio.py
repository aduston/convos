from watsoncreds import creds
import urllib
import requests
import os

talkdir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '..', 'talk')

url = "https://stream.watsonplatform.net/speech-to-text/api/v1/recognitions"
url = "{0}?{1}".format(
    url,
    urllib.urlencode(dict(
        continuous="true",
        inactivity_timeout="-1",
        timestamps="true",
        smart_formatting="false",
        profanity_filter="false"
    )))

r = requests.post(
    url,
    auth=(creds["username"], creds["password"]),
    headers={
        'Content-Type': 'audio/ogg;codecs=opus',
    },
    data=open(os.path.join(talkdir, "right.ogg"), "r"))

if r.status_code == 201:
    print r.json()
else:
    print r.status_code
    print r.text
