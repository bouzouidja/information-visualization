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



px.set_mapbox_access_token(open("data/AirPollutionSeoul/Token.txt").read())


##################

#### Overview dataframe##############
def polluant_overview_barchart(df_air):
    """fig = px.bar(df_air, x='Short_address', y=['NO2','SO2','O3',],
                     title="Mean of pollutions grouped by address station and year")
                fig.show()
    """
    fig = px.bar(df_air, x='Short_address', y='NO2',
     title="Mean of pollutions grouped by address station", labels={"Short_address":"Station name"})

def polluant_overview_line(data):
    # Create traces
    #print(df_air.head(700))
   
    df_sorted = data.copy().groupby(['Year_month','Year','Month'], as_index=False).agg({'SO2':'mean',
     'NO2':'mean', 'O3':'mean', 'CO':'mean', 'PM10':'mean', 'PM2.5':'mean'}).sort_values(by="Year_month")
    #df_sorted.to_csv('df_sorted.csv')
    fig= go.Figure()
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::2], y=df_sorted['NO2'].iloc[::2],
                    mode='lines+markers',
                    name='Pollutant NO2')),
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::2], y=df_sorted['SO2'].iloc[::2],
                    mode='lines+markers',
                    name='Pollutant SO2'))
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::2], y=df_sorted['CO'].iloc[::2],
                    mode='lines+markers',
                    name='Pollutant CO'))
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::2], y=df_sorted['O3'].iloc[::2],
                    mode='lines+markers',
                    name='Pollutant O3'))
    fig.update_layout(
    yaxis_title="Concentration %",
    xaxis_title="Time",)


    return fig

def particulate_matter_overview_line(data):
    df_sorted = data.copy().groupby(['Year_month','Year','Month'], as_index=False).agg({'PM10':'mean',
     'PM2.5':'mean'}).sort_values(by="Year_month")
    #df_sorted.to_csv('df_sorted.csv')
    fig= go.Figure()
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::2], y=df_sorted['PM10'].iloc[::2],
                    mode='lines+markers',
                    name='Pollutant PM10'))
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::2], y=df_sorted['PM2.5'].iloc[::2],
                    mode='lines+markers',
                    name='Pollutant PM2.5'))

    fig.update_layout(
    yaxis_title="Concentration (mcg/m3)",
    xaxis_title="Time",)    

    return fig


def piechart_overview(df_air):
    df = df_air.copy()
    fig = px.pie(df, values='CO', names='Short_address', title='Contribution of the pollutants by stations')

    return fig 

