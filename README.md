# information-visualization 
This repo is dedicated to our information visualization project that concern Air pollution in Seoul city.


# Project summary
Prepare and then present dataset of 3 years of pollutants collected from 25 factories in Seoul city.
The outcome (graphs, charts) need to be provided to Seoul governement in order to acheive their goals.
# Dataset
The dataset is provided from Kaggle, air pollution in Seoul city (source from Seoul gov official web site)
# Targer users
Seoul governement staffs
# Target tasks
- Protect humain health
- Reduce the pollution within the city
- Nature protection
- Neutralization carbon


# Tools and packages needed
- Dash Plotly lib
- Mapbox lib
- Pandas


# Visualization charts used
- Scatter Mapbox
- Line chart
- PieChart
- BarChart

# Interaction
Show an overview of the whole data set and then show a subset of it, use multiform, facet, 
show for example the bad subset of polluants.

# Tasks to realize and things to avoid


Project :
	Avoid large number,
	Use log scale, for small values
	Avoid brightness color, and try to see if the color is necessary and it givs information

	
-keep the user choose a date and show him the concentration over day..
- Choose the best labels for your visualization
- remove the number in the station address
- show the peak of the concentration by day, by heure de point 16,17 ou midi
- In the presentation show the threshold provided in measurment info
- Set a threshold for each linechart of polluant in order to see when the plot cross the average threshold,
- Allow user to adjust the threshold maybe it a plus!
- Choose the effective polluant and put it as color in all graphs 