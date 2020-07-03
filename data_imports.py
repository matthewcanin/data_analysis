'''
Imports and cleans datasets to be used for visualizations.
Datasets:
1) Geospatial map of counties
2) Census information
3) Cases
4) Deaths
'''

import geopandas as gpd
import pandas as pd
# from matplotlib import pyplot as plt


def geo_organized(file_name):
    '''
    This function organizes an inputed geospacial file.
    Returning a dataset that only contains data for the
    continental United States.
    '''
    geodataframe = gpd.read_file(file_name)
    geodataframe['STATEFP'] = geodataframe["STATEFP"].astype(int)
    # excluded_terr is all ids not in the continental US
    excluded_terr = [2, 81, 60, 3, 7, 64, 14, 66, 15, 86, 67, 89, 68, 71, 76,
                     69, 70, 95, 43, 72, 74, 52, 78, 79]
    excluded_columns = ['STATEFP', 'COUNTYFP', 'COUNTYNS', 'NAME', 'NAMELSAD',
                        'INTPTLAT', 'INTPTLON', 'geometry']

    # Remove the ids in excluded_terr from the dataframe
    geodataframe = geodataframe[~geodataframe.STATEFP.isin(excluded_terr)]

    # Extracts the wanted columns in excluded_columns from the dataframe
    geodataframe = geodataframe[excluded_columns]

    # Geospacial data testing
    # print(geodataframe.head())
    # geodataframe.plot()
    # plt.savefig("test.png")

    return geodataframe


def census_organized(file_name):
    '''
    This function reads in the census data and organizes it
    to remove unneeded columns and rows.
    '''
    census_data = pd.read_csv(file_name, encoding='cp437')
    included_columns = ['STNAME', 'CTYNAME', 'POPESTIMATE2019', 'NPOPCHG_2019',
                        'BIRTHS2019', 'DEATHS2019', 'NATURALINC2019',
                        'INTERNATIONALMIG2019', 'DOMESTICMIG2019',
                        'NETMIG2019', "STATE"]

    census_data = census_data[included_columns]

    # print(census_data.head())

    return census_data


def data_merge(geo_data, census_data, cases_data, deaths_data):
    '''
    This function merges all the datasets used in the program
    into one dataset.
    '''
    # Most Recent Date needs to be updated if file is updated
    newest_date = '6/2/2020'
    death_date = newest_date[0:6]
    # import the two Corona Virus Datafiles
    cases_formatted = cases_data.loc[:, ["Province_State", "Admin2",
                                     newest_date]]

    deaths_formatted = deaths_data.loc[:, ["Province_State", "Admin2",
                                           death_date]]
    # Merge the Data files
    # Corona Virus files Merged
    cases_deaths_merged = cases_formatted.merge(deaths_formatted,
                                                left_on=["Admin2",
                                                         'Province_State'],
                                                right_on=["Admin2",
                                                          'Province_State'],
                                                how='left')

    cases_deaths_merged.rename(columns={newest_date: 'Cases',
                                        death_date: "Deaths"},
                               inplace=True)

    merged = geo_data.merge(census_data, left_on=['NAMELSAD', "STATEFP"],
                            right_on=['CTYNAME', 'STATE'], how='left')

    merged = merged.merge(cases_deaths_merged, left_on=["NAME", 'STNAME'],
                          right_on=["Admin2", 'Province_State'], how="left")

    # print(merged.loc[(merged["NAME"] == 'Lincoln') &
    #                  (merged["STATEFP"] == 56)])
    # merged.plot()
    # plt.savefig("test.png")

    return merged


def get_cases(kind):
    '''
    This function takes a string with the type of
    cases (Cases or Deaths) desired and imports the
    relevant data and organizes it to remove
    unneeded rows.
    '''
    # Imports file
    if kind == "Cases":
        file_name = "Project datasets/Cases.csv"
    elif kind == "Deaths":
        file_name = "Project datasets/Deaths.csv"

    data = pd.read_csv(file_name, encoding='cp437')

    # excluded_terr is all ids not in the continental US
    excluded_terr = [2, 81, 60, 3, 7, 64, 14, 66, 15, 86, 67, 89, 68, 71, 76,
                     69, 70, 95, 43, 72, 74, 52, 78, 79]

    # Remove the ids in excluded_terr from the dataframe
    data = data[~data.FIPS.isin(excluded_terr)]

    # print(data.head())

    return data


def get_merged():
    '''
    This function imports the census and geospatial
    data, formats them, and then merge them and
    returns the merged dataframe.
    '''
    # Imports geo data
    geofile = "Project datasets/tl_2019_us_county"
    geodataset = geo_organized(geofile)

    # Imports census data
    censusfile = 'Project datasets/CensusData.csv'
    censusdataset = census_organized(censusfile)

    # Import Cases data
    casesdataset = get_cases("Cases")

    # Import Deaths data
    deathsdataset = get_cases("Deaths")

    # Merges census and geo data
    merged_data = data_merge(geodataset, censusdataset, casesdataset,
                             deathsdataset)

    return merged_data, casesdataset, deathsdataset