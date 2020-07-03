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