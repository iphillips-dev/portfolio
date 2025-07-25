# %%
import json
import requests
import base64
from itertools import islice
import matplotlib as mp
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Any 
import pandas as pd
from requests.auth import HTTPBasicAuth

# %%
#Assigning a value to each one of these variables 
organization = '{organization}'
project = '{project_name}'
query_id = '{query_id}'
pat_token = "{pat_token}"

# %%
url = f'https://dev.azure.com/{organization}/{project}/_apis/wit/wiql/{query_id}?api-version=7.1'

# %%
response = requests.get(url, auth=HTTPBasicAuth('', pat_token))

# %%
requests

# %%
if response.status_code == 200:
    query_results = response.json()
    print(query_results)
else:
    print(f"Failed to fetch query results. Status code: {response.status_code}")
    print(response.text)

# %%
pd.json_normalize(query_results)
query_results['columns']

# %%
def extract_work_item_ids(query_results):
    work_item_ids = []
    work_items = query_results.get('workItems', [])
    for work_item in work_items:
        work_item_id = work_item.get('id')
        if work_item_id is not None:
            work_item_ids.append(work_item_id)
    return work_item_ids

# %%
work_item_ids = extract_work_item_ids(query_results)
print(work_item_ids)

# %%
batch_work_item_ids = work_item_ids

# %%
def batch_request(all_work_item_ids, batch_size=200):
    batch_url = 'https://dev.azure.com/{OrganizationName}/_apis/wit/workItemsBatch?api-version=7.1'
    batch_pat_token = '{batach_token}'
    encoded_pat = base64.b64encode(bytes(':'+ batch_pat_token, 'utf-8')).decode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + encoded_pat
    }

    def chunks(data, size):
        it = iter(data)
        for i in range(0, len(data), size):
            yield list(islice(it, size))

    batch_work_item_details = []

    for batch in chunks(all_work_item_ids, batch_size):
        body = {
            "ids": batch,
            "fields": [
                "System.Id", "System.WorkItemType", "System.Title", "System.AssignedTo", "System.State", "System.Tags","System.TeamProject", "Microsoft.VSTS.Scheduling.TargetDate",
                'Custom.EstimatedStartDate',"System.CreatedDate","Custom.WSJF",'Microsoft.VSTS.Scheduling.Effort','Microsoft.VSTS.Common.BusinessValue', "System.Description", "Custom.BusinessOutcomes", 
                "Custom.LeadingIndicators", "System.Description", "Custom.LeadingIndicators", "Custom.NonFunctionalRequirements", "Custom.Threshold",'Custom.ValueDriver'
            ]
        }
        response2 = requests.post(batch_url, headers=headers, data=json.dumps(body))

        if response2.status_code == 200:
            batch_work_item_details.extend(response2.json()['value'])
        else:
            response2.raise_for_status()

    return batch_work_item_details

# %%
result = batch_request(batch_work_item_ids)
html = json.dumps(result, indent=2)
print(html)

# %%
def remove_html_tags(text: str) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    clean_text = soup.get_text(separator=" ")
    return clean_text

def replace_unicode_chars(text: str) -> str:
    replacements = {
        '\u2013': '-',  # En dash
        '\u200b': '',  # Zero-width space
        '\u201c': '"',  # Left double quotation mark
        '\u201d': '"',  # Right double quotation mark
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def remove_extra_spaces(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()

def clean_text_in_keys(data: Dict[str, Any], keys_to_clean: List[str]) -> Dict[str, Any]:
    for k, v in data.items():
        if isinstance(v, str) and k in keys_to_clean:
            v = remove_html_tags(v)
            v = replace_unicode_chars(v)
            v = remove_extra_spaces(v)
            data[k] = v
        elif isinstance(v, dict):
            data[k] = clean_text_in_keys(v, keys_to_clean)
        elif isinstance(v, list):
            data[k] = [clean_text_in_keys(item, keys_to_clean) if isinstance(item, dict) else item for item in v]
    return data

html2 = json.loads(html)

keys_to_clean  = ["Custom.LeadingIndicators","Custom.BusinessOutcomes","System.Description","Custom.NonFunctionalRequirements"]

cleaned_data = [clean_text_in_keys(item, keys_to_clean) for item in html2]
print(json.dumps(cleaned_data, indent=2))

# %%
df = pd.json_normalize(cleaned_data)
az_df = pd.DataFrame(df)

# %%
az_df.columns = az_df.columns.str.replace('^fields.', '', regex=True)
az_df.columns = az_df.columns.str.replace('^System.', '', regex=True)
az_df.columns = az_df.columns.str.replace('^Microsoft.VSTS.Scheduling.', '', regex=True)
az_df.columns = az_df.columns.str.replace('^Custom', '', regex=True)
az_df.columns = az_df.columns.str.replace('^AssignedTo', '', regex=True)
az_df.columns = az_df.columns.str.replace('^\.', '', regex=True)
az_df.columns.to_list()

# %%
az_df = az_df.fillna('')

# %%
IT_BigRocks_df = az_df[[
'id',
 'Id',
 'TeamProject',
 'WorkItemType',
 'State',
 'displayName',
 '_links.avatar.href',
 'uniqueName',
 'imageUrl',
 'descriptor',
 'CreatedDate',
 'Title',
 'TargetDate',
 'Effort',
 'Microsoft.VSTS.Common.BusinessValue',
 'WSJF',
 'Description',
 'BusinessOutcomes',
 'LeadingIndicators',
 'NonFunctionalRequirements',
 'Tags',
 'EstimatedStartDate',
 'ValueDriver'
]]

# %%
IT_BigRocks_df = IT_BigRocks_df.drop(IT_BigRocks_df.columns[1], axis=1)

# %%
IT_BigRocks_df

# %%
IT_BigRocks_df.insert(len(IT_BigRocks_df.columns), "Organization", "{organization}")
IT_BigRocks_df.insert(len(IT_BigRocks_df.columns), "AzureDevRootUrl", "https://dev.azure.com/")

# %%
IT_BigRocks_df

# %%
IT_BigRocks_df.insert(len(IT_BigRocks_df.columns), "TeamProjectUrl", IT_BigRocks_df["TeamProject"])

# %%
IT_BigRocks_df

# %%
def replace_spaces_with_percent20(x):
    return x.replace(" ", "%20")

IT_BigRocks_df["TeamProjectUrl"] = IT_BigRocks_df["TeamProjectUrl"].apply(replace_spaces_with_percent20)

# %%
IT_BigRocks_df.insert(len(IT_BigRocks_df.columns), "WorkItemEditUrl","/_workitems/edit/")

# %%
IT_BigRocks_df = IT_BigRocks_df.reset_index(drop=True)
duplicate_columns = IT_BigRocks_df.columns.duplicated()
duplicate_columns

# %%
IT_BigRocks_df