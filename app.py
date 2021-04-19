# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

"""
This application creates a simple visualization to show  gene expression
value over time.

The webpage is part of the zombie gene project. Please refer to teh below
article.

PI: Jeffrey Loeb
Project lead by: Fabian Dachet
Platform developed by: Biswajit Maharathi
contact: bmahar2@uic.edu

"""
from base64 import b64encode
from io import StringIO
from dash_extensions import Download
import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.figure_factory as ff

import pandas as pd

# read the CSV file for the data
genedata = pd.read_csv('data4.csv')

# format the raw data
genedata_insert = [
    (row + 1, gdata[0], gdata[3:].tolist(), gdata[1],gdata[2].split('[')[0])
    for row, gdata in genedata.iterrows()]

genedata_insert = pd.DataFrame(genedata_insert, columns=['geneid', 'genename', 'genexpression', 'Ensemble', 'Genedescription'])
genedata_names = genedata_insert[['geneid', 'genename','Genedescription']].copy()
genedata_names['genenamedesc'] = genedata_names['genename'] + '(' + genedata_names['Genedescription'] + ')'
genename_selection = [{"label": gName[3], "value": gName[0]} for idx, gName in genedata_names.iterrows()]

xtimevalues = [0, 1, 2, 4, 8, 12, 24]

# read the logo
image_filename = 'UINeurorepository.jpg'
encoded_image = b64encode(open(image_filename, 'rb').read())

# associate the bootstrap style sheet for dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="Postmortem human cortex gene calculator")

headerimage = dbc.Container(
    [
        html.Img(src='data:image/jpg;base64,{}'.format(encoded_image.decode()), alt="UI Neurorepository",
                 style={'height': '80%', 'width': '80%'}),
    ]
)

introduction = dbc.Jumbotron(
    [
        html.H1("Postmortem human cortex gene calculator", className="display-5"),
        html.Hr(className="my-2"),
        html.P("Time-Dependent Changes in Gene Expression of the Human Neocortex",
               className="lead",
               ),
    ]
)

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label(['Enter one or more ', html.A('Ensembl Gene', href='https://grch37.ensembl.org/index.html'), ' Annotations']),
                dcc.Dropdown(
                    id="GeneName",
                    options=genename_selection,
                    value=[1],
                    placeholder="Please select a gene",
                    multi=True
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Select Plot Option"),
                dcc.Dropdown(
                    id="PlotType",
                    options=[
                        {'label': 'Gene Expression (Absolute)', 'value': 'GEA'},
                        {'label': 'Gene Expression (Relative to max expression)', 'value': 'GEE'},
                        {'label': 'Gene Expression (Relative to expression at time zero)', 'value': 'GET'}
                    ],
                    value='GET',
                    placeholder="Please select a gene"
                ),
            ]
        ),
    ],
    body=True,
)

ftest = dbc.Row(
    [
        html.Br(),
    ]
)
footer = dbc.Jumbotron(
    [
        html.H4(
            "Article: Selective time-dependent changes in activity and cell-specific gene expression in human postmortem brain",
            className="display-5"),
        html.Hr(className="my-2"),
        html.P("Abstract: As a means to understand human neuropsychiatric disorders from human brain samples, "
               "we compared the transcription patterns and histological features of postmortem brain to fresh human "
               "neocortex isolated immediately following surgical removal. Compared to a number of neuropsychiatric "
               "disease-associated postmortem transcriptomes, the fresh human brain transcriptome had an entirely "
               "unique transcriptional pattern. To understand this difference, we measured genome-wide transcription "
               "as a function of time after fresh tissue removal to mimic the postmortem interval. Within a few "
               "hours, a selective reduction in the number of neuronal activity-dependent transcripts occurred with "
               "relative preservation of housekeeping genes commonly used as a reference for RNA normalization. Gene "
               "clustering indicated a rapid reduction in neuronal gene expression with a reciprocal time-dependent "
               "increase in astroglial and microglial gene expression that continued to increase for at least 24 h "
               "after tissue resection. Predicted transcriptional changes were confirmed histologically on the same "
               "tissue demonstrating that while neurons were degenerating, glial cells underwent an outgrowth of "
               "their processes. The rapid loss of neuronal genes and reciprocal expression of glial genes highlights "
               "highly dynamic transcriptional and cellular changes that occur during the postmortem interval. "
               "Understanding these time-dependent changes in gene expression in post mortem brain samples is "
               "critical for the interpretation of research studies on human brain disorders.",
               className="lead",
               ),
        html.P(dbc.Button("Read article", color="primary", className="mr-1",
                          href="https://doi.org/10.1038/s41598-021-85801-6", external_link=True)),

        html.Div(
            [
                Download(id="download"),
                html.P(dbc.Button("Download full dataset",
                                  id="save-button", color="success", className="mr-1")),
            ]
        )
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(headerimage, md=12),
            ],
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(introduction, md=12),
            ],
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(controls, md=12),
            ],
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="gene-graph"), md=12),
            ],
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="gene-table"), md=12),
            ],
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(ftest, md=12),
            ],
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(footer, md=12),
            ],
            align="center",
        ),
    ],
    fluid=True,
)


