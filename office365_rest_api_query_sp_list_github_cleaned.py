# %%
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.listitems.caml.query import CamlQuery

# %%
import pandas as pd

# %%
site_url = '{site_url}'
client_secret = '{client_secret}'
client_id = '{client_id}'

# %%
try:
    ctx = ClientContext(site_url).with_credentials(ClientCredential(client_id, client_secret))
    target_list = "Applications"
    sp_list = ctx.web.lists.get_by_title(target_list)

    items = sp_list.items.select([
        "Title",   
        "TIMEChoice",
        "OperationalStatusChoice",
        "field_11", 
        "field_12", 
        "field_13",
        "field_15",
        "field_14",
        "BusinessCriticalityChoice",
        "EmergencyTierchoice",
        "ITOwnerlookup/Title",
        "BusinessOwnerlookup/Title",
        "Supportgrouplookup/Title",
        "Portfoliolookup/Title"
    ]).expand(["Portfoliolookup", "Supportgrouplookup", "ITOwnerlookup", "BusinessOwnerlookup"])
    ctx.load(items)
    ctx.execute_query()

    data = []
    for item in items:
        data.append(item.properties)

    applications_df = pd.DataFrame(data)

except Exception as e:
    print(f"Error: {e}")

applications_df.rename(columns={
    "Portfoliolookup": "Portfolio",
    "ITOwnerlookup": "IT Owner",
    "field_11": "Business Process",
    "field_12": "Description",
    "field_13": "Active User Count",
    "field_15": "Environment",
    "OperationalStatusChoice": "Operational Status",
    "Supportgrouplookup": "Support Group",
    "BusinessOwnerlookup": "Business Owner",
    "TIMEChoice": "TIME",
    "field_14": "End of Support/life",
    "EmergencyTierchoice": "Emergency Tier",
    "BusinessCriticalityChoice": "Business Criticality"
})

# %%
applications_df.info()

# %%
