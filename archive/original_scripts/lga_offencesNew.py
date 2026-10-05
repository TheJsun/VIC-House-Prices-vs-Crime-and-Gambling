import data
import pandas as pd

offencesByLGA = pd.DataFrame(columns=["LGA", "Year", "Type A Percentage", "Type B Percentage", "Type C Percentage", "Type D Percentage", "Type E Percentage", "Offence Rate"])
filteredOffencesData = data.lga_offences.loc[(data.lga_offences['Year'] >= 2016) & (data.lga_offences['Year'] <= 2020), ['Year', 'Local Government Area', 'Offence Subdivision', 'LGA Rate per 100,000 population', 'Offence Count']]
filteredOffencesData['Code'] = filteredOffencesData['Offence Subdivision'].str[:1]

#Dictionary for each offence division
codeType = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E': 0}
targetedYears = ['2016', '2017', '2018', '2019', '2020']
results = []

for year in targetedYears:
    #Calculating rate of offences and their type categorical distribution for each LGA
    for lga in filteredOffencesData['Local Government Area'].unique():
        currentYear = int(year)
        totalOffenceCount = filteredOffencesData[(filteredOffencesData['Year'] == currentYear)& (filteredOffencesData["Local Government Area"] == lga)]["Offence Count"].sum()
        
        lgaRateOffences = filteredOffencesData[(filteredOffencesData['Year'] == currentYear) & (filteredOffencesData['Local Government Area'] == lga)]['LGA Rate per 100,000 population'].sum()

        #Distribution for each type of offence
        for code in codeType:
            codeType[code] =  round(((filteredOffencesData[(filteredOffencesData['Year'] == currentYear)&(filteredOffencesData["Local Government Area"] == lga) & (filteredOffencesData["Code"] == code)]["Offence Count"].sum())/totalOffenceCount)*100,2)

        results.append({'LGA': lga, 'Year': year, 'Type A Percentage': codeType['A'], 'Type B Percentage': codeType['B'],'Type C Percentage': codeType['C'], 'Type D Percentage': codeType['D'],'Type E Percentage': codeType['E'],'Offence Rate': round(lgaRateOffences,2)})
    

offencesByLGA = pd.DataFrame(results)

# Set index to LGA
offencesByLGA.set_index("LGA", inplace=True)

print(offencesByLGA)

#Current problems are that all data across each year is the same.

#Output
offencesByLGA.to_csv("Offences By LGA NEW.csv")