@app.callback(
    Output("gene-graph", "figure"),
    [
        Input("GeneName", "value"),
        Input("PlotType", "value"),
    ],
)
def make_graph(gvals, gtype):
    # get the data
    xdata = xtimevalues
    ydata = genedata_insert[genedata_insert['geneid'].isin(gvals)]

    # create figure
    derive_data = pd.DataFrame(columns=['Time', 'Expression', 'Gene'])
    for idx, gdata in ydata.iterrows():
        temp_data = pd.DataFrame()
        if gtype == 'GEA':
            ygdata = gdata[2] # value column

        elif gtype == 'GEE':
            ygdata = [i * 100 / max(gdata[2]) for i in gdata[2]]

        elif gtype == 'GET':
            ygdata = [i * 100 / gdata[2][0] for i in gdata[2]]

        temp_data['Time'] = xdata
        temp_data['Expression'] = ygdata
        temp_data['Gene'] = gdata[1]

        derive_data = derive_data.append(temp_data, ignore_index=True)

    if derive_data.empty:
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "Please select a gene",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 28
                        }
                    }
                ]
            }
        }
    else:
        fig = px.line(derive_data,
                      x="Time", y="Expression", color='Gene')

        # Edit the trace properties
        fig.update_traces(line=dict(width=5)
                          )
        # Edit the layout
        fig.update_layout(title='<b>Relative Postmortem Gene Expression </b>',
                          yaxis_title='<b>Gene Expression</b>',
                          xaxis=dict(
                              title='<b>Postmortem Interval (Hours)</b>',
                              tickmode='array',
                              tickvals=xdata,
                              ticktext=[str(i) for i in xdata]
                          )
                          )

        return fig


@app.callback(
    Output("gene-table", "figure"),
    [
        Input("GeneName", "value"),
        Input("PlotType", "value"),
    ],
)
def make_table(gvals, gtype):
    # get the data
    xdata = xtimevalues
    ydata = genedata_insert[genedata_insert['geneid'].isin(gvals)]

    # create figure
    if ydata.empty:
        return {
            "layout": {
                "xaxis": {
                    "visible": False
                },
                "yaxis": {
                    "visible": False
                },
                "annotations": [
                    {
                        "text": "Please select a gene",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 28
                        }
                    }
                ]
            }
        }
    else:
        derive_data = list()
        table_columns = ['Gene']
        table_columns.extend([str(i) + ' Hours' for i in xdata])
        derive_data.append(table_columns)

        for idx, gdata in ydata.iterrows():
            temp_data = [gdata[1]]
            if gtype == 'GEA':
                ygdata = gdata[2]

            elif gtype == 'GEE':
                ygdata = [round(i * 100 / max(gdata[2])) for i in gdata[2]]

            elif gtype == 'GET':
                ygdata = [round(i * 100 / gdata[2][0]) for i in gdata[2]]

            temp_data.extend(ygdata)
            derive_data.append(temp_data)

        fig = ff.create_table(derive_data, height_constant=20)

        return fig


@app.callback(
    Output("download", "data"),
    Input("save-button", "n_clicks"))
def download_as_csv(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    download_buffer = StringIO()
    genedata.to_csv(download_buffer, index=False)
    download_buffer.seek(0)
    return dict(content=download_buffer.getvalue(), filename="gene_expression_dataset.csv")


if __name__ == '__main__':
    app.run_server(debug=False)
