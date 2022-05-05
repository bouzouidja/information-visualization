# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json



###### set up Plotly express token #####
px.set_mapbox_access_token(open("data/AirPollutionSeoul/Token.txt").read())

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
df_air = data.groupby(['Short_address','Year','Month','Latitude','Longitude'], as_index=False).agg({'SO2':'mean',
 'NO2':'mean', 'O3':'mean', 'CO':'mean', 'PM10':'mean', 'PM2.5':'mean'})

##Status of polluants preparation based if measurement info file in order to add color in the Bar
so2_status = df_air[['Short_address','Year','Month', 'SO2','Latitude','Longitude']]
so2_status['SO2_status'] = pd.DataFrame({'SO2_status':so2_status['SO2'].map(lambda x: "Very bad" if float(x)>=1.0 else "Bad" if
float(x)<1.0 and float(x)>=0.15 else "Normal" if float(x)<0.15 and x>=0.05 else "Good" )})

no2_status = df_air[['Short_address','Year','Month', 'NO2','Latitude','Longitude']]
no2_status['NO2_status'] = pd.DataFrame({'NO2_status':no2_status['NO2'].map(lambda x: "Very bad" if float(x)>=2.0 else "Bad" if
float(x)<2.0 and float(x)>=0.2 else "Normal" if float(x)<0.2 and x>=0.06 else "Good" )})

co_status = df_air[['Short_address','Year','Month', 'CO','Latitude','Longitude']]
co_status['CO_status'] = pd.DataFrame({'CO_status':co_status['CO'].map(lambda x: "Very bad" if float(x)>=50 else "Bad" if
float(x)<50.0 and float(x)>=15 else "Normal" if float(x)<15 and x>=9 else "Good" )})


o3_status = df_air[['Short_address','Year','Month', 'O3','Latitude','Longitude']]
o3_status['O3_status'] = pd.DataFrame({'O3_status':o3_status['O3'].map(lambda x: "Very bad" if float(x)>=.5 else "Bad" if
float(x)<.5 and float(x)>=.15 else "Normal" if float(x)<.15 and x>=.09 else "Good" )})


pm10_status = df_air[['Short_address','Year','Month', 'PM10','Latitude','Longitude']]
pm10_status['PM10_status'] = pd.DataFrame({'PM10_status':pm10_status['PM10'].map(lambda x: "Very bad" if float(x)>=600.0 else "Bad" if
float(x)<600.0 and float(x)>=150 else "Normal" if float(x)<150 and x>=80 else "Good" )})

pm25_status = df_air[['Short_address','Year','Month', 'PM2.5','Latitude','Longitude']]
pm25_status['PM2.5_status'] = pd.DataFrame({'PM2.5_status':pm25_status['PM2.5'].map(lambda x: "Very bad" if float(x)>=500.0 else "Bad" if
float(x)<500.0 and float(x)>=75 else "Normal" if float(x)<75 and x>=35 else "Good" )})


Addresses = data['Short_address'].unique()
years = data['Year'].unique()
months = data['Month'].unique()
print(months)



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
months_to_number = {'January':'01', 'February':'02','Mars':'03','April':'04','May':'05',
         'June':'06','July':'07','August':'08','September':'09','October':'10',
          'November':'11', 'December':'12'}
##################

app = Dash(__name__)


app.layout = html.Div([
    html.H1(children='Air pollution analysis in Seoul', style={'text-align':'center'}),
    html.Div([
        html.H2(children='Average of concentration by station addresses', style={'text-align':'left'}),
          dcc.Dropdown(id='polluants_id', options= [{"label":"SO2","value":"SO2"},
           {"label":"NO2","value":"NO2"}, {"label":"O3","value":"O3"},
            {"label":"PM10","value":"PM10"}, {"label":"PM2.5","value":"PM2.5"}],
             multi=False, value="NO2", style={'width':'200px'}, placeholder="Select the polluant"),
        html.Br(),
        dcc.Dropdown(id='dropdown_years',options=['2017','2018','2019'], multi=False,
         value="2017", style={'width':'200px'}, placeholder="Select the year"),
        
        html.Br(),
        dcc.Dropdown(id='dropdown_months',options=['January', 'February','Mars','April','May',
         'June','July','August','September','October', 'November', 'December'],
          multi=False, value='January', style={'width':'200px'},
          placeholder="Select the month"),
        
        
        dcc.Graph(id='barchart1', figure={})
     ]),
     
    html.Div([
        html.H2(children='PieChart analysis', style={'text-align':'left'}),
        dcc.Dropdown(id='dropdown_stations',options=Addresses, multi=False, value=Addresses[0]),
        html.Br(),
        dcc.Graph(id='PieChart_id', figure={})
     ]),

    html.Div([
        html.H2(children='Map analysis', style={'text-align':'left'}),
        dcc.Dropdown(id='dropdown_stations2',options=Addresses,multi=False, value=Addresses[0]),
        html.Br(),
        dcc.Graph(id='map_choropleth', figure={})
     ])

    
       
])

####Callback for connecting components
@app.callback(
    [Output(component_id='barchart1', component_property='figure'),
    Output(component_id='PieChart_id', component_property='figure'),
     Output(component_id='map_choropleth', component_property='figure'),],
    [
     Input(component_id='polluants_id', component_property='value'),
     Input(component_id='dropdown_years', component_property='value'),
     Input(component_id='dropdown_months', component_property='value')
      ]
)
def update_graph(gaz, year, month):
    res = False
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
    #print(str(year)+"-01")
    if year and month:
        mth = str(year)+"-"+months_to_number[month]
        print("this is the month in number",mth)
        df = df[(df["Year"]==str(year)) & (df["Month"]==mth) ]
        ## prepare the figure according to the filtered data
        fig = px.bar(df, x='Short_address', y=gaz,
         title="Mean of pollutions grouped by address station and year", color=color)
        # Plotly Express
        fig2 = px.pie(df, values=gaz, names='Short_address', title='Contribution of the polluant')
        fig3 = px.scatter_mapbox(df,
         lat="Latitude",
         lon="Longitude",
         color=color,
         color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)

        res = fig, fig2, fig3
    return res


if __name__ == '__main__':
    app.run_server(debug=True)