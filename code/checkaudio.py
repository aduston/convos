from watsoncreds import creds
import requests
import os

talkdir = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    '..', 'talk')

id_left = '4b992ab0-3af0-11e6-b59c-dbb8860ad118'
id_right = '54c668f0-3af0-11e6-b59c-dbb8860ad118'

id_left_new = '06676750-3af4-11e6-b59c-dbb8860ad118'
id_right_new = '0cdcd890-3af4-11e6-b59c-dbb8860ad118'

url = "https://stream.watsonplatform.net/speech-to-text/api/v1/recognitions/{0}".format(id_right)

r = requests.get(
    url,
    auth=(creds["username"], creds["password"]))

with open(os.path.join(talkdir, "right.txt"), "w") as f:
    f.write(r.text)
