import pandas as pd
import numpy as np

egm_rate_2019_df = pd.read_csv('EGM-rate-2019.csv')
egm_data=[]
for ids, data in egm_rate_2019_df.iterrows():
    egm_data.append([data["LGA"], 2019, data["2019"], data["rate 2019"]])
    egm_data.append([data["LGA"], 2018, data["2018"], data["rate 2018"]])
    egm_data.append([data["LGA"], 2017, data["2017"], data["rate 2017"]])
    egm_data.append([data["LGA"], 2016, data["2016"], data["rate 2016"]])
    egm_data.append([data["LGA"], 2020, data["2020"], data["rate 2020"]])

new_format_DF = pd.DataFrame(data=egm_data, columns=["LGA","Year","total dollars","rate"])
new_format_DF.set_index("LGA", inplace=True)
new_format_DF.to_csv("EGM-New-Format.csv")