import pandas as pd
import numpy as np
import data
egm = data.egm
communities_summary = data.communities_summary

#generates a new dataframe of lga's and population
lgas = pd.DataFrame(columns=["LGA", "Population"])
for lga in communities_summary["LGA"].unique():
    lga_total_population = communities_summary[communities_summary["LGA"] == lga]["Population"].sum()
    lgas=lgas._append({"LGA":lga, "Population": lga_total_population}, ignore_index=True)


egm2016_2020 = egm.loc[:56][["LGA", "2019","2018","2017","2016", "2020"]]

def seperatedatayears(jointcommunityname, communityname, totalpopulation):
    Years=["2019","2018","2017","2016", "2020"]
    community = []
    for column in Years:
        community.append((egm2016_2020.loc[egm2016_2020["LGA"] == jointcommunityname][column].values[0])*(lgas.loc[lgas["LGA"] == communityname]["Population"].values[0])/(totalpopulation))
    return community


#seperated all the data with combined LGA's
sum_whittlesea = lgas.loc[lgas["LGA"] == "Whittlesea"]["Population"].values[0]+lgas.loc[lgas["LGA"] == "Nillumbik"]["Population"].values[0]
whittlesea = seperatedatayears("CITY OF WHITTLESEA", "Whittlesea", sum_whittlesea)
egm2016_2020= egm2016_2020._append({"LGA": "Whittlesea", "2019": round(whittlesea[0],2), "2018": round(whittlesea[1],2), "2017":round(whittlesea[2],2), "2016":round(whittlesea[3],2), "2020":round(whittlesea[4],2)},ignore_index=True)
Nillumbik = seperatedatayears("CITY OF WHITTLESEA", "Nillumbik", sum_whittlesea)
egm2016_2020= egm2016_2020._append({"LGA": "Nillumbik", "2019": round(Nillumbik[0],2), "2018": round(Nillumbik[1],2), "2017":round(Nillumbik[2],2), "2016":round(Nillumbik[3],2),"2020":round(Nillumbik[4],2)},ignore_index=True)

sum_Grampians = lgas.loc[lgas["LGA"] == "Ararat"]["Population"].values[0]+lgas.loc[lgas["LGA"] == "Northern Grampians"]["Population"].values[0]
ararat = seperatedatayears("SHIRE OF NORTHERN GRAMPIANS", "Ararat", sum_Grampians)
egm2016_2020= egm2016_2020._append({"LGA": "Ararat", "2019": round(ararat[0],2), "2018" : round(ararat[1],2),"2017":round(ararat[2],2),"2016":round(ararat[3],2), "2020":round(ararat[4],2)},ignore_index=True)
northern_gramps = seperatedatayears("SHIRE OF NORTHERN GRAMPIANS", "Northern Grampians", sum_Grampians)
egm2016_2020= egm2016_2020._append({"LGA": "Northern Grampians", "2019":round(northern_gramps[0],2),"2018":round(northern_gramps[1],2),"2017":round(northern_gramps[2],2), "2016":round(northern_gramps[3],2), "2020":round(northern_gramps[4],2)},ignore_index=True)

sum_Grt_Geelong = lgas.loc[lgas["LGA"] == "Queenscliffe"]["Population"].values[0]+lgas.loc[lgas["LGA"] == "Greater Geelong"]["Population"].values[0]
queenscliffe = seperatedatayears("CITY OF GREATER GEELONG", "Queenscliffe", sum_Grt_Geelong)
egm2016_2020= egm2016_2020._append({"LGA": "Queenscliffe", "2019":round(queenscliffe[0],2),"2018":round(queenscliffe[1],2),"2017":round(queenscliffe[2],2),"2016":round(queenscliffe[3],2), "2020":round(queenscliffe[4],2)},ignore_index=True)
greater_geelong = seperatedatayears("CITY OF GREATER GEELONG", "Greater Geelong", sum_Grt_Geelong)
egm2016_2020= egm2016_2020._append({"LGA": "Greater Geelong", "2019":round(greater_geelong[0],2),"2018":round(greater_geelong[1],2),"2017":round(greater_geelong[2],2),"2016":round(greater_geelong[3],2),"2020":round(greater_geelong[4],2)},ignore_index=True)

