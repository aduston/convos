#!/usr/bin/env python

import requests
import secrets
import urllib
import pprint

secrets.load()

r = requests.post(
    "https://stream.watsonplatform.net/speech-to-text/api/v1/register_callback?{0}".format(
        urllib.urlencode({ 'callback_url': secrets.callback_url })),
    auth=(secrets.watson_username, secrets.watson_password),
    data="{}")

print(r.status_code)
print(pprint.pformat(r.json()))
