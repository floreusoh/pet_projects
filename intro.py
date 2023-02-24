import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from plotly.subplots import make_subplots


app = Dash(__name__)

data = pd.read_csv("Youth_Tobacco_Survey.csv")

df = data.groupby(['State', 'Type of smoking', 'Gender', 'YEAR', 'Period', 'State_code'])[['pct of young people']].mean()
df.reset_index(inplace=True)
smoking_types = ['Cigarette Use', 'Smokeless Tobacco Use', 'Cessation']

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1("Youth Tobacco Survey (YTS)", style={'text-align': 'center', 'font-weight': 'normal'}, className="header-title"
                ),
                html.H3("The YTS was developed to provide states with comprehensive data on both middle school and high school students regarding tobacco use,"
                        " exposure to environmental tobacco smoke, smoking cessation. The YTS uses a two-stage cluster sample design to produce representative"
                        " samples of students in middle schools (grades 6–8) and high schools (grades 9–12).", style={'font-weight': '30'}
                )
            ],
            className="header",style={'fontSize': "18px"},
        ),

        html.Div(
            children=[
                dcc.Graph(id='pie', figure={},style={'width': "100%", "height" : "30%", 'display': 'inline-block'}),
                dcc.RadioItems(
                    id="slct_impact",
                    options=[{"label": x, "value":x} for x in smoking_types],
                    value="Cigarette Use",
                    style={'width': "40%", 'height' : '100%', 'display': 'inline-block'},
                    inline=True),
                dcc.Dropdown(id="slct_period",
                    options=[
                        {"label": "1999-2004", "value": 1},
                        {"label": "2005-2010", "value": 2},
                        {"label": "2011-2017", "value": 3}],

                    multi=False,
                    value=1,
                    style={'width': "40%", 'display': 'inline-block'}
                ),
            ],
            className = 'dropdown', style={'fontSize': "18px",'textAlign': 'center'}
        ),
        html.Div(
            children=[
                html.Div(
                children = dcc.Graph(
                    id='smoking_map',
                    figure={}
                    ),
                style={'width': '50%', 'display': 'inline-block'}
                ),
                html.Div(
                children =  dcc.Graph(
                    id='smoking_timeline',
                    figure={}),
                style={'width': '50%', 'display': 'inline-block'}
                ),
                html.Div(
                children =  dcc.Graph(
                    id='smoking_barplot',
                    figure={}),
                style={'width': '100%', 'display': 'inline-block'}
                )
            ],
            className = 'double-graph'
        )
])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
     Output(component_id='pie', component_property='figure'),
    [Input(component_id='slct_period', component_property='value')]
)
def update_graph(option_slctd1):
    dff = df.copy()
    dff = dff[dff['Period'] == option_slctd1]
    dff = dff[(dff['Gender'] == 'Male') | (dff['Gender'] == 'Female')]
    fig = make_subplots(1, 3, specs=[[{'type':'domain'}, {'type':'domain'}, {'type':'domain'}]],
                    subplot_titles=['Cigarette Use', 'Smokeless Tobacco Use', 'Cessation'])
    cig = dff[dff['Type of smoking'] == 'Cigarette Use']
    smok = dff[dff['Type of smoking'] == 'Smokeless Tobacco Use']
    ces = dff[dff['Type of smoking'] == 'Cessation']
    fig.add_trace(go.Pie(labels=cig['Gender'], values=cig['pct of young people'], name='Cigarette Use',
                    hole=0.3), 1, 1)
    fig.add_trace(go.Pie(labels=smok['Gender'], values=smok['pct of young people'], name='Smokeless Tobacco Use',
                    hole=0.3), 1, 2)
    fig.add_trace(go.Pie(labels=ces['Gender'], values=ces['pct of young people'],name='Cessation',
                    hole=0.3, marker_colors=[px.colors.qualitative.Prism[0], px.colors.qualitative.Prism[1]]), 1, 3)
    fig.update_layout(height=350, paper_bgcolor="#F5F5F5")
    return fig
@app.callback(
     Output(component_id='smoking_map', component_property='figure'),
    [Input(component_id='slct_period', component_property='value'),
     Input(component_id='slct_impact', component_property='value')]
)
def update_graph(option_slctd1, option_slctd2):

    dff = df.copy()
    dff = dff[dff["Period"] == option_slctd1]
    dff = dff[dff["Type of smoking"] == option_slctd2]

    chor = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='State_code',
        scope="usa",
        color='pct of young people',
        hover_data=['State', 'pct of young people'],
        color_continuous_scale="twilight",
        labels={'Pct of smoking youth': '% of Young Respondents'},
        template='ggplot2',
    )
    chor.update_layout(paper_bgcolor="#F5F5F5")
    return chor

@app.callback(
     Output(component_id='smoking_timeline', component_property='figure'),
    [Input(component_id='slct_impact', component_property='value')])
def update_graph(o):

    dff = data.copy()
    dff = dff.groupby(['Type of smoking', 'YEAR'])[['pct of young people']].mean().reset_index()

    line = px.line(
        data_frame=dff,
        x='YEAR',
        y='pct of young people',
        color='Type of smoking',
        template='ggplot2',
        color_discrete_sequence=[px.colors.qualitative.Prism[0],
                                 px.colors.qualitative.Prism[1],
                                 px.colors.qualitative.Prism[7]]
    )
    line.update_layout(paper_bgcolor="#F5F5F5")
    return line

@app.callback(
    Output(component_id='smoking_barplot', component_property='figure'),
    [Input(component_id='slct_period', component_property='value'),
    Input(component_id='slct_impact', component_property='value')]
)
def update_graph(option_slctd1, option_slctd2):

    dff = df.copy()
    dff = dff[dff['Period'] == option_slctd1]
    dff = dff[dff['Type of smoking'] == option_slctd2]
    dff = dff.groupby('State')[['pct of young people']].mean().reset_index().sort_values(by='pct of young people')
    bar = px.bar(
        dff,
        y='State',
        x='pct of young people',
        orientation='h',
        color='pct of young people',
        template='ggplot2',
        labels={'pop':'population of Canada'},
        color_continuous_scale='twilight',
        )
    bar.update_layout(paper_bgcolor='#F5F5F5', height=800,)
    return bar
# ------------------------------------------------------------------------------


if __name__ == '__main__':
    app.run_server(debug=True)