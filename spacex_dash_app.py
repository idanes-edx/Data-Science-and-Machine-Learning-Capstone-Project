# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


# --------------------------------------------
launch_sites_df = spacex_df.groupby(['Launch Site'], as_index=False).first()
launch_sites_df = launch_sites_df[['Launch Site']]
launch_sites_df["Key Value"] = launch_sites_df['Launch Site']


site_options = launch_sites_df.to_dict("records")
site_options.insert(0, {"Launch Site": 'All Sites', "Key Value": "ALL"})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                               
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                           #options=[{'label': 'All Sites', 'value': 'ALL'}, {'label': 'site1', 'value': 'site1'}, ],
                                            options=[{'label': i['Launch Site'], 'value': i['Key Value']} for i in site_options],
                                            value='ALL',
                                            placeholder="Select a Launch Site here",
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0',
                                                    2000: '2000',
                                                    4000: '4000',
                                                    6000: '6000',
                                                    8000: '8000',
                                                    10000: '10000'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    
    if entered_site == 'ALL':
        fig = px.pie(spacex_df[spacex_df['class'] == 1].groupby(['Launch Site'])['class'].count().reset_index(name='count'), 
        values='count', 
        names='Launch Site', 
        title='Total Success Launches by Site')
        return fig
    else:
        fig = px.pie(spacex_df[spacex_df['Launch Site'] == entered_site].groupby(['class'])['Launch Site'].count().reset_index(name='count'),
        values='count', 
        names='class', 
        title='Total Success Launches for site ' +  entered_site)
        return fig
        
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'), 
              Input(component_id="payload-slider", component_property="value")
              )
def get_scatter_chart(entered_site, slider_range):
    
    if entered_site == 'ALL':

        low, high = slider_range
        mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
        fig = px.scatter(spacex_df[mask], x="Payload Mass (kg)", y="class", 
        color="Booster Version Category",
        title="Correlation between Payload and Success for all Sites")
        return fig

    else:

        low, high = slider_range
        mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high) & (spacex_df['Launch Site'] == entered_site)
        fig = px.scatter(spacex_df[mask], x="Payload Mass (kg)", y="class", 
        color="Booster Version Category",
        title="Correlation between Payload and Success for site " +  entered_site)
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server()



