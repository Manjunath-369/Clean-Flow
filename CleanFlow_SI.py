#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
from pathlib import Path

# Importing Raw sheets as well Google sheet

df_smry_turbine_filter = pd.read_csv(r"C:\Users\manju\OneDrive\Documents\skyspecs_summary_export.csv")
df_img_turbine_filter = pd.read_csv(r"C:\Users\manju\OneDrive\Documents\skyspecs_blade_export.csv", dtype={"Inspection Date": str},low_memory=False)
df_dmg_turbine_filter = pd.read_csv(r"C:\Users\manju\OneDrive\Documents\anomaly_export_with_resource_names.csv",low_memory=False)
df_dwn_sum = pd.read_csv(r"C:\Users\manju\OneDrive\Documents\assign task automation texst case 1.csv")
df_site_map = pd.read_excel(r"C:\Users\manju\OneDrive\Documents\Consolidated Zeitview Site List (2).xlsx")
sheet_url = "https://docs.google.com/spreadsheets/d/1HpW2ggD9kxV9Ur3037mMpD-0f2GM7AFSTSuNVo2dEJY/export?format=csv&gid=0"
df_sheet = pd.read_csv(sheet_url)



# In[ ]:


# Setting up Inspection date universal

df_smry_turbine_filter["Inspection Date"] = pd.to_datetime(
    df_smry_turbine_filter["Inspection Date"],
    dayfirst=True,
    
)

df_img_turbine_filter["Inspection Date"] = pd.to_datetime(
    df_img_turbine_filter["Inspection Date"],
    format="%d-%m-%Y",
)

df_dmg_turbine_filter["Inspection Date"] = pd.to_datetime(
    df_dmg_turbine_filter["Inspection Date"],
    dayfirst=True,
)

df_sheet["Inspection Date"] = pd.to_datetime(df_sheet["Inspection Date"],format="%d-%m-%Y")
df_sheet = df_sheet[["Site", "Turbine","Inspection Date"]]



# In[ ]:


# Taking turbines from sheet and filtering in raw sheet and assigning to new variable

result_smry = df_smry_turbine_filter.merge(
    df_sheet,
    on=["Site", "Turbine","Inspection Date"],
    how="inner"
)


result_img = df_img_turbine_filter.merge(
    df_sheet,
    left_on=["Site Name", "WTG ID","Inspection Date"],
    right_on=["Site", "Turbine","Inspection Date"],
    how="inner"
)

result_img = result_img.drop(columns=["Site", "Turbine"])



result_dmg = df_dmg_turbine_filter.merge(
    df_sheet,
    left_on=["Site Name", "WTG #", "Inspection Date"],
    right_on=["Site", "Turbine", "Inspection Date"],
    how="inner"
)

result_dmg = result_dmg.drop(columns={"Site","Turbine","Unnamed: 31"},errors="ignore")

result_dmg["Inspection Date"] = result_dmg["Inspection Date"]




# In[ ]:


# Summary sheet creation according to our requirement..........V2 testing

df_raw_sum = result_smry.copy()
df_dwn_sum["number_ds"] = df_dwn_sum["Turbine"].str.extract(r'(\d+)').fillna(0).astype(int)
df_raw_sum["number_rs"] = df_raw_sum["Turbine"].str.extract(r'(\d+)').fillna(0).astype(int)

df_dwn_sum = df_dwn_sum.sort_values(by=["Site","number_ds"])
df_site_name = df_site_map.set_index("Site Name")["Horizon Site Name"]
df_raw_sum["Site"] = df_raw_sum["Site"].map(df_site_name)

df_dwn_sum = df_dwn_sum.rename(columns={"number_ds": "num"})
df_dwn_sum["Site_Num"] = df_dwn_sum["Site"].astype(str) + "_" + df_dwn_sum["num"].astype(str)
df_dwn_sum = df_dwn_sum.drop(columns="num")

df_raw_sum = df_raw_sum.sort_values(by=["Site","number_rs"])
df_raw_sum = df_raw_sum.rename(columns={"number_rs": "num"})
df_raw_sum["Site_Num"] = df_raw_sum["Site"].astype(str) + "_" + df_raw_sum["num"].astype(str)
df_raw_sum["Inspection Date"] = pd.to_datetime(df_raw_sum["Inspection Date"],dayfirst=True).dt.date
# df_raw_sum["Inspection Date"] = df_raw_sum["Inspection Date"].dt.strftime("%Y-%m-%d")
wtg_convert = df_dwn_sum.set_index("Site_Num")["Turbine"]
horizon_task_id = df_dwn_sum.set_index("Site_Num")["Horizon Task ID"]
df_raw_sum["Turbine"] = df_raw_sum["Site_Num"].map(wtg_convert)
df_raw_sum["Horizon Task ID"] = df_raw_sum["Site_Num"].map(horizon_task_id)
df_raw_sum = df_raw_sum.drop(columns=["num","Site_Num"])
df_raw_sum = df_raw_sum.reset_index(drop=True)



# In[ ]:


# Image sheet creation according to our requirement

df_img = result_img.copy()
df_img["number_rs"] = df_img["WTG ID"].str.extract(r'(\d+)').fillna(0).astype(int)
df_img = df_img.sort_values(by=["Site Name","number_rs"])
df_img = df_img.rename(columns={"number_rs": "num"})
df_img["Site Name"] = df_img["Site Name"].map(df_site_name)
df_img["Site_Num"] = df_img["Site Name"].astype(str) + "_" + df_img["num"].astype(str)
df_img["WTG ID"] = df_img["Site_Num"].map(wtg_convert)
df_img["Horizon Task ID"] = df_img["Site_Num"].map(horizon_task_id)
col = df_img.pop("Horizon Task ID")
df_img.insert(2,"Horizon Task ID",col)
df_img = df_img.drop(columns=["Site_Num","num","Inspection Date"])
df_img = df_img.reset_index(drop=True)


# In[ ]:


result_dmg = result_dmg.sort_values(by=["Site Name","WTG #"])


# In[ ]:


# Making csv sheet of summary,image and damage

turbine_first = df_raw_sum["Turbine"].iloc[0]
turbine_last = df_raw_sum["Turbine"].iloc[-1]

site_name_first = df_raw_sum["Site"].iloc[0]
site_name_last = df_raw_sum["Site"].iloc[-1]



folder_name = f"{site_name_first} {turbine_first} to {site_name_last} {turbine_last}"
desktop = Path(r"C:\Users\manju\OneDrive\Documents\Desktop\Skyspec")
output_folder = desktop / folder_name 

if output_folder.exists():
    print(f"Folder '{folder_name}' already exists, Delete that folder first")
else:
    output_folder.mkdir()
    print(f"Folder '{folder_name}' created successfully.")
df_raw_sum.to_csv(output_folder / "smry.csv", index=False)
df_img.to_csv(output_folder / "img.csv", index=False)
result_dmg.to_csv(output_folder / "dmg.csv", index=False)   

