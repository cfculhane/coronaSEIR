import json

import requests

URL = "https://coronavirus-tracker-api.herokuapp.com/v2/locations"

raw_data = requests.get(URL)

data_json = json.loads(raw_data.text)
