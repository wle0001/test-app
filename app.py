'''
import os

import dash
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    html.H2('Hello World'),
    dcc.Dropdown(
        id='dropdown',
        options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
        value='LA'
    ),
    html.Div(id='display-value')
])

@app.callback(dash.dependencies.Output('display-value', 'children'),
              [dash.dependencies.Input('dropdown', 'value')])
def display_value(value):
    return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True)
'''
import plotly.express as px
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import json

# Load Data
#df = px.data.tips()
df = pd.read_csv('FcstCompare.csv', parse_dates=True)

with open('../shps/AEZs.geojson') as f:
    counties = json.load(f)
    
for feature in counties["features"]:
    feature['id'] = str(feature['properties']['COUNTY'])
    

# Build App
app = JupyterDash(__name__)
app.layout = html.Div([
    html.H1("RHEAS-DSSAT Demo"),
    
    dcc.Dropdown(
            id='fcst-dropdown', clearable=False,
            value='fcst_dates', options=[
                {'label': f, 'value': f}
                for f in df['fcst_date'].unique()
            ]),
    
    dcc.Graph(id = 'map'),
    
    dcc.Graph(id='graph'),
    
    dcc.Dropdown(
        id='cnty-dropdown', clearable=False,
        value='fcst_dates', options=[
            {'label': c, 'value': c} for c in df['County'].unique()
            ]),
    
    dcc.Graph(id='plot'),
    
   
    
])

# Define callback to update graph
@app.callback(
    Output('map', 'figure'),
    [Input("fcst-dropdown", "value")]
)
def update_figure(fcst_date):
    filtered_df = df[df.fcst_date == fcst_date]
    
    mfig = px.choropleth_mapbox(filtered_df, geojson=counties, locations='County', color='avg_yield',
    color_continuous_scale="RdYlGn",
    range_color=(0, 3000),
    mapbox_style="carto-positron",
    zoom=5, center = {"lat": 0.1, "lon": 37.8},
    opacity=0.7,labels={'avg_yield':'Average Yield'})
                              
    mfig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return mfig


@app.callback(
    Output('graph', 'figure'),
    [Input("fcst-dropdown", "value")]
)
def update_figure(fcst_date):
    filtered_df = df[df.fcst_date == fcst_date]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
    name='Yield',
    x = filtered_df['County'],
    y=filtered_df['avg_yield'],
    error_y= dict(type='data', array=filtered_df['std_yield'].values)
    ))
    
    fig.update_layout

    return fig

# Define callback to update graph
@app.callback(
    Output('plot', 'figure'),
    [Input("cnty-dropdown", "value")]
)
def update_figure(cnty):
    filtered_df = df[df.County == cnty]
    
    #return px.bar(filtered_df, x="County", y="avg_yield"
    return px.line(filtered_df, x="fcst_date", y="avg_yield", title='Average Yield')
    
# Run app and display result inline in the notebook


app.run_server(mode='external')

