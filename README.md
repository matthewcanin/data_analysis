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

