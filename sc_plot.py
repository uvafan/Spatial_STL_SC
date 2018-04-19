'''
Code-In-Progress for data visualization 
Currently have (x,y) node coordinates, (x1,y1),(x2,y2) edge coordinates saved
         in a pandas dataframe. Just need to plot, running into server error w/plotly.
'''

import osmnx as ox
import sc_lib
import plotly as py
from plotly.graph_objs import *
import pandas as pd
import Sample
#py.tools.set_credentials_file(username='Timothy_Davison', api_key='hmNOkvh7tz5GGvDnRsqL')
py.plotly.sign_in('Timothy_Davison', 'hmNOkvh7tz5GGvDnRsqL')

G = ox.graph_from_point((56.21728389, 10.2336194), distance=2000)
graph = Sample.graph_from_OSMnx(G)

plot_nodes = []
for item in graph.nodes:
    item.middle_coordinate['x'] = ((graph.edge_dict[item.intersections[0]].coordinates['x'] + 
                              graph.edge_dict[item.intersections[1]].coordinates['x'])/2.0)
    item.middle_coordinate['y'] = ((graph.edge_dict[item.intersections[0]].coordinates['y'] +
                          graph.edge_dict[item.intersections[0]].coordinates['y'])/2.0)
    plot_nodes.append({'Identifier': item.identifier, 'x': item.middle_coordinate['x'], 
                       'y': item.middle_coordinate['y']})
df_nodes = pd.DataFrame(plot_nodes)

plot_edges = []
for item in graph.nodes:
    for successor in item.successors:
        plot_edges.append({'start_lon':item.middle_coordinate['x'], 'end_lon':successor.middle_coordinate['x'],
                           'start_lat':item.middle_coordinate['y'], 'end_lat':successor.middle_coordinate['y']})
df_edges = pd.DataFrame(plot_edges)


nodes = [ dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = df_nodes['x'],
        lat = df_nodes['y'],
        hoverinfo = 'text',
        text = df_nodes['Identifier'],
        mode = 'markers',
        marker = dict( 
            size=2, 
            color='rgb(255, 0, 0)',
            line = dict(
                width=3,
                color='rgba(68, 68, 68, 0)'
            )
        ))]
        
flight_paths = []
for i in range( len( df_edges ) ):
    flight_paths.append(
        dict(
            type = 'scattergeo',
            locationmode = 'USA-states',
            lon = [ df_edges['start_lon'][i], df_edges['end_lon'][i] ],
            lat = [ df_edges['start_lat'][i], df_edges['end_lat'][i] ],
            mode = 'lines',
            line = dict(
                width = 1,
                color = 'red',
            ),
            #opacity = float(df_edges['cnt'][i])/float(df_edges['cnt'].max()),
        )
    )
    
layout = dict(
        title = 'Plotted City Data -- 4/10/18',
        showlegend = False, 
        geo = dict(
            scope='europe',
            projection=dict( type='azimuthal equal area' ),
            showland = True,
            landcolor = 'rgb(243, 243, 243)',
            countrycolor = 'rgb(204, 204, 204)',
        ),
    )
    
fig = dict( data=flight_paths + nodes, layout=layout )
#py.plotly.image.save_as(fig, 'SC_plot.png')
py.plotly.plot(fig, filename='Hello World')
#plotly.offline.plot(fig)