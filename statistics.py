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