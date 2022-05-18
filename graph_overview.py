#overview

#### Overview dataframe##############
def polluant_overview_barchart():
    """fig = px.bar(df_air, x='Short_address', y=['NO2','SO2','O3',],
                     title="Mean of pollutions grouped by address station and year")
                fig.show()
    """
    fig = px.bar(df_air, x='Short_address', y='NO2',
     title="Mean of pollutions grouped by address station", labels={"Short_address":"Station name"})

def polluant_overview_line():
    # Create traces
    #print(df_air.head(700))
   
    df_sorted = data.copy().groupby(['Year_month','Year','Month'], as_index=False).agg({'SO2':'mean',
     'NO2':'mean', 'O3':'mean', 'CO':'mean', 'PM10':'mean', 'PM2.5':'mean'}).sort_values(by="Year_month")
    #df_sorted.to_csv('df_sorted.csv')
    fig= go.Figure()
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::2], y=df_sorted['NO2'].iloc[::2],
                    mode='lines+markers',
                    name='Polluant NO2')),
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::2], y=df_sorted['SO2'].iloc[::2],
                    mode='lines+markers',
                    name='Polluant SO2'))
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::2], y=df_sorted['CO'].iloc[::2],
                    mode='lines+markers',
                    name='Polluant CO'))
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::2], y=df_sorted['O3'].iloc[::2],
                    mode='lines+markers',
                    name='Polluant O3'))


    return fig

def particulate_matter_overview_line():
    df_sorted = data.copy().groupby(['Year_month','Year','Month'], as_index=False).agg({'PM10':'mean',
     'PM2.5':'mean'}).sort_values(by="Year_month")
    #df_sorted.to_csv('df_sorted.csv')
    fig= go.Figure()
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::2], y=df_sorted['PM10'].iloc[::2],
                    mode='lines+markers',
                    name='Polluant PM10'))
    fig.add_trace(go.Scatter(x=df_sorted['Year_month'].iloc[::2], y=df_sorted['PM2.5'].iloc[::2],
                    mode='lines+markers',
                    name='Polluant PM2.5'))

    

    return fig

def map_overview_by_station():
    map_overview_fig = px.scatter_mapbox(df_air,
             lat="Latitude",
             lon="Longitude",
             animation_frame="Year",
             color="CO",
             size="PM10",
              height=800,
             color_continuous_scale=px.colors.sequential.Turbo, zoom=10)
    #map_overview_fig.show()
    return map_overview_fig

def piechart_overview():
    df = df_air.copy()
    fig = px.pie(df, values='CO', names='Short_address', title='Contribution of the polluant by stations')

    return fig 