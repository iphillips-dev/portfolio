# %%
import json
import pandas as pd
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth

# %%

url = '{url}'
headers = {
    "Authorization": "{bearer_token}"
}

# %%
response = requests.get(url, headers=headers) 

if response.status_code == 200:      
   
    refresh_history = response.json()   
    print(refresh_history)    
else:
    print(f"Failed to retrieve refresh history. Status code: {response.status_code}, Response: {response.text}")  

# %%
load_json = pd.json_normalize(refresh_history['value'])
load_json
