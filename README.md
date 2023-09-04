# humphreysBus
CDAS work on CP Humphreys Project

# Setup
Project was a data analysis, visualization, and potential simulation request from 8th Army Korea ORSAs. The Garrison on Cp Humphreys wanted to make the bus routes better, and wanted a data-driven analysis to inform the changes. The two main datasets for this analysis are: `busData.csv` and `taxiData.csv`. To help with the visualizations, I had to create the `locationSheet`, `locationDictionary`, and `locationBusOnly` files by manually looking up locations using installation maps and open source imagery from Google. 

# Exploratory Analysis
To conduct the initial exploratory analysis, I used Jupyter Notebooks to import, clean, and help build some visualizations. These can be seen in the `taxiVisualization` and `busAnalysisVisualization` files. Most of the visualizations were interactive, but some of the clips look like:

![Bus Demand](/images/puDOheatmap.png)

![Pick Up By Stop](/images/busPickups.png)

![Drop Offs by Stop](/images/busDropOffs.png)

# Simulation
With a solid idea of what the data looked like, I then set about building some basic SimPy simulations to model the existing route. 
