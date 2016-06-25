from watsoncreds import creds
import urllib
import requests

url = "https://stream.watsonplatform.net/speech-to-text/api/v1/recognitions"
url = "{0}?{1}".format(
    url,
    urllib.urlencode(dict(
        continuous="true",
        inactivity_timeout="-1",
        timestamps="true",
        smart_formatting="true",
        profanity_filter="false"
    )))

r = requests.post(
    url,
    auth=(creds["username"], creds["password"]),
    headers={
        'Content-Type': 'audio/ogg;codecs=opus',
    },
    data=open("simpletest.ogg", "r"))

if r.status_code == 201:
    print r.json()
else:
    print r.status_code
    print r.text
