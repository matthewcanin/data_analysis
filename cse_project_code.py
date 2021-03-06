# -*- coding: utf-8 -*-
'''
CSE Project Code

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1m4Vf5jk6r0hsZ4oIJDcqmPJfq0IpYa2G
'''

# data_imports.py
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

# data_visualization.py
'''
Creates geospatial plots for states and the US.
'''

from matplotlib import pyplot as plt
import pandas as pd

from data_imports import get_merged

from statistics import get_statistics

from timeseries import county_timeseries
from timeseries import state_timeseries


def population_graphs(coronadata, place, type, par):
    '''
    This function takes a dataframe of coronavirus cases
    by country and returns 3 plots.
    1. A plot of the population by location (State or Country level)
    2. A plot of the reported cases by location
    3. A plot of the reported deaths by location
    If type = None & par = None, returns a non-normalized set of graphs.
    If type = "Normalized" & par = None,
    returns a population-normalized set of graphs.
    If type = "Normalized" & par = "Density",
    returns a population density-normalized set of graphs.
    '''
    # this is the folder name
    folder = 'Project datasets/Geo_graphs/'
    pd.options.mode.chained_assignment = None
    if place == "US":
        location_data = coronadata[['geometry', 'Province_State',
                                    'POPESTIMATE2019', 'Cases', 'Deaths']]
        location_data = location_data.dissolve(by="Province_State",
                                               aggfunc='sum')
    else:
        location_data = coronadata.loc[coronadata["Province_State"] == place]

    if type == "Normalized":

        location_data["NormCases"] = (location_data['Cases'] /
                                      location_data["POPESTIMATE2019"]
                                      * 100000)

        case_mean = location_data['NormCases'].mean()

        location_data["NormDeaths"] = (location_data["Deaths"] /
                                       location_data["POPESTIMATE2019"]
                                       * 100000)

        deaths_mean = location_data["NormDeaths"].mean()

        if par == "Density":
            location_data['area'] = location_data['geometry'].\
                                    to_crs({'init': 'epsg:3395'}).\
                                    map(lambda p: p.area / (4*10**6))
            location_data["NormCases"] = location_data["NormCases"] / \
                location_data['area']
            case_mean = location_data['NormCases'].mean()
            location_data["NormDeaths"] = location_data["NormDeaths"] / \
                location_data['area']
            deaths_mean = location_data["NormDeaths"].mean()

        # plot the output
        location_data.plot(column='POPESTIMATE2019', legend=True)
        plt.title(place + ' Population')
        plt.xticks([])
        plt.yticks([])
        plt.savefig(folder + 'Population.png')

        location_data.plot(column="NormCases", legend=True,
                           clim=(0, 1.5 * case_mean))
        if par == 'Density':
            plt.title(place + ' Cases per 100,000 people/square mile')
        else:
            plt.title(place + ' Cases per 100,000 people')
        plt.xticks([])
        plt.yticks([])
        plt.savefig(folder + 'Cases.png')

        location_data.plot(column='NormDeaths', legend=True,
                           clim=(0, 1.5 * deaths_mean))
        if par == 'Density':
            plt.title(place + ' Deaths per 100,000 people/square mile')
        else:
            plt.title(place + ' Deaths per 100,000 people')
        plt.xticks([])
        plt.yticks([])
        plt.savefig(folder + 'Deaths.png')

    else:
        location_data.plot(column='POPESTIMATE2019', legend=True)
        plt.title(place + ' Population')
        plt.xticks([])
        plt.yticks([])
        plt.savefig(folder + 'Population.png')

        location_data.plot(column='Cases', legend=True)
        plt.title(place + ' Reported Cases')
        plt.xticks([])
        plt.yticks([])
        plt.savefig(folder + 'Reported_Cases.png')

        location_data.plot(column='Deaths', legend=True)
        plt.title(place + ' Reported Deaths')
        plt.xticks([])
        plt.yticks([])
        plt.savefig(folder + 'Reported_Deaths.png')

    return


def main():
    merged_data_tuple = get_merged()
    merged_data = merged_data_tuple[0]
    casesdataset = merged_data_tuple[1]
    deathsdataset = merged_data_tuple[2]

    # Parameters for location
    county = "King"
    state = "Washington"

    # For the county
    county_timeseries(casesdataset, "Cases", county, state)
    county_timeseries(deathsdataset, "Deaths", county, state)
    population_graphs(merged_data, place="US", type="Normalized",
                      par="Density")

    # For the state
    state_timeseries(casesdataset, "Cases", state)
    state_timeseries(deathsdataset, "Deaths", state)

    # Plots the population graphs
    population_graphs(merged_data, place=state, type="Normalized",
                      par="Density")

    get_statistics(merged_data, para='Density')