sum_Colac = lgas.loc[lgas["LGA"]=="Corangamite"]["Population"].values[0]+lgas.loc[lgas["LGA"]=="Colac-Otway"]["Population"].values[0]
Corangamite = seperatedatayears("SHIRE OF COLAC-OTWAY", "Corangamite", sum_Colac)
egm2016_2020= egm2016_2020._append({"LGA": "Corangamite", "2019":round(Corangamite[0],2), "2018":round(Corangamite[1],2), "2017":round(Corangamite[2],2), "2016":round(Corangamite[3],2), "2020":round(Corangamite[4],2)},ignore_index=True)
Colac_Otway = seperatedatayears("SHIRE OF COLAC-OTWAY", "Colac-Otway", sum_Colac)
egm2016_2020= egm2016_2020._append({"LGA": "Colac-Otway", "2019":round(Colac_Otway[0],2), "2018":round(Colac_Otway[1],2), "2017":round(Colac_Otway[2],2), "2016":round(Colac_Otway[3],2), "2020":round(Colac_Otway[4],2)},ignore_index=True)

sum_Moorabool = lgas.loc[lgas["LGA"]=="Hepburn"]["Population"].values[0]+lgas.loc[lgas["LGA"]=="Moorabool"]["Population"].values[0]
Hepburn = seperatedatayears("SHIRE OF MOORABOOL", "Hepburn", sum_Moorabool)
egm2016_2020= egm2016_2020._append({"LGA" : "Hepburn", "2019":round(Hepburn[0],2), "2018":round(Hepburn[1],2), "2017":round(Hepburn[2],2), "2016":round(Hepburn[3],2), "2020":round(Hepburn[4],2)},ignore_index=True)
Moorabool = seperatedatayears("SHIRE OF MOORABOOL", "Moorabool", sum_Moorabool)
egm2016_2020= egm2016_2020._append({"LGA": "Moorabool", "2019":round(Moorabool[0],2), "2018":round(Moorabool[1],2), "2017":round(Moorabool[2],2), "2016":round(Moorabool[3],2), "2020":round(Moorabool[4],2)},ignore_index=True)

sum_Goldfields = lgas.loc[lgas["LGA"] =="Central Goldfields"]["Population"].values[0]+lgas.loc[lgas["LGA"] =="Mount Alexander"]["Population"].values[0]
CentralGoldfields = seperatedatayears("SHIRE OF CENTRAL GOLDFIELDS", "Central Goldfields", sum_Goldfields)
egm2016_2020= egm2016_2020._append({"LGA": "Central Goldfields", "2019":round(CentralGoldfields[0],2),"2018":round(CentralGoldfields[1],2),"2017":round(CentralGoldfields[2],2),"2016":round(CentralGoldfields[3],2), "2020":round(CentralGoldfields[4],2)},ignore_index=True)
MountAlexander = seperatedatayears("SHIRE OF CENTRAL GOLDFIELDS", "Mount Alexander", sum_Goldfields)
egm2016_2020= egm2016_2020._append({"LGA": "Mount Alexander", "2019":round(MountAlexander[0],2),"2018":round(MountAlexander[1],2),"2017":round(MountAlexander[2],2), "2016":round(MountAlexander[3],2), "2020":round(MountAlexander[4],2)},ignore_index=True)

