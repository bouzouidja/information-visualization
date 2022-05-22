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
#encoded_image = base64.b64encode(open('data/src/static/seoul_metropolitan_logo.png', 'rb').read())
image_filename = 'data/src/static/seoul_metropolitan_logo.png' # replace with your own image
encoded_image = base64.b64encode(open(image_filename, 'rb').read())
#  html.Img(id="VUB", src='data/src/ulb_logo.png;base64,{}'.format(encoded_image)),
#html.Img(id="Seoul", src='data/src/seoul_metropolitan_logo.png;base64,{}'.format(encoded_image)),


app.layout = html.Div([
    html.Div([
        html.Div(
        html.Img(title="VUB",src=app.get_asset_url('data/src/static/vub_logo.png'), style={'height':'10%', 'width':'10%'})),
        html.H1(children='Air pollution analysis in Seoul city', style={'text-align':'center'}),
        html.Img(title="LOGO",src='data/src/static/seoul_metropolitan_logo.png;base64,{}'.format(encoded_image))
        ]),
    html.Br(),

    html.Div([
        html.H2(children='Overview of polluants over the whole network', style={'text-align':'left'}),
        html.Br(),
        
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
        html.H2(children='Map overview of polluants by stations', style={'text-align':'left'}),
        html.Div([
            html.H4(children='Select the polluant',style={'display':'inline-block','margin-right':160}),
        html.H4(children='Select the animation time',style={'display':'inline-block','margin-right':160}),

            ]),
            dcc.RadioItems(id="radio_polluant__for_map_id",
            options=[{"label":"SO2","value":"SO2"},
           {"label":"NO2","value":"NO2"}, {"label":"CO","value":"CO"}, {"label":"O3","value":"O3"},
            {"label":"PM10","value":"PM10"}, {"label":"PM2.5","value":"PM2.5"}],
            value='SO2',style={'width':'200px','display':'inline-block','margin-right':40}),
        dcc.RadioItems(id="animation_type_id",
            options=[{"label":"By Year","value":"Year"}, {"label":"By Month","value":"Month"}],
            value='Year', style={'display':'inline-block','margin-right':40}),
        html.Br(),        
        dcc.Graph(id='map_polluant_overview', figure={})

     ]),
    html.Br(), 
    

    html.Div([
        html.H2(children='Average of concentration by station addresses', style={'text-align':'left'}),
        
        html.Div([
        html.H4(children='Select the polluant',style={'display':'inline-block','margin-right':160}),
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
        
                
        dcc.Graph(id='barchart1', figure={}),
        html.H2(children='concentration by hours of date', style={'text-align':'left'}),
        html.H4(children='Select your day',style={'text-align':'left'}),
        dcc.Dropdown(id='dropdown_day',
          style={'width':'200px','display':'inline-block','margin-right':40}, placeholder="Select the day"),
    
        dcc.Graph(id='barchart_by_time', figure={}),
        html.H2(children='PieChart analysis', style={'text-align':'left'}),
        html.Br(),
        dcc.Graph(id='PieChart_id', figure={})
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
        dcc.Graph(id='threshold_overview_line_id', figure={})
        ]),
       
])


####Callback for connecting components

@app.callback(
    Output(component_id='map_polluant_overview', component_property='figure'),
    [Input(component_id='radio_polluant__for_map_id', component_property='value'),
    Input(component_id='animation_type_id', component_property='value'),]
)
def update_map_overview(gaz, animation):
    fig = {}
    if animation=="Year":
        fig = px.scatter_mapbox(df_air,
                 lat="Latitude",
                 lon="Longitude",
                 animation_frame="Year",
                 color=gaz,
                 size="PM10",
                  height=800,
                 color_continuous_scale=px.colors.sequential.Turbo, zoom=10)
    else:
        fig = px.scatter_mapbox(df_air,
                 lat="Latitude",
                 lon="Longitude",
                 animation_frame="Year_month",
                 color=gaz,
                 size="PM10",
                  height=800,
                 color_continuous_scale=px.colors.sequential.Turbo, zoom=10)
    return fig


"""
 dcc.Tabs(id="tabs", value='tab-1', children=[
                 dcc.Tab(label='Concentration details by polluant', value='tab-1'),
                 dcc.Tab(label='Concentration details by station', value='tab-2'),
             ]),
             html.Div(id='tabs-content'),
    
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div(id="main_div")
    elif tab == 'tab-2':
        return  html.Div([
        html.H2(children='PieChart 2 analysis', style={'text-align':'left'}),
        html.Br(),
        dcc.Graph(id='PieChart_id2', figure=glo.piechart_overview(df_air))
     ]),
"""


@app.callback(
    [Output(component_id='barchart1', component_property='figure'),
    Output(component_id='PieChart_id', component_property='figure'),
     Output(component_id='dropdown_day', component_property='options'),
     #Output(component_id='dropdown_day', component_property='value'),
     Output(component_id='barchart_by_time', component_property='figure'), ],
    [
     Input(component_id='radio_polluant_id', component_property='value'),
     Input(component_id='dropdown_years', component_property='value'),
     Input(component_id='dropdown_months', component_property='value'),
     Input(component_id='dropdown_day', component_property='value'),
      ]
)
def update_graph(gaz, year, month, day):
    res = False

    ##filter dataframe with year value selected by user
    if year and month:
        days = prp.generate_days(year, month, data)
        mth = str(year)+"-"+prp.months_to_number[month]
        df =df_air.copy()
        df = df[(df["Year"]==str(year)) & (df["Month"]==prp.months_to_number[month]) ]
        ## prepare the figure according to the filtered data
        fig = px.bar(df, x='Short_address', y=gaz,
         title="Mean of pollutions grouped by address station and year", color=gaz,
         color_continuous_scale=px.colors.sequential.Turbo,
          labels={"Short_address":"Station name"})
        

        # Plotly Express
        fig2 = px.pie(df, values=gaz, names='Short_address', title='Contribution of the polluant by stations')
        if day:
            data_by_hour = data[(data['Measurement date'].str.split(' ').map(lambda  x:x[0])==day)].copy()
            data_by_hour['Day_time']=data_by_hour['Measurement date'].str.split(' ').map(lambda x:x[1])
            fig4 = px.bar(data_by_hour, x='Short_address', y='NO2',
             title="Mean of pollutions by day", color='NO2',
              animation_frame="Day_time",
              color_continuous_scale=px.colors.sequential.Turbo,
               labels={"Short_address":"Station name"})
            res = fig, fig2, days, fig4
        else: 
            res = fig, fig2, days, {}
    return res

@app.callback(Output(component_id='threshold_overview_line_id', component_property='figure'),
             Input(component_id='radio_polluant_tab3_id', component_property='value'),)
def update_threshold_linechart(gaz):
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
    return fig



if __name__ == '__main__':
    app.run_server(debug=True,threaded=True)