if __name__ == "__main__":
    main()

# timeseries.py
'''
This file is responsible for graphing
the timeseries plots.
Only the function state_timeseries
needs to be imported to get the graphs.
'''

from matplotlib import pyplot as plt


def get_county_data(data, county, state):
    """
    This function takes in the cases or deaths
    dataframe and the county name and returns the
    relevant row as a panda series.
    """
    # Filtering the relevant data
    mask1 = data["Admin2"] == county
    mask2 = data["Province_State"] == state
    temp = data[mask1 & mask2]

    data_row = temp.iloc[0].copy(deep=True)

    return data_row


def get_state_data(data, state):
    # Gets the data for the relevant state
    mask = data["Province_State"] == state
    temp = data[mask].reset_index()

    # Groups the data by their sum
    temp2 = temp.groupby(["Province_State"]).sum()

    # Turns the dataframe into a series
    data_row = temp2.iloc[0].copy(deep=True)

    # Saves the State name for later use
    data_row.loc["UID"] = state

    return data_row


def graph_cum_timeseries(data, kind, place):
    """
    This function takes a data series
    and kind of case (Normalized/Raw Cases/Deaths)
    and place type (either County or State)
    and graphs the cumulative number of cases/deaths.
    Returns None
    The prints are saved under the name
    "Cumulative_kind_in_County/State name.png"
    """
    # Sets up parameters
    time_data = data[12:]

    # Adds county to the name
    if place == "County":
        name = data["Admin2"] + "_County"
    else:
        name = data["UID"]

    time_data.plot()

    # Plot settings
    plt.title(kind + " in " + name)
    plt.ylabel(kind)
    plt.xlabel("day")
    plt.tight_layout()

    # Saving the plot
    plt.savefig("Project datasets/Timeseries/Cumulative_" +
                kind + "_in_" + name + ".png")
    plt.close()


def graph_diff_timeseries(data, kind, place):
    """
    This function takes a data series
    and a string with the kind of case
    (Normalized/Raw Cases/Deaths)
    and a string with the place type (either County or State)
    and graphs the number of cases/deaths for each day.
    Returns None
    The prints are saved under the name
    "New_kind_in_County/State name.png"
    """
    # Sets up parameters
    time_data = data[12:]
    difference = time_data.diff()

    # Adds county to the name
    if place == "County":
        name = data["Admin2"] + " County"
    else:
        name = data["UID"]

    difference.plot()

    # Plot settings
    plt.title("Daily " + kind + " in " + name)
    plt.xlabel(kind)
    plt.ylabel("day")
    plt.tight_layout()

    # Saving the plot
    plt.savefig("Project datasets/Timeseries/New_" +
                kind + "_in_" + name + ".png")
    plt.close()


def county_timeseries(data, kind, county, state):
    """
    This function takes in the cases or deaths
    data, and the county name and state
    and prints a timeserises graph.
    Returns none.
    """
    # Gets the relevant row
    data_row = get_county_data(data, county, state)

    # Gets time data
    graph_cum_timeseries(data_row, kind, "County")
    graph_diff_timeseries(data_row, kind, "County")

    # Normalizes the data
    nor_kind = "Normalized " + kind
    nor_data = data_row.copy(deep=True)
    nor_data[12:] = nor_data[12:] / nor_data["Population"]

    # Gets Normalized time data
    graph_cum_timeseries(nor_data, nor_kind, "County")


def state_timeseries(data, kind, state):
    """
    This function takes in the cases or deaths
    data, a string with the type of data
    (Cases or Deaths) and the state name
    and prints a timeserises graph.
    Returns none.
    """
    # Gets the relevant row
    data_row = get_state_data(data, state)

    # Gets time data
    graph_cum_timeseries(data_row, kind, "State")
    graph_diff_timeseries(data_row, kind, "State")

    # Normalizes the data
    nor_kind = "Normalized " + kind
    nor_data = data_row.copy(deep=True)
    nor_data[12:] = nor_data[12:] / nor_data["Population"] * 100000

    # Gets Normalized time data
    graph_cum_timeseries(nor_data, nor_kind, "State")

# statistics.py
'''
This file is responsible for the statistical
analysis of the data.
'''

from matplotlib import pyplot as plt
import pandas as pd
import scipy.stats as stats


