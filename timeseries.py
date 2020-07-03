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