sum_Mitchell = lgas.loc[lgas["LGA"]=="Mansfield"]["Population"].values[0]+lgas.loc[lgas["LGA"]=="Murrindindi"]["Population"].values[0]+lgas.loc[lgas["LGA"]=="Mitchell"]["Population"].values[0]
Mansfield = seperatedatayears("SHIRE OF MITCHELL", "Mansfield", sum_Mitchell)
egm2016_2020= egm2016_2020._append({"LGA": "Mansfield", "2019":round(Mansfield[0],2),"2018":round(Mansfield[1],2),"2017":round(Mansfield[2],2),"2016":round(Mansfield[3],2), "2020":round(Mansfield[4],2)},ignore_index=True)
Murrindindi = seperatedatayears("SHIRE OF MITCHELL", "Murrindindi", sum_Mitchell)
egm2016_2020= egm2016_2020._append({"LGA": "Murrindindi", "2019":round(Murrindindi[0],2),"2018":round(Murrindindi[1],2),"2017":round(Murrindindi[2],2),"2016":round(Murrindindi[3],2),"2020":round(Murrindindi[4],2)},ignore_index=True)
Mitchell = seperatedatayears("SHIRE OF MITCHELL", "Mitchell", sum_Mitchell)
egm2016_2020= egm2016_2020._append({"LGA": "Mitchell", "2019":round(Mitchell[0],2),"2018":round(Mitchell[1],2),"2017":round(Mitchell[2],2),"2016":round(Mitchell[3],2),"2020":round(Mitchell[4],2)},ignore_index=True)

sum_Alpine = lgas.loc[lgas["LGA"] == "Towong"]["Population"].values[0]+lgas.loc[lgas["LGA"] == "Alpine"]["Population"].values[0]
Towong = seperatedatayears("SHIRE OF ALPINE", "Towong", sum_Alpine)
egm2016_2020= egm2016_2020._append({"LGA": "Towong", "2019":round(Towong[0],2),"2018":round(Towong[1],2),"2017":round(Towong[2],2),"2016":round(Towong[3],2),"2020":round(Towong[4],2)},ignore_index=True)
Alpine = seperatedatayears("SHIRE OF ALPINE", "Alpine", sum_Alpine)
egm2016_2020= egm2016_2020._append({"LGA": "Alpine", "2019":round(Alpine[0],2),"2018":round(Alpine[1],2),"2017":round(Alpine[2],2),"2016":round(Alpine[3],2),"2020":round(Alpine[4],2)},ignore_index=True)

sum_Benalla = lgas.loc[lgas["LGA"]=="Moira"]["Population"].values[0]+lgas.loc[lgas["LGA"]=="Strathbogie"]["Population"].values[0]+lgas.loc[lgas["LGA"]=="Benalla"]["Population"].values[0]
Moira = seperatedatayears("RURAL CITY OF BENALLA", "Moira", sum_Benalla)
egm2016_2020= egm2016_2020._append({"LGA": "Moira", "2019":round(Moira[0],2),"2018":round(Moira[1],2),"2017":round(Moira[2],2),"2016":round(Moira[3],2), "2020":round(Moira[4],2)},ignore_index=True)
Strathbogie = seperatedatayears("RURAL CITY OF BENALLA", "Strathbogie", sum_Benalla)
egm2016_2020= egm2016_2020._append({"LGA": "Strathbogie", "2019":round(Strathbogie[0],2),"2018":round(Strathbogie[1],2),"2017":round(Strathbogie[2],2),"2016":round(Strathbogie[3],2),"2020":round(Strathbogie[4],2)},ignore_index=True)
Benalla = seperatedatayears("RURAL CITY OF BENALLA", "Benalla", sum_Benalla)
egm2016_2020= egm2016_2020._append({"LGA": "Benalla", "2019":round(Benalla[0],2),"2018":round(Benalla[1],2),"2017":round(Benalla[2],2),"2016":round(Benalla[3],2),"2020":round(Benalla[4],2)},ignore_index=True)

