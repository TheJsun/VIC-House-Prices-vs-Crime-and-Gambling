import pandas as pd
import numpy as np
import data
import math

emg = data.egm
communities = data.communities
houses_by_suburb = data.houses_by_suburb
lga_offences = data.lga_offences


suburbs = data.suburbs
communities_summary = data.communities_summary

houses_by_suburb["Locality"] = houses_by_suburb["Locality"].str.title().str.strip()
suburbs["Community Name"] = suburbs["Community Name"].str.title().str.strip()

# Houses by LGA
houses_by_lga = pd.DataFrame(columns=[
    "LGA",
    "Year",
    "Weighted House Price"
])

years = [
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "2018",
    "2019",
    "2020",
    "2021",
    "2022",
    "2023"
]


houses_by_suburb[years] = houses_by_suburb[years].astype(str)
houses_by_suburb.replace('-', np.nan, inplace=True)
houses_by_suburb[years] = houses_by_suburb[years].astype(float)


all_suburbs = [x for x in houses_by_suburb["Locality"]]

for year in years:
    for lga in suburbs["LGA"].unique():

        # lga_total_population, exclude the missing data suburb population
        lga_total_population = 0
        weighted_house_price = 0
        for s in suburbs[suburbs["LGA"] == lga]["Community Name"]: 
            if s in all_suburbs and not math.isnan(houses_by_suburb[houses_by_suburb["Locality"] == s][year].values[0]) :
                lga_total_population += suburbs[suburbs["Community Name"] == s]["Population"].values[0]

        for s in suburbs[suburbs["LGA"] == lga]["Community Name"]:
            if s in all_suburbs and not math.isnan(houses_by_suburb[houses_by_suburb["Locality"] == s][year].values[0]):
                weighted_house_price += suburbs[suburbs["Community Name"] == s]["Population"].values[0] / lga_total_population * houses_by_suburb[houses_by_suburb["Locality"] == s][year].values[0]

    
        houses_by_lga.loc[len(houses_by_lga)] = {
            "LGA" : lga,
            "Year" : year,
            "Weighted House Price" : round(weighted_house_price, 2),
        }


houses_by_lga.set_index(["LGA", "Year"], inplace=True)
houses_by_lga.to_csv("Houses by LGA.csv")


