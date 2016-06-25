from watsoncreds import creds
import requests

url = "https://stream.watsonplatform.net/speech-to-text/api/v1/recognitions/{0}".format("b0f0c960-3ae9-11e6-b59c-dbb8860ad118")

r = requests.get(
    url,
    auth=(creds["username"], creds["password"]))

print r.text