sum_Campaspe = lgas.loc[lgas["LGA"] =="Campaspe"]["Population"].values[0]+lgas.loc[lgas["LGA"] =="Gannawarra"]["Population"].values[0]
Gannawarra = seperatedatayears("SHIRE OF CAMPASPE", "Gannawarra", sum_Campaspe)
egm2016_2020= egm2016_2020._append({"LGA": "Gannawarra", "2019":round(Gannawarra[0],2),"2018":round(Gannawarra[1],2),"2017":round(Gannawarra[2],2),"2016":round(Gannawarra[3],2),"2020":round(Gannawarra[4],2)},ignore_index=True)
Campaspe = seperatedatayears("SHIRE OF CAMPASPE", "Campaspe", sum_Campaspe)
egm2016_2020= egm2016_2020._append({"LGA": "Campaspe", "2019":round(Campaspe[0],2),"2018":round(Campaspe[1],2),"2017":round(Campaspe[2],2),"2016":round(Campaspe[3],2), "2020":round(Campaspe[4],2)},ignore_index=True)

sum_Glenelg = lgas.loc[lgas["LGA"] == "Glenelg"]["Population"].values[0]+lgas.loc[lgas["LGA"] == "Southern Grampians"]["Population"].values[0]
Glenelg = seperatedatayears("SHIRE OF GLENELG", "Glenelg", sum_Glenelg)
egm2016_2020= egm2016_2020._append({"LGA": "Glenelg","2019":round(Glenelg[0],2),"2018":round(Glenelg[1],2),"2017":round(Glenelg[2],2),"2016":round(Glenelg[3],2), "2020":round(Glenelg[4],2)},ignore_index=True)
Grampians = seperatedatayears("SHIRE OF GLENELG", "Southern Grampians", sum_Glenelg)
egm2016_2020= egm2016_2020._append({"LGA": "Southern Grampians", "2019":round(Grampians[0],2),"2018":round(Grampians[1],2),"2017":round(Grampians[2],2),"2016":round(Grampians[3],2),"2020":round(Grampians[4],2)},ignore_index=True)

egm2016_2020 = egm2016_2020.loc[11:]
egm2016_2020["LGA"] = egm2016_2020["LGA"].str.removeprefix("Shire of").str.strip()
egm2016_2020["LGA"] = egm2016_2020["LGA"].str.removeprefix("Rural City of").str.strip()
egm2016_2020["LGA"] = egm2016_2020["LGA"].str.removeprefix("City of").str.strip()
for curlga in egm2016_2020["LGA"].unique():
    egm2016_2020.loc[egm2016_2020["LGA"] == curlga, "rate 2020"] = round(egm2016_2020.loc[egm2016_2020["LGA"] == curlga]["2020"].values[0]/lgas.loc[lgas["LGA"]==curlga]["Population"].values[0],2)
    egm2016_2020.loc[egm2016_2020["LGA"] == curlga, "rate 2019"] = round(egm2016_2020.loc[egm2016_2020["LGA"] == curlga]["2019"].values[0]/lgas.loc[lgas["LGA"]==curlga]["Population"].values[0],2)
    egm2016_2020.loc[egm2016_2020["LGA"] == curlga, "rate 2018"] = round(egm2016_2020.loc[egm2016_2020["LGA"] == curlga]["2018"].values[0]/lgas.loc[lgas["LGA"]==curlga]["Population"].values[0],2)
    egm2016_2020.loc[egm2016_2020["LGA"] == curlga, "rate 2017"] = round(egm2016_2020.loc[egm2016_2020["LGA"] == curlga]["2017"].values[0]/lgas.loc[lgas["LGA"]==curlga]["Population"].values[0],2)
    egm2016_2020.loc[egm2016_2020["LGA"] == curlga, "rate 2016"] = round(egm2016_2020.loc[egm2016_2020["LGA"] == curlga]["2016"].values[0]/lgas.loc[lgas["LGA"]==curlga]["Population"].values[0],2)


# Set index to LGA
egm2016_2020.set_index("LGA", inplace=True)
egm2016_2020.to_csv("EGM-rate-2019.csv")