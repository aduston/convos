#!/usr/bin/env python

import requests
import secrets
import urllib
import pprint

# Illustration of how I can't get the Watson Speech-to-Text
# register_callback call to work.

secrets.load_creds()

opts = {
    'callback_url': secrets.callback_url
}
url = "https://stream.watsonplatform.net/speech-to-text/api/v1/register_callback"
url = "{0}?{1}".format(url, urllib.urlencode(opts))

r = requests.post(
    url,
    auth=(secrets.watson_username, secrets.watson_password),
    data="{}")

print(r.status_code)
print(pprint.pformat(r.json()))

# This outputs:

# 400
# {u'code': 400,
#  u'code_description': u'Bad Request',
#  u'error': u"unable to verify callback url 'https://<redacted>.execute-api.us-east-1.amazonaws.com/prod/SpeechToTextCallback' , server responded with status code: 400"}

# and no http call is logged on the server. Note: the actual url does
# not contain "<redacted>"

r = requests.get(
    secrets.callback_url, params=dict(challenge_string="is this going to work?"))

print(r.status_code)
print(r.text)

# This outputs:

# 200
# "is this going to work?"

# and an HTTP GET is logged on the server.
