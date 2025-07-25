# %%
import requests
from requests.auth import HTTPBasicAuth
import json
import pandas as pd

# %%
PAT = '{dynatrace_pat}'

# %%
url = '{url}'
headers = {
    'Authorization': '{api_token}'
}

# %%
response = requests.get(url,headers=headers)
response

# %%
if response.status_code == 200:
    response_data = response.json()  
else:
    print(f"Failed to retrieve data: {response.status_code}")
    print(f"Response: {response.text}")
print(json.dumps(response_data))

# %%
response_data

# %%
json = pd.json_normalize(response_data)
json.head(5)





