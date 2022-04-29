# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

###### PIPELINE#####

###1/ loading data###   
data = pd.read_csv('data/AirPollutionSeoul/Measurement_summary.csv')


#### 2/ Data preparation and exploration####
# separate date and time from measurement date features
data_prepared = data['Measurement date'].str.split(" ")
adrs = data['Address'].str.split(",")
adrs = adrs.map(lambda x: ','.join(x[0:3]))
adrs = pd.DataFrame({'Short_address':adrs}, columns=["Short_address"])
data['Short_address']=adrs['Short_address']
dates = data_prepared.map(lambda x: x[0])
times = data_prepared.map(lambda x: x[1])
data_prepared= pd.DataFrame({'Date':dates, 'Time':times},  columns=['Date', 'Time'])
data['Date']= data_prepared['Date']
data['Time']= data_prepared['Time']
# Create a column containing the month and year
data['Year'] = pd.to_datetime(data['Date']).dt.to_period('Y')
data['Month'] = pd.to_datetime(data['Date']).dt.to_period('M')
# Aggregate by year, month, station
df_air = data.groupby(['Short_address','Year','Month'], as_index=False).agg({'SO2':'mean',
 'NO2':'mean', 'O3':'mean', 'CO':'mean', 'PM10':'mean', 'PM2.5':'mean'})

##Status of polluants preparation based if measurement info file in order to add color in the Bar
so2_status = df_air[['Short_address','Year','Month', 'SO2']]
so2_status['SO2_status'] = pd.DataFrame({'SO2_status':so2_status['SO2'].map(lambda x: "Very bad" if float(x)>=1.0 else "Bad" if
float(x)<1.0 and float(x)>=0.15 else "Normal" if float(x)<0.15 and x>=0.05 else "Good" )})

no2_status = df_air[['Short_address','Year','Month', 'NO2']]
no2_status['NO2_status'] = pd.DataFrame({'NO2_status':no2_status['NO2'].map(lambda x: "Very bad" if float(x)>=2.0 else "Bad" if
float(x)<2.0 and float(x)>=0.2 else "Normal" if float(x)<0.2 and x>=0.06 else "Good" )})

co_status = df_air[['Short_address','Year','Month', 'CO']]
co_status['CO_status'] = pd.DataFrame({'CO_status':co_status['CO'].map(lambda x: "Very bad" if float(x)>=50 else "Bad" if
float(x)<50.0 and float(x)>=15 else "Normal" if float(x)<15 and x>=9 else "Good" )})


o3_status = df_air[['Short_address','Year','Month', 'O3']]
o3_status['O3_status'] = pd.DataFrame({'O3_status':o3_status['O3'].map(lambda x: "Very bad" if float(x)>=.5 else "Bad" if
float(x)<.5 and float(x)>=.15 else "Normal" if float(x)<.15 and x>=.09 else "Good" )})


pm10_status = df_air[['Short_address','Year','Month', 'PM10']]
pm10_status['PM10_status'] = pd.DataFrame({'PM10_status':pm10_status['PM10'].map(lambda x: "Very bad" if float(x)>=600.0 else "Bad" if
float(x)<600.0 and float(x)>=150 else "Normal" if float(x)<150 and x>=80 else "Good" )})

pm25_status = df_air[['Short_address','Year','Month', 'PM2.5']]
pm25_status['PM2.5_status'] = pd.DataFrame({'PM2.5_status':pm25_status['PM2.5'].map(lambda x: "Very bad" if float(x)>=500.0 else "Bad" if
float(x)<500.0 and float(x)>=75 else "Normal" if float(x)<75 and x>=35 else "Good" )})


Addresses = data['Short_address'].unique()
years = data['Year'].unique()


##### Static method
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])
##################

app = Dash(__name__)