def get_statistics(data, para="Population", cases="Cases"):
    """
    This function takes the data for population
    and Cases/Deaths (baseed on cases parameter)
    for studies the statistical significance of the effects
    of population or population density depending on the
    parameter passed, with population being the default.
    This function prints out the results and returns None.
    """
    # Checks whether the data is for population or
    # population density
    if para == "Population":
        data["Pop_Parameter"] = data["POPESTIMATE2019"]
    elif para == "Density":
        data['area'] = data['geometry'] \
                      .to_crs({'init': 'epsg:3395'}) \
                      .map(lambda p: p.area / (4*10**6))
        data["Pop_Parameter"] = data["POPESTIMATE2019"] / data['area']

    # Gets the normalized data
    if cases == "Cases":
        data['Norm_Cases'] = data["Cases"] / data["POPESTIMATE2019"] * 100000
    elif cases == "Deaths":
        data['Norm_Cases'] = data["Deaths"] / data["POPESTIMATE2019"] * 100000

    # Groups the data into sections
    # Makes masks for use in grouping data
    pd.options.mode.chained_assignment = None
    if para == "Population":
        mask1 = data["Pop_Parameter"] < 10000
        mask2 = data["Pop_Parameter"] < 30000
        mask3 = data["Pop_Parameter"] < 100000
        mask4 = data["Pop_Parameter"] < 1000000

    elif para == "Density":
        mask1 = data["Pop_Parameter"] < 30
        mask2 = data["Pop_Parameter"] < 60
        mask3 = data["Pop_Parameter"] < 120
        mask4 = data["Pop_Parameter"] < 250

    # Group 1 x < 10k
    group1 = data[mask1]

    # Group 2 10k < x < 30k
    group2 = data[~mask1 & mask2]

    # Group 3 30k < x < 100k
    group3 = data[~mask2 & mask3]

    # Group 4 100k < x < 1M
    group4 = data[~mask3 & mask4]

    # Group 5 x > 1M
    group5 = data[~mask4]

    # Variables for analysis
    groups = [group1, group2, group3, group4, group5]
    mean = list()
    std = list()
    for group in groups:
        mean.append(group["Norm_Cases"].mean())
        std.append(group["Norm_Cases"].std())

    # Making boxplots to visualize data
    if para == "Population":
        group1["Data"] = "Very Small"
        group2["Data"] = "Small"
        group3["Data"] = "Medium"
        group4["Data"] = "Large"
        group5["Data"] = "Very Large"
    else:
        group1["Data"] = "Very Sparse"
        group2["Data"] = "Sparse"
        group3["Data"] = "Medium"
        group4["Data"] = "Dense"
        group5["Data"] = "Very Dense"

    # Plotting plot
    cd = pd.concat(groups)
    plt.figure()
    cd.boxplot(by="Data", column=["Norm_Cases"])

    # Plot settings
    if para == "Population":
        temp = "Population"
    elif para == "Density":
        temp = "Population Density"

    plt.suptitle('')
    plt.title(cases + " grouped by county " + temp)
    plt.ylabel(str(cases) + " Per 100,000 population")
    plt.xlabel("County Type")
    plt.tight_layout()

    plt.savefig("Project datasets/Statistics/groups-distribution.png")

    # Setting a size limit to make a better plot
    height = data["Norm_Cases"].mean() + 3 * data["Norm_Cases"].std()
    plt.ylim(0, height)

    plt.savefig("Project datasets/Statistics/groups-distribution2.png")

    plt.close()

    # What worked
    data_clean = data.dropna(subset=["Pop_Parameter", "Norm_Cases"])
    s, p = stats.pearsonr(data_clean["Pop_Parameter"],
                          data_clean["Norm_Cases"])
    print("p-value = " + str(p))

    return None

"""
# README.md

All  required files needed to run this program are included in the Final Project working directory.
This directory contains 4 python files, and a folder named Project Datasets. The Project Datasets
folder contains 3 subfolders in addition to 3 CSV files. 2 of the 3 subfolders are used to store
outputted graphs created from running the program. The third subfolder contains the geospatial
data used in this project.

IN ORDER TO RUN:
1. You must initialize the 4 python files: data_imports, data_visualization, timeseries, and statistics.
2. Run the data_visualization file. This will run all the other files and will provide results.
The desired location can be chosen by changing the variables 'county' and 'state' in the main function.
Additionally, setting state='US' allows the user to look at county-summed aggregates of all states rather than just one state.
The population graphing function has hyperparameters 'type' and 'par' that can be changed to allow the user to look at:
a. Raw data
b. Data normalized by population 
c. Data normalized by population density (pop/area)

The get_statistics function has the parameter 'para' that allows the user to specify if the stats are
to be compared on the basis of population or population density.

After running the file, the resulting output plots from the time series data and the population graphs
can be found in sub folders within the Project datasets folder.

IMPORTANT NOTE
1. It is important that the directory structure is unchanged. Moving folders or files out of their
respective locations within the directory will prevent the program from running.
2. Every time the code is run, the output plot replaces the current plot in the directory. If you want
to save a specific plot, you must change its file name before running the code with the same parameters.
"""

