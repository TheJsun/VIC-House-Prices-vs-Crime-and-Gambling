import platform
import pandas as pd
import numpy as np

# Settings
pd.options.mode.copy_on_write = True

# Data file path
EGM_CSV_FILEPATH = ".\\Data\\EGM.csv" if platform.system() == "Windows" else "./Data/EGM.csv"
COMMUNITIES_CSV_FILEPATH = ".\\Data\\communities.csv" if platform.system() == "Windows" else "./Data/communities.csv"
HOUSES_BY_SUBURB_CSV_FILEPATH = ".\\Data\\Houses-by-suburb.csv" if platform.system() == "Windows" else "./Data/Houses-by-suburb.csv"
LGA_OFFENCES_FILEPATH = ".\\Data\\LGA Offences.xlsx" if platform.system() == "Windows" else "./Data/LGA Offences.xlsx"

# Dataframe from original data
egm = pd.read_csv(EGM_CSV_FILEPATH)
egm.rename(columns={"LGA Name": "LGA"}, inplace=True)
communities = pd.read_csv(COMMUNITIES_CSV_FILEPATH)
houses_by_suburb = pd.read_csv(HOUSES_BY_SUBURB_CSV_FILEPATH)
lga_offences = pd.read_excel(LGA_OFFENCES_FILEPATH, sheet_name="Table 02")


# General data

# Suburb with corresponding LGA
# Suburb names turn into capitalize
suburbs = communities.loc[communities["Community Name"].str.contains(r"\(Suburb\)$")][["Community Name", "LGA", "Population Density", "Area (km^2)"]]
suburbs["Community Name"] = suburbs["Community Name"].str.removesuffix("(Suburb)").str.strip()
suburbs["Population"] = suburbs["Population Density"]*suburbs["Area (km^2)"]

#standardises the format for lga's
suburbs["LGA"]=suburbs["LGA"].str.removesuffix("(RC)").str.strip()
suburbs["LGA"]=suburbs["LGA"].str.removesuffix("(C)").str.strip()
suburbs["LGA"]=suburbs["LGA"].str.removesuffix("(S)").str.strip()
suburbs["LGA"]=suburbs["LGA"].str.removesuffix("(B)").str.strip()

# communities_summary (short verison of communities)
communities_summary = communities[["Community Name", "LGA", "Population Density", "Area (km^2)"]]
communities_summary["Population"] = communities_summary["Population Density"] * communities_summary["Area (km^2)"]

# standardises the format for lga's
communities_summary["LGA"]=communities_summary["LGA"].str.removesuffix("(RC)").str.strip()
communities_summary["LGA"]=communities_summary["LGA"].str.removesuffix("(C)").str.strip()
communities_summary["LGA"]=communities_summary["LGA"].str.removesuffix("(S)").str.strip()
communities_summary["LGA"]=communities_summary["LGA"].str.removesuffix("(B)").str.strip()
