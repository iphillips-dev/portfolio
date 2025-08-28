## packages you need to install
pip install numpy pandas
pip install office365-rest-python-client
pip install numpy pandas office365-rest-python-client



## packeges you need to import
import numpy as np
import pandas as pd
from datetime import datetime, timezone 
import sys
import io
from io import BytesIO
import os
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.listitems.caml.query import CamlQuery
from office365.sharepoint.files.file import File
from office365.graph_client import GraphClient


### information for authentication -- my org didn't allow basic (username,password) so they had to register an app in azure and provide me with the credetials.

site_url = 'ROOT SHAREPOINT URL'                                        {entry required}
client_secret = 'CLIENT SECRET FROM APP THAT WAS REGISTERED'            {entry required}
client_id = 'ADD CLIENT ID'                                             {entry required}

### grabbing file from sharepont

ctx = ClientContext(site_url).with_credentials(ClientCredential(client_id, client_secret))
relative_url = 'add you file url --> open the file from sharepoint in desktop --> go to the info tab copy the url --> put it in here delete the last part (web?) the last part should be the file type xlsx '

response = File.open_binary(ctx, relative_url)

#save data to BytesIO stream
bytes_file_obj = io.BytesIO()
bytes_file_obj.write(response.content)
bytes_file_obj.seek(0) #set file object to start

#read file into pandas dataframe
df = pd.read_excel(bytes_file_obj,sheet_name='2026 Detail Consol.') 

'''
DO ANY DATA PREPERATION YOU NEED BEFORE WRITING IT TO SHAREPOINT

''' 


### Writing your file to the sharepoint page

try:
    file_name = 'NAME OF YOUR FILE'                        {entry required}
    local_path = os.path.join(os.getcwd(), file_name)      {entry required}
    PUT YOUR DATAFRAME HERE.to_csv(local_path, index=False)   {entry required}
    

    sharepoint_folder_name = 'Shared Documents/SUBFOLDER/FOLDER'            {entry required}
    now_utc = datetime.now(timezone.utc).strftime("%m/%d/%Y %H:%M:%S UTC")
 
    credentials = ClientCredential(client_id, client_secret)
    ctx = ClientContext(site_url).with_credentials(credentials)
    
    target_folder = ctx.web.get_folder_by_server_relative_url(sharepoint_folder_name)
 
    with open(local_path, 'rb') as f:
        file_name = os.path.basename(local_path)
        uploaded_file = target_folder.upload_file(file_name, f.read())
        ctx.execute_query()
        
        print(f"File '{file_name}' uploaded successfully to '{sharepoint_folder_name}'published at '{now_utc}'")

except Exception as e:
    print(f"Error uploading file: {e}")
