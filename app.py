#!/usr/bin/env python3
# coding: utf-8


#Imports for data handling
# import os

# from os import walk, listdir
import pandas as pd
import numpy as np
# import ipywidgets as widgets

import plotly
import plotly.graph_objs as go
from plotly import tools

from pathlib import Path
import glob
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


p = Path('.')
data_filepath = list(p.glob('./MATLAB/Sx@area/*mat.h5'))
fname=[]

for index, csv in enumerate(data_filepath):
    fname.append(data_filepath[index].name)

# Variables that we will use constantly
dispang = range(-90,95,5)
colorPattern = ['r','g','b']

data_dict = { i : [] for i in fname }

# while using Dash template use offline, if not use the other one called Materialize
#app = dash.Dash('/assets/offline')
app = dash.Dash('/assets/materialize_min')
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    html.Div([
        html.H2('Poincare Spheres (PS) for reflectance of paper samples ',
                style={'float': 'center',
                       }),
        ]),
    html.Div([
        dcc.Checklist(id='sensors',
            options=[
                {'label': 'Red Sensor', 'value': 'r'},
                {'label': 'Green Sensor', 'value': 'g'},
                {'label': 'Blue Sensor', 'value': 'b'}
            ],
            values=['r', 'g', 'b'],
            inputStyle={'input':'checkbox'},
            labelStyle={'display': 'inline-block','width' : '30%',
                        'margin-bottom': '10px','height':'10%','font-size': '18pt','font-weight':'normal','input':'checkbox'},
            #style={'margin-top': '10px','top':'1px','left':'0','height':'10%','width' : '90%'}#"height" : "3vh", "width" : "100vw"}
            ),
    ],style={'margin-top': '10px','top':'1px','left':'0','height':'50%','width' : '90%'}),
    dcc.Dropdown(id='poincare-spheres-names',
                 options=[{'label': s.split('Data')[0], 'value': s}
                          for s in data_dict.keys()],
                 value=[],
                 multi=True
                 ),
    html.Div(children=html.Div(id='graphs'), className='row'),
    dcc.Slider(
            id='angle-detector--slider',
            min=-90,
            max=90,
            step=5,
            value=0,
            marks={i: '{}'.format(i) for i in dispang}
        ),
    ], className="container",style={'width':'95 %','margin-left':10,'margin-right':10,'max-width':50000})



@app.callback(
    Output('graphs', 'children'),
    [Input('angle-detector--slider', 'value'),
    Input('poincare-spheres-names','value'),
    Input('sensors','values')]
)

def update_plot(angle,data_names,color):
    def addfigure(sencol,dataset):        
        if len(sencol)> 2:
            figout={'data': dataset.data,'layout' : dataset.layout}
        elif len(sencol)==2:
            if ('r' and 'g' in sencol):
                figout={'data': (dataset.data[0],dataset.data[1]),'layout' : dataset.layout}
            elif ('r' and 'b' in sencol):
                figout={'data': (dataset.data[0],dataset.data[2]),'layout' : dataset.layout}
            else:
                figout={'data': (dataset.data[1],dataset.data[2]),'layout' : dataset.layout}
        elif len(sencol)==1:
            figout={'data': (dataset.data[colorPattern.index(sencol[0])],),'layout' : dataset.layout}
        else:
            figout={'data': [],'layout' : dataset.layout}
                
        return figout
    
    graphs = []
    
    # In[4]:


    # recursive function to extract the data in the form the spheres are generated
    def readtraces(dataname,slideang):
        fullpath = './MATLAB/Sx@area/'+dataname
        trace0 = go.Scatter3d(
        x = np.array(pd.read_hdf(fullpath,'xr').loc[dispang.index(slideang)]),
        y = np.array(pd.read_hdf(fullpath,'yr').loc[dispang.index(slideang)]),
        z = np.array(pd.read_hdf(fullpath,'zr').loc[dispang.index(slideang)]),
        marker={'color': 'red', 'size': 1}, mode='markers', name='Red sensor'
        )

        trace1 = go.Scatter3d(
        x = np.array(pd.read_hdf(fullpath,'xg').loc[dispang.index(slideang)]),
        y = np.array(pd.read_hdf(fullpath,'yg').loc[dispang.index(slideang)]),
        z = np.array(pd.read_hdf(fullpath,'zg').loc[dispang.index(slideang)]),
        marker={'color': 'green', 'size': 1}, mode='markers', name='Green sensor'
        )

        trace2 = go.Scatter3d(
        x = np.array(pd.read_hdf(fullpath,'xb').loc[dispang.index(slideang)]),
        y = np.array(pd.read_hdf(fullpath,'yb').loc[dispang.index(slideang)]),
        z = np.array(pd.read_hdf(fullpath,'zb').loc[dispang.index(slideang)]),
        marker={'color': 'blue', 'size': 1}, mode='markers', name='Blue sensor'
        )

        figText = fullpath.split('Sx@area/')
        figText = figText[1].split('@')
        
        layout = go.Layout(
            autosize=True,
            #width=300,
            #height=300,
            margin=go.layout.Margin(
                l=10,
                r=10,
                b=10,
                t=40,
                pad=20
            ),
            title = '<b>{}@{}deg</b> {}'.format(figText[0],figText[1][0:2],slideang),
            scene = dict(
            zaxis = dict(
                title = 'S3'
            ),
            yaxis = dict(
                title = 'S2'
            ),
            xaxis = dict(
                title = 'S1'
            ),)
        )
        data = [trace0, trace1, trace2]

        fig = go.Figure(data=data, layout=layout)
        return fig

    """
    This is a function to select the poincare 
    sphere with the selection of the angle the
    detector is placed around the sample
    """
    
    if len(data_names)>2:
        class_choice = 'col s12 m6 l4'
    elif len(data_names) == 2:
        class_choice = 'col s12 m6 l6'
    else:
        class_choice = 'col s12'
        
    for data_name in data_names:
        #tempFig = []
        #tempFig = data_dict[data_name]
        df = readtraces(data_name,angle)        
    
        graphs.append(html.Div(dcc.Graph(
            id=data_name,
            #animate=True,
            figure = addfigure(color,df),
            ), className=class_choice))

    return graphs
    
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

if __name__ == '__main__':
    app.run_server(debug=True)