app.layout = html.Div([
    html.H1(children='Air pollution analysis in Seoul', style={'text-align':'center'}),
    html.Div([
        html.H2(children='Average of concentration by station addresses', style={'text-align':'left'}),
        html.Br(),
        dcc.Dropdown(id='dropdown_years',options=[{"label":"2017","value":"2017"},
         {"label":"2018","value":"2018"},
         {"label":"2019","value":"2019"},], multi=False, value="2017"),
          dcc.Dropdown(id='polluants_id',options= [{"label":"SO2","value":"SO2"},
           {"label":"NO2","value":"NO2"}, {"label":"O3","value":"O3"},
            {"label":"PM10","value":"PM10"}, {"label":"PM2.5","value":"PM2.5"}],
             multi=False, value="NO2"),
        dcc.Graph(id='barchart1', figure={})
     ]),
     
    html.Div([
        html.H2(children='PieChart analysis', style={'text-align':'left'}),
        dcc.Dropdown(id='dropdown_stations',options=Addresses,multi=False, value=Addresses[0]),
        html.Br(),
     ]),

    html.Div([
        html.H2(children='Map analysis', style={'text-align':'left'}),
        dcc.Dropdown(id='dropdown_stations2',options=Addresses,multi=False, value=Addresses[0]),
        html.Br(),
     ])

    
       
])


####Callback for connecting components
@app.callback(
    Output(component_id='barchart1', component_property='figure'),
    [Input(component_id='dropdown_years', component_property='value'),
     Input(component_id='polluants_id', component_property='value')]
)
def update_graph(year, gaz):
    if gaz == "PM10":
        df = pm10_status.copy()
        color = "PM10_status"
    elif gaz=="PM2.5":
        df = pm25_status.copy()
        color = "PM2.5_status"
    elif gaz=="NO2":
        df = no2_status.copy()
        color = "NO2_status"
    elif gaz=="SO2":
        df = so2_status.copy()
        color = "SO2_status"
    elif gaz=="O3":
        df = o3_status.copy()
        color = "O3_status"
    else :
        df = co_status.copy()
        color = "co_status"
   
    ##filter dataframe with year value selected by user
    df = df[df["Year"]==str(year)]
    
   
    ## prepare the figure according to the filtered data
    fig = px.bar(df, x='Short_address', y=gaz,
     title="Mean of pollutions grouped by address station and year", color=color)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)


"""from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import dates as mpl_dates
import numpy as np
import os

os.getcwd()

app = Dash(__name__)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options

###### PIPELINE#####

###1/ loading data###   
data = pd.read_csv('data/AirPollutionSeoul/Measurement_summary.csv')
#data.to_csv("data/AirPollutionSeoul/Measurement_summary_save.csv", index=False)


#### 2/ Data preparation and exploration####
# separate date and time from measurement date features
data_prepared = data['Measurement date'].str.split(" ")
dates = data_prepared.map(lambda x: x[0])
times = data_prepared.map(lambda x: x[1])
#print(dtt, type(dtt))
#print(times[0:10])
stations = data[['Station code']].drop_duplicates() ### usefull if you show the addresses by extracting it from address!*
data_prepared= pd.DataFrame({'Date':dates, 'Time':times},  columns=['Date', 'Time'])
data['Date']= data_prepared['Date']
data['Time']= data_prepared['Time']
# Create a column containing the month
data['Year'] = pd.to_datetime(data['Date']).dt.to_period('Y')
data['Month'] = pd.to_datetime(data['Date']).dt.to_period('M')

print(data.head(10))


def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")
#fig = px.bar(data.head(10), x="Year", y="SO2", color="Station code", barmode="group")

app.layout = html.Div(children=[
    html.H1(children='Air Polution In Seoul City'),

    html.Div(children='''
        Gaz poluants analysis.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

app.layout = html.Div([
    html.H4(children='Dataset'),
    generate_table(data)
])

if __name__ == '__main__':
    app.run_server(debug=True)







dcc.Dropdown(id='dropdown_years',options=[{"label":"2017","value":"2017"}, {"label":"2018","value":"2018"},
     {"label":"2019","value":"2019"},], multi=False, value="2017"),

"""