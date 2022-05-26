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
import preprocessing as prp
import global_overview as glo
import base64





###### set up Plotly express token #####
px.set_mapbox_access_token(open("data/AirPollutionSeoul/Token.txt").read())

###### PIPELINE#####

###1/ loading data### 

#data = pd.read_csv('data/AirPollutionSeoul/Measurement_summary.csv')
data=prp.read_dataset('data/AirPollutionSeoul/Measurement_summary.csv')

#### Preprocessing steps
data = prp.datetime_preprocessing(data)
 

### Aggregation of polluants by stations, year, month, longitude, lattitude
df_air = prp.aggregation(data)


####Avoid negative values for NO2 Polluant
df_air = prp.filter_negative_no2(df_air)



##############################################

app = Dash(__name__)


app.layout = html.Div([
 
        html.Div([
            html.H1(children='Air pollution analysis in Seoul city', style={'text-align':'center',"text-decoration": "underline"}),
            html.Br(),
            html.Img(src=app.get_asset_url('vub_logo.png'), style={'display':'inline-block','height':'10%', 'width':'10%'}),
            html.Img(src=app.get_asset_url('seoul_metropolitan_logo.png'), style={'float':'right','display':'inline-block','height':'20%', 'width':'20%'}),
            html.Br(),
        ]),
    html.Br(),

    html.Div([
        html.H2(children='Overview of pollutants over the whole network', style={'text-align':'left'}),
        
        dcc.Graph(id='polluant_overview_line_id', figure=glo.polluant_overview_line(data))
     ]),
    html.Br(),

    html.Div([
        html.H2(children='Overview of particulate matter over the whole network', style={'text-align':'left'}),
        html.Br(),
        
        dcc.Graph(id='particulate_overview_line_id', figure=glo.particulate_matter_overview_line(data))
     ]),

    html.Br(),

    html.Div([
        html.H2(children='Map overview of pollutants by locations', style={'text-align':'left'}),
        html.Div([
            html.H4(children='Select the pollutant',style={'display':'inline-block','margin-right':160}),
        html.H4(children='Select the animation time',style={'display':'inline-block','margin-right':160}),

            ]),
            dcc.RadioItems(id="radio_polluant__for_map_id",
            options=[{"label":"SO2","value":"SO2"},
           {"label":"NO2","value":"NO2"}, {"label":"CO","value":"CO"}, {"label":"O3","value":"O3"},
            {"label":"PM10","value":"PM10"}, {"label":"PM2.5","value":"PM2.5"}],
            value='NO2',style={'width':'200px','display':'inline-block','margin-right':40}),
        dcc.RadioItems(id="animation_type_id",
            options=[{"label":"By Year","value":"Year"}, {"label":"By Month","value":"Month"}],
            value='Year', style={'display':'inline-block','margin-right':40}),
        html.Br(),        
        dcc.Graph(id='map_polluant_overview', figure={})

     ]),
    html.Br(), 
    

    html.Div([
        html.H2(children='Average of concentration by station', style={'text-align':'left'}),
        
        html.Div([
        html.H4(children='Select the pollutant',style={'display':'inline-block','margin-right':160}),
        dcc.RadioItems(id="radio_polluant_id",
            options=[{"label":"SO2","value":"SO2"},
           {"label":"NO2","value":"NO2"}, {"label":"CO","value":"CO"}, {"label":"O3","value":"O3"},
            {"label":"PM10","value":"PM10"}, {"label":"PM2.5","value":"PM2.5"}],
            value='NO2'),
        html.H4(children='Select the year',style={'display':'inline-block','margin-right':160}),
        html.H4(children='Select the month',style={'display':'inline-block','margin-right':160}),]),
        
        dcc.Dropdown(id='dropdown_years',options=['2017','2018','2019'], multi=False,
         value="2017", style={'width':'200px','display':'inline-block','margin-right':40}, placeholder="Select the year"),
    

        dcc.Dropdown(id='dropdown_months',options=['January', 'February','Mars','April','May',
         'June','July','August','September','October', 'November', 'December'],
          multi=False, value='January', style={'width':'200px','display':'inline-block','margin-right':40},
          placeholder="Select the month"),
        
        html.H2(children='PieChart analysis', style={'text-align':'left'}),
        html.Br(),
        dcc.Graph(id='PieChart_id', figure={}),

        html.Br() , 
        dcc.Graph(id='barchart1', figure={}),
        html.H2(children='Concentration by hours', style={'text-align':'left'}),
        html.H4(children='Select your day',style={'text-align':'left'}),
        dcc.Dropdown(id='dropdown_day',
          style={'width':'200px','display':'inline-block','margin-right':40}, placeholder="Select the day"),
    
        dcc.Graph(id='barchart_by_time', figure={}),
        
     ],id="main_div"),

        html.Div([
        html.H2(children='Concentration overview by limit', style={'text-align':'left'}),   
        html.H4(children='Select the polluant',style={'display':'inline-block','margin-right':160}),
        dcc.RadioItems(id="radio_polluant_tab3_id",
            options=[{"label":"SO2","value":"SO2"},
           {"label":"NO2","value":"NO2"}, {"label":"CO","value":"CO"}, {"label":"O3","value":"O3"},
            {"label":"PM10","value":"PM10"}, {"label":"PM2.5","value":"PM2.5"}],
            value='SO2'),    
        html.Br(),
        dcc.Graph(id='threshold_overview_line_id', figure={}),
        html.Br(),
        html.H3(children='Edit your limitation', style={'text-align':'left'}),   

        dcc.Input(
            id="input_threshold",
            type="range",
            value=0.0,
            placeholder="input type",),

        html.Div(id="out-all-types"),
        ] ),
       
])


####Callback for connecting components###############################
###################################################################

@app.callback(
    Output(component_id='map_polluant_overview', component_property='figure'),
    [Input(component_id='radio_polluant__for_map_id', component_property='value'),
    Input(component_id='animation_type_id', component_property='value'),]
)
def update_map_overview(gaz, animation):
    fig = {}
    if animation=="Year":
        fig = px.scatter_mapbox(df_air[df_air['SO2']>=0],
                 lat="Latitude",
                 lon="Longitude",
                 animation_frame="Year",
                 color=gaz,
                 size="SO2",
                  height=800,
                 color_continuous_scale=px.colors.sequential.Turbo, zoom=10)
    else:
        fig = px.scatter_mapbox(df_air[df_air['SO2']>=0],
                 lat="Latitude",
                 lon="Longitude",
                 animation_frame="Year_month",
                 color=gaz,
                 size="SO2",
                  height=550,
                  mapbox_style="carto-positron",
                 color_continuous_scale=px.colors.sequential.Turbo, zoom=10)
    return fig




@app.callback(
    [Output(component_id='barchart1', component_property='figure'),
    Output(component_id='PieChart_id', component_property='figure'),
     Output(component_id='dropdown_day', component_property='options'),
     Output(component_id='dropdown_day', component_property='value'),
      ],
    [
     Input(component_id='radio_polluant_id', component_property='value'),
     Input(component_id='dropdown_years', component_property='value'),
     Input(component_id='dropdown_months', component_property='value'),
     
      ]
)
def update_graph(gaz, year, month):
    res = ()

    ##filter dataframe with year value selected by user
    if year and month:
        days = prp.generate_days(year, month, data)
        mth = str(year)+"-"+prp.months_to_number[month]
        df =df_air.copy()
        df = df[(df["Year"]==str(year)) & (df["Month"]==prp.months_to_number[month]) ]
        ## prepare the figure according to the filtered data
        fig = px.bar(df, x='Short_address', y=gaz,
         title="Mean of pollutions grouped by station and year", color="SO2",
         color_continuous_scale=px.colors.sequential.Turbo,
          labels={"Short_address":"Station name"})
        # Plotly Express
        fig2 = px.pie(df, values=gaz, names='Short_address', title='Contribution of the pollutants by stations')
        
        res = fig, fig2, days,days[0]

    return res

@app.callback(Output(component_id='barchart_by_time', component_property='figure'),
            [Input(component_id='dropdown_day', component_property='value'),
            Input(component_id='radio_polluant_id', component_property='value'),],)
def update_barchart_day(day,gaz):
    res = {}
    if day:
        data_by_hour = data[(data['Measurement date'].str.split(' ').map(lambda  x:x[0])==day)].copy()
        data_by_hour['Day_time']=data_by_hour['Measurement date'].str.split(' ').map(lambda x:x[1])

        fig = px.bar(data_by_hour, x='Short_address', y=gaz,
             title="Mean of pollutions by day", color='SO2',
              animation_frame="Day_time",
              color_continuous_scale=px.colors.sequential.Turbo,
               labels={"Short_address":"Station name"})
        res = fig
    return res



@app.callback([Output(component_id='threshold_overview_line_id', component_property='figure'),
                Output(component_id="input_threshold",component_property='min'),
                Output(component_id="input_threshold",component_property='max'),
                ],
             [Input(component_id='radio_polluant_tab3_id', component_property='value'),
             Input(component_id='input_threshold', component_property='value')],)
def update_threshold_linechart(gaz, threshold):
    threshold= prp.polluant_threshold[gaz]
    df_sorted = data.copy().groupby(['Year_month','Year','Month'], as_index=False).agg({'SO2':'mean',
         'NO2':'mean', 'O3':'mean', 'CO':'mean', 'PM10':'mean', 'PM2.5':'mean'}).sort_values(by="Year_month")
    df_sorted['Threshold_polluant']=df_sorted[gaz].map(lambda x:threshold)
    #print(df_sorted)
    fig= go.Figure()
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::], y=df_sorted[gaz].iloc[::],
                            mode='lines+markers',
                            name='Polluant '+ gaz),),
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::], y=df_sorted['Threshold_polluant'].iloc[::],
                            mode='lines',
                            name='Threshold '+gaz))
    min =0
    max =0
    if gaz=="PM2.5":
        min= 30.0
        max=150.0
    elif gaz=="PM10":
        min= 15.0
        max=75.0
    elif gaz=="SO2":
        min= .02
        max= .15
    elif gaz=="NO2":
        min= .03
        max= .2
    elif gaz=="CO":
        min= 2.0
        max= 15.0
    elif gaz=="O3":
        min= .03
        max= .15
    return fig, min, max

@app.callback(
    Output("out-all-types", "children"),
    [Input("input_threshold", "value"),
    Input("radio_polluant_tab3_id", "value"), ],
)
def cb_render(rangeval, gaz):
        
        prp.polluant_threshold[gaz]=rangeval
        return "range: {}".format(rangeval)

"""
@app.callback(
    Output("number-out", "children"),
    Input("dfalse", "value"),
    Input("dtrue", "value"),
    Input("input_range_2", "value"),
)
def number_render(fval, tval, rangeval):
    return "dfalse: {}, dtrue: {}, range: {}".format(fval, tval, rangeval)
"""


if __name__ == '__main__':
    app.run_server(debug=True,threaded=True)