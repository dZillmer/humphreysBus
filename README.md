# CP Humphreys Bus: Data Analysis, Visualization, and Simulation
This project was a request for analytical support by 8th Army Korea ORSAs. The project primarily consisted of data analysis and visualization of two datasets, and a request for quantitative technique to facilitate comparing varying route options in implementing potential new bus routes. The outputs were a variety of visualizations and a basic SimPy simulation that allowed for comparing alternate routes via a "time in transit" metric to compare the existing routes to potential new ones. 

# Setup
Project was a data analysis, visualization, and potential simulation request from 8th Army Korea ORSAs. The Garrison on Cp Humphreys wanted to make the bus routes better, and wanted a data-driven analysis to inform the changes. The two main datasets for this analysis are: `busData.csv` and `taxiData.csv`. To help with the visualizations, I had to create the `locationSheet`, `locationDictionary`, and `locationBusOnly` files by manually looking up locations using installation maps and open source imagery from Google. 

# Exploratory Analysis
To conduct the initial exploratory analysis, I used Jupyter Notebooks to import, clean, and help build some visualizations. These can be seen in the `taxiVisualization` and `busAnalysisVisualization` files. Most of the visualizations were interactive, but some of the clips look like:

![Bus Demand](/images/puDOheatmap.png)

![Pick Up By Stop](/images/busPickups.png)

![Drop Offs by Stop](/images/busDropOffs.png)

# Simulation
With a solid idea of what the data looked like, I then set about building some basic SimPy simulations to model the existing route. My basic workflow, as seen across the `busSimulation.py` file iterations (before I began to use Git for version control!), was:
- clean, explore, and analyze data (as seen above)
- identify a metric for success (i.e., in this case, we considered average transit time)
- use data to build "oriented demand" data per stop
- use Poisson random variables calibrated off data to estimate basic simulation inputs
- verify simulation works by comparing it to reality
- calculate current route metrics
- using proposed routes, compare new route metrics to old routes to assess which were better

One example of the simulation versus data visualizations is below.

![Sim Versus Observation](/images/simComparisonOverview.png)

# Results
|   | Green Route | Blue Route | Red/Black Route | Weighted Average|
|---|-------------|------------|-----------------|-----------------|
|Old Route | 12.94 |     12.68 |       12.06     | 12.57|
|New Route | 9.55  |      9.38 |        9.46     | 9.47 |
