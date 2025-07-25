# %%
import pandas as pd
from tableau_api_lib import TableauServerConnection 
from tableau_api_lib.utils import querying, flatten_dict_column

# %%
config = { 
          'tableau_prod': {
            'server':'{server}' ,
            'api_version' :'3.24',
            'personal_access_token_name': '{name}',
            'personal_access_token_secret': '{token_secret}',
            'username': '',
            'password': '<',
            'site_name': '{site_name}',
            'site_url': '{site_url}',
          }
}

# %%
connect = TableauServerConnection(config_json=config, env='tableau_prod')
response = connect.sign_in()
response

# %%
response.json()

# %%
connect.server_info().json()

# %%
workbooks_df = querying.get_workbooks_dataframe(connect)
workbooks_df

# %%
workbooks_df = querying.get_workbooks_dataframe(connect)
workbooks_df.astype({'id': 'string', 'name': 'string'})
workbooks_df.dtypes

# %%
workbooks_df_lmd = workbooks_df[workbooks_df['name'] == '{workbook_name}']
workbooks_df_lmd

# %%
workbooks_df_views = querying.get_views_for_workbook_dataframe(
    conn=connect, workbook_id=workbooks_df_lmd.get('id').to_list().pop()
)

workbooks_filtered = workbooks_df_views[workbooks_df_views['name'].str.contains('(W)')]
workbooks_filtered

# %%
workbooks_targeted = workbooks_filtered.drop([22, 24])
workbooks_targeted

# %%
workbook_name = "Amazon LMD: External Dashboard"

# %%
for index, row in workbooks_targeted.iterrows():
    if row["name"] != workbook_name:
        print(f"creating CSV file for view { row['name']}...")
        response = connect.query_view_data(view_id=row["id"])
        with open (f"{row['name']}.csv", "wb") as file:
            file.write(response.content)

# %%