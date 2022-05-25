# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dash_table 
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from urllib.request import urlopen
import json

months_to_number = {'January':'01', 'February':'02','Mars':'03','April':'04','May':'05',
         'June':'06','July':'07','August':'08','September':'09','October':'10',
          'November':'11', 'December':'12'}
polluant_threshold={'SO2':.05,'NO2':.06,'CO':9.0,'O3':.09,'PM10':80.0,'PM2.5':35.0}


ALLOWED_TYPES = (
    "text", "number", "password", "email", "search",
    "tel", "url", "range", "hidden",
)




def read_dataset(path):
    return pd.read_csv('data/AirPollutionSeoul/Measurement_summary.csv')

#### 2/ Data preparation and exploration####
# separate date and time from measurement date features

def datetime_preprocessing(data):
    data_prepared = data['Measurement date'].str.split(" ")
    adrs = data['Address'].str.split(",")
    adrs = adrs.map(lambda x: ','.join(x[2:3]))
    adrs = pd.DataFrame({'Short_address':adrs}, columns=["Short_address"])
    data['Short_address']=adrs['Short_address']
    dates = data_prepared.map(lambda x: x[0])
    times = data_prepared.map(lambda x: x[1])
    data_prepared= pd.DataFrame({'Date':dates, 'Time':times},  columns=['Date', 'Time'])
    data['Date']= data_prepared['Date']
    data['Time']= data_prepared['Time']

    # Create a column containing the month and year
    #data['Year'] = pd.to_datetime(data['Date']).dt.to_period('Y')
    data['Year'] = data['Date'].str.split("-").map(lambda x: x[0])
    #print("this is the years2", data['Year'])

    data['Month'] = data['Date'].str.split("-").map(lambda x: x[1])
    #dddd = pd.DatetimeIndex(data['Measurement date']).month

    year_month=data_prepared['Date'].str.split('-').map(lambda x:'-'.join(x[0:2]))
    data['Year_month']=year_month

    return data


def aggregation(data):

    return  data.groupby(['Short_address','Year_month','Year','Month','Latitude','Longitude'],
     as_index=False).agg({'SO2':'mean', 'NO2':'mean', 'O3':'mean', 'CO':'mean', 'PM10':'mean',
      'PM2.5':'mean'})

###avoid negative value
def filter_negative_no2(data):
    return data[(data["NO2"]>=0)]




def generate_days(year, month, data):
    dates= data[(data['Year']==str(year)) & (data['Month']==months_to_number[month])]
    dates=dates['Date'].unique()
    return dates


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




#### Overview dataframe##############
