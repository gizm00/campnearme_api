import pandas as pd
import json
from pandas.io.json import json_normalize
import requests


response = requests.get(url="http://api.campnear.me/GetFacilityNames")
try :
	data = json.loads(response.text)
	df = json_normalize(data['Items'])


except Exception as ex:
	print("RidbData.extract(): unable to read response")
	print(ex)

df.to_csv('test.csv', index=False)