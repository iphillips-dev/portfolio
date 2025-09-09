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
from datetime import datetime, timezone, date, timedelta

# %% [markdown]
# ### In the block below you are iterationg over all projects in ADO and pulling data on spikes, user stories, and enablers. This data will be used to determine the amount of time spent in each state.

# %%
import requests
import pandas as pd

# Define your variables
organization = ""
projects = [                      # All you projects go here
    "Customer", 
    "RetailSolutions", 
    "CustomerRevenue", 
]

personal_access_token = ''    #Enter you PAT

# Common query parameters
filter_criteria = (
    "(WorkItemType eq 'Spike' or "
    "WorkItemType eq 'User Story' or "
    "WorkItemType eq 'Enabler' or "
    "WorkItemType eq 'Epic' or "
    "WorkItemType eq 'Feature' or "
    "WorkItemType eq 'Portfolio Epic') and "
    "CreatedDate ge 2025-01-01T00:00:00.000-05:00 and "
    "StateChangeDate ne null"
)

column_selection = "Title, WorkItemId, State, WorkItemType, StateCategory, StoryPoints, CreatedDate, StateChangeDate"
top = 10000
max_records = 600250

# Placeholder for all data
all_data = []

# Initialize session
session = requests.Session()
session.auth = ('', personal_access_token)

# Iterate over each project
for project in projects:
    skip = 0
    base_url = f"https://analytics.dev.azure.com/{organization}/{project}/_odata/v3.0-preview/WorkItemRevisions"

    while True:
        odata_query = (f"{base_url}?$apply=filter({filter_criteria})&$select={column_selection}&$top={top}&$skip={skip}")

        try:
            response = session.get(odata_query, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Debug: print response status and current skip
            print(f"{project}: Fetched {len(data['value'])} records with skip={skip}")

            # Append the project name to each record.
            batch = [{**record, "ProjectName": project} for record in data['value']]

            # Check how many records can be added without exceeding the limit
            records_to_add = min(top, max_records - len(all_data))
            all_data.extend(batch[:records_to_add])

            if len(batch) < top:
                break

            skip += top

        except requests.exceptions.RequestException as e:
            print(f"An error occurred for project {project}: {e}")
            break

# Convert the accumulated data into a pandas DataFrame
work_item_revisions = pd.json_normalize(all_data)
df = pd.DataFrame(work_item_revisions)


