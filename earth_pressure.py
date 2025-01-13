import os
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objs as go
import time


app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

app.title = 'Earth Pressure'
app._favicon = ('assets/favicon.ico')

# Updated layout with sliders on top and layer properties below
app.layout = html.Div([
    # Main container
    html.Div(style={'display': 'flex', 'flexDirection': 'row', 'width': '100%'}, children=[
        # Control container (sliders)
        html.Div(id='control-container', style={'width': '25%', 'padding': '2%', 'flexDirection': 'column'}, children=[
            html.H1('Earth Pressure', className='h1'),

            # Add the update button
            html.Button("Update Graphs", id='update-button', n_clicks=0, style={'width': '100%', 'height': '5vh', 'marginBottom': '1vh'}),

            # Sliders for each layer
            html.Div(className='slider-container', children=[
                # Layer 1 Slider
                html.Label(children=[
                    'Z', html.Sub('1'), ' (m)', 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Thickness of layer 1.', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='z-1', min=0, max=20, step=0.25, value=4,
                    marks={i: f'{i}' for i in range(0, 21, 5)},
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),

                # Layer 2 Slider
                html.Label(children=[
                    'Z', html.Sub('2'), ' (m)', 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Thickness of layer 2.', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='z-2', min=0, max=20, step=0.25, value=4,
                    marks={i: f'{i}' for i in range(0, 21, 5)},
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),

                # Layer 3 Slider
                html.Label(children=[
                    'Z', html.Sub('3'), ' (m)', 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Thickness of layer 3.', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='z-3', min=0, max=20, step=0.25, value=4,
                    marks={i: f'{i}' for i in range(0, 21, 5)},
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),

                # Water table slider
                html.Label(children=[
                    "Water Table", 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Water table depth from the surface.', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='water-table', min=0, max=20, step=0.25, value=1,
                    marks={i: f'{i}' for i in range(0, 21, 5)},
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),

            ]),
        
        # Properties for each layer
        html.Div(className='layer-properties', children=[
                # foundation Properties
                html.H3('Foundation:', style={'textAlign': 'left'}, className='h3'),
                html.Label(["a", 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Length of the footing', className='tooltiptext')
                            ]),'(m)'], className='input-label'),
                dcc.Input(id='a', type='number', value=4, step=0.1, className='input-field'),
                html.Label(["b", 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Width of the footing', className='tooltiptext')
                            ]),'(m)'], className='input-label'),
                dcc.Input(id='b', type='number', value=2, step=0.1, className='input-field'),
                html.Label(["q", 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Footing load', className='tooltiptext')
                            ]),'(kPa)'], className='input-label'),
                dcc.Input(id='q', type='number', value=100, step=1, className='input-field'),


                # Layer 1 Properties
                html.H3('Layer 1:', style={'textAlign': 'left'}, className='h3'),
                html.Label([f'γ', html.Sub('d'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Dry unit weight of Layer 1', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_1', type='number', value=18, step=0.01, className='input-field'),
                html.Label([f'γ', html.Sub('sat'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Saturated unit weight of Layer 1', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_r_1', type='number', value=19, step=0.01, className='input-field'),
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'whiteSpace': 'nowrap'}, children=[
                    html.Label([f'γ′', 
                                html.Div(className='tooltip', children=[
                                    html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                    html.Span('Submerged unit weight of Layer 1', className='tooltiptext')
                                ])], className='input-label', style={'marginRight': '5px'}),
                    html.Div(id='gamma_prime_1', className='input-field')  
                ]),
                html.Label([f'C', html.Sub('c'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Compression index of Layer 1', className='tooltiptext')
                            ])], className='input-label'),
                dcc.Input(id='C_c_1', type='number', value=0.1, step=0.001, className='input-field'),
                html.Label([f'C', html.Sub('s'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Swelling index of Layer 1', className='tooltiptext')
                            ])], className='input-label'),
                dcc.Input(id='C_s_1', type='number', value=0.05, step=0.0001, className='input-field'),
                html.Label([f'e', html.Sub('0'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('initial void ratio of Layer 1', className='tooltiptext')
                            ])], className='input-label'),
                dcc.Input(id='e_0_1', type='number', value=2, step=0.01, className='input-field'),
                html.Label(["OCR", 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('OverConsolidation ratio of Layer 1', className='tooltiptext')
                            ])], className='input-label'),
                dcc.Input(id='OCR_1', type='number', value=1, step=0.1, className='input-field'),

                # Layer 2 Properties
                html.H3('Layer 2:', style={'textAlign': 'left'}, className='h3'),
                html.Label([f'γ', html.Sub('d'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Dry unit weight of Layer 2', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_2', type='number', value=19, step=0.01, className='input-field'),
                html.Label([f'γ', html.Sub('sat'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Saturated unit weight of Layer 2', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_r_2', type='number', value=21, step=0.01, className='input-field'),
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'whiteSpace': 'nowrap'}, children=[
                    html.Label([f'γ′', 
                                html.Div(className='tooltip', children=[
                                    html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                    html.Span('Submerged unit weight of Layer 2', className='tooltiptext')
                                ])], className='input-label', style={'marginRight': '5px'}),
                    html.Div(id='gamma_prime_2',className='input-field')  
                ]),
                html.Label([f'C', html.Sub('c'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Compression index of Layer 2', className='tooltiptext')
                            ])], className='input-label'),
                dcc.Input(id='C_c_2', type='number', value=0.1, step=0.001, className='input-field'),
                html.Label([f'C', html.Sub('s'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Swelling index of Layer 2', className='tooltiptext')
                            ])], className='input-label'),
                dcc.Input(id='C_s_2', type='number', value=0.05, step=0.0001, className='input-field'),
                html.Label([f'e', html.Sub('0'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('initial void ratio of Layer 2', className='tooltiptext')
                            ])], className='input-label'),
                dcc.Input(id='e_0_2', type='number', value=2, step=0.0001, className='input-field'),
                html.Label(["OCR", 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('OverConsolidation ratio of Layer 2', className='tooltiptext')
                            ])], className='input-label'),
                dcc.Input(id='OCR_2', type='number', value=1, step=0.1, className='input-field'),

                # Layer 3 Properties
                html.H3('Layer 3:', style={'textAlign': 'left'}, className='h3'),
                html.Label([f'γ', html.Sub('d'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Dry unit weight of Layer 3', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_3', type='number', value=18, step=0.01, className='input-field'),
                html.Label([f'γ', html.Sub('sat'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Saturated unit weight of Layer 3', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_r_3', type='number', value=19, step=0.01, className='input-field'),
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'whiteSpace': 'nowrap'}, children=[
                    html.Label([f'γ′', 
                                html.Div(className='tooltip', children=[
                                    html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                    html.Span('Submerged unit weight of Layer 3', className='tooltiptext')
                                ])], className='input-label', style={'marginRight': '5px'}),
                    html.Div(id='gamma_prime_3', className='input-field')  
                ]),
                html.Label([f'C', html.Sub('c'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Compression index of Layer 3', className='tooltiptext')
                            ])], className='input-label'),
                dcc.Input(id='C_c_3', type='number', value=0.1, step=0.001, className='input-field'),
                html.Label([f'C', html.Sub('s'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Swelling index of Layer 3', className='tooltiptext')
                            ])], className='input-label'),
                dcc.Input(id='C_s_3', type='number', value=0.05, step=0.0001, className='input-field'),
                html.Label([f'e', html.Sub('0'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('initial void ratio of Layer 3', className='tooltiptext')
                            ])], className='input-label'),
                dcc.Input(id='e_0_3', type='number', value=2, step=0.01, className='input-field'),
                html.Label(["OCR", 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('OverConsolidation ratio of Layer 3', className='tooltiptext')
                            ])], className='input-label'),
                dcc.Input(id='OCR_3', type='number', value=1, step=0.1, className='input-field'),
            ]),
        ]),

        # Graphs container
        html.Div(
            className='graph-container', 
            id='graphs-container', 
            style={
                'display': 'flex', 
                'flexDirection': 'row',  # Arrange the graphs in a row
                'width': '75%'  # Increased width to make it wider
            }, 
            children=[
                # Left column: Stack the first and second graphs
                html.Div(
                    style={'display': 'flex', 'flexDirection': 'column', 'width': '60%', 'height': '100%'}, 
                    children=[
                        # First graph (Foundation dimension)
                        html.Div(
                            style={'height': '20%', 'position': 'relative'},  # First graph takes 50% of the height
                            children=[
                                dcc.Graph(id='foundation-dimension-graph', style={'height': '100%', 'width': '100%'})
                            ]
                        ),
                        # Second graph (Soil layers)
                        html.Div(
                            style={'height': '80%'},  # Second graph takes the remaining 50% of the height
                            children=[
                                dcc.Graph(id='soil-layers-graph', style={'height': '80%', 'width': '100%'})
                            ]
                        ),
                    ]
                ),
                # Right column: The third graph (change in stress) takes the same height as the second one
                html.Div(
                    style={'display': 'flex', 'flexDirection': 'column', 'width': '40%', 'height': '100%'},  # Adjusted to take 55% of the width
                    children=[
                        html.Div(style={'height': '20%', 'position': 'relative'},
                                children=[
                                    html.Table(
                                        className='anchored-table',  # Assign a class for the table
                                        children=[
                                            html.Thead(
                                                html.Tr([
                                                    html.Th('Sublayer thickness (m)', className='table-header'),
                                                    html.Th('Total settlement (mm)', className='table-header'),
                                                ])
                                            ),
                                            html.Tbody([
                                                html.Tr([
                                                    html.Td('Reference= 0.05', className='table-cell'),
                                                    html.Td(id='sett_ref', children='', className='table-cell'),
                                                ]),
                                                html.Tr([
                                                    html.Td(
                                                        html.Div(
                                                            [
                                                                "Preferred= ",  # Label text
                                                                dcc.Input(
                                                                    id='input-factor',
                                                                    type='number',
                                                                    value=1,
                                                                    min=0.01,
                                                                    max=1,
                                                                    step=0.01,
                                                                    className='input-field'
                                                                )
                                                            ],
                                                            className='input-container'
                                                        ),
                                                        className='table-cell'
                                                    ),
                                                    html.Td(id='sett_pref', children='', className='table-cell'),
                                                ]),
                                            ])
                                        ]
                                    )
                                ]),
                        html.Div(
                            style={'height': '80%'},  
                            children=[
                                dcc.Graph(id='stress-change-graph', style={'height': '80%', 'width': '100%'}) 
                            ]
                        ),
                    ]
                )
            ]
        ),

        
        # Add the logo image to the top left corner
        html.Img(
            src='/assets/logo.png', className='logo',
            style={
                'position': 'absolute',
                'width': '15%',  # Adjust size as needed
                'height': 'auto',
                'z-index': '1000',  # Ensure it's on top of other elements
            }
        )
    ])
])

# Callback to control the bounderies of the input fields and sliders
@app.callback(
    [Output(f'gamma_prime_{i}', 'children') for i in range(1, 4)] + [Output('b', 'value')],
    [Output(f'OCR_{i}', 'value') for i in range(1, 4)],
    Output('water-table', 'max'),
    Output('input-factor', 'max'),
    [Input(f'z-{i}', 'value') for i in range(1, 4)],
    [Input(f'gamma_r_{i}', 'value') for i in range(1, 4)],
    Input('a', 'value'),
    Input('b', 'value'),
    [Input(f'OCR_{i}', 'value') for i in range(1, 4)],
    
)
def update_gamma_prime(z1, z2, z3, gamma_r1, gamma_r2, gamma_r3, a_value, b_value, OCR1, OCR2, OCR3):
    # Ensure b does not exceed a
    if b_value > a_value:
        b_value = a_value  # or return a message, e.g., "b cannot exceed a"
    
    # if one or more of z1, z2, z3 is zero set the input factor the minimum of the others
    inputfactor_max = min([value for value in (z1, z2, z3) if value != 0]) 

    # Ensure OCR is at least 1
    OCR1 = max(1, OCR1)
    OCR2 = max(1, OCR2)
    OCR3 = max(1, OCR3)

    # insure water table is not below the maximum depth
    water_table_max = z1 + z2 + z3

    # Calculate γ′ as γ_r - 9.81 for each layer
    gamma_prime1 = round(gamma_r1 - 10, 2) if gamma_r1 is not None else None
    gamma_prime2 = round(gamma_r2 - 10, 2) if gamma_r2 is not None else None
    gamma_prime3 = round(gamma_r3 - 10, 2) if gamma_r3 is not None else None

    return f"= {gamma_prime1} kN/m³", f"= {gamma_prime2} kN/m³", f"= {gamma_prime3} kN/m³", b_value, OCR1, OCR2, OCR3, water_table_max, inputfactor_max




# # JavaScript for updating window width
# app.clientside_callback(
#     """
#     function(n_intervals) {
#         return window.innerWidth;
#     }
#     """,
#     Output('window-width', 'data'),
#     Input('interval', 'n_intervals')
# )


# Callback to handle the animations and input updates
@app.callback(
    [Output('foundation-dimension-graph', 'figure'),
     Output('soil-layers-graph', 'figure'),
     Output('stress-change-graph', 'figure'),
     Output('sett_ref', 'children'),
     Output('sett_pref', 'children')],
    [Input('update-button', 'n_clicks')],
    [State('input-factor', 'value'),
     State('z-1', 'value'),
     State('z-2', 'value'),
     State('z-3', 'value'),
     State('water-table', 'value'),
     State('a', 'value'),
     State('b', 'value'),
     State('q', 'value'),
     State('gamma_1', 'value'),
     State('gamma_r_1', 'value'),
     State('gamma_2', 'value'),
     State('gamma_r_2', 'value'),
     State('gamma_3', 'value'),
     State('gamma_r_3', 'value'),
     State('C_c_1', 'value'),
     State('C_s_1', 'value'),
     State('e_0_1', 'value'),
     State('OCR_1', 'value'),
     State('C_c_2', 'value'),
     State('C_s_2', 'value'),
     State('e_0_2', 'value'),
     State('OCR_2', 'value'),
     State('C_c_3', 'value'),
     State('C_s_3', 'value'),
     State('e_0_3', 'value'),
     State('OCR_3', 'value')]
)

def update_graphs(n_clicks, sublayer_thickness, z1, z2, z3, water_table, a, b, q, gamma_1, gamma_r_1, gamma_2, gamma_r_2, 
                   gamma_3, gamma_r_3, C_c_1, C_s_1, e_0_1, OCR_1, C_c_2, C_s_2, e_0_2, 
                   OCR_2, C_c_3, C_s_3, e_0_3, OCR_3):
    # Constants
    gamma_water = 10 # kN/m³ for water
    # total_settelment = 0

    # total depth
    total_depth = z1 + z2 + z3

    # Ensure y_top has a default value
    y_top = -0.1*total_depth

    # Define soil layers and their boundaries with specified patterns
    layers = [
        {'layer_id': '1', 'name': 'Layer 1', 'thickness' : z1,'top': 0, 'bottom': z1},  
        {'layer_id': '2', 'name': 'Layer 2', 'thickness' : z2, 'top': z1, 'bottom': z1 + z2},  
        {'layer_id': '3', 'name': 'Layer 3', 'thickness' : z3, 'top': z1 + z2, 'bottom': z1 + z2 + z3},  
    ]

    # Create the soil layers figure (139,69,19)
    foundation_fig = go.Figure()
    soil_layers_fig = go.Figure()
    stress_change_fig = go.Figure()

 
    # add top view dimension scaled to 0-1
    x0_dim = 2*a - a/2
    y0_dim = 0
    x1_dim = 2*a + a/2
    y1_dim = b

    # add rectangle for foundation top view
    foundation_fig.add_shape(
        type="rect",
        x0=x0_dim,
        y0=y0_dim,
        x1=x1_dim,
        y1=y1_dim,
        line=dict(width=3, color="black"),
    )

    # Add text annotation at the middle of the line
    foundation_fig.add_annotation(
        x=0.5*(x1_dim - x0_dim) + x0_dim,  # Middle x-coordinate
        y=1.07 * y1_dim,  # Slightly above the line
        text=f"a= {a}m",  # The label text
        showarrow=False,  # No arrow for the text itself
        xanchor='center',
        yanchor='bottom'  # Align the text to appear above the line
    )

    # Add text annotation at the middle of the line with dircetion of the text from down to up
    foundation_fig.add_annotation(
        x=0.99*x0_dim,  # Slightly left of the line
        y=0.5*(y1_dim - y0_dim) + y0_dim,  # Middle y-coordinate
        text=f"b= {b}m",  # The label text
        showarrow=False,  # No arrow for the text itself
        xanchor='right',
        yanchor='middle',  # Align the text to appear above the line
        textangle=-90
    )

    # add A-A section the middle of foundation length b
    foundation_fig.add_shape(
        type="line",
        x0=0.8*x0_dim,
        y0=b/2,
        x1=1.1*x1_dim,
        y1=b/2,
        line=dict(color="black", width=2, dash='dash'),
    )   

    # add text at the begining and end of the line
    foundation_fig.add_annotation(
        x=0.8*x0_dim, # x-coordinate of arrow head
        y=b/2, # y-coordinate of arrow head
        text="A",  # The label text
        showarrow=False,  # No arrow for the text itself
        # font=dict(size=14, color="black"),
        xanchor='center',
        yanchor='bottom'  # Align the text to appear above the line
    )
    foundation_fig.add_annotation(
        x=1.1*x1_dim, # x-coordinate of arrow head
        y=b/2, # y-coordinate of arrow head
        text="A",  # The label text
        showarrow=False,  # No arrow for the text itself
        xanchor='center',
        yanchor='bottom'  # Align the text to appear above the line
    )

    # add a point E at the center of the foundation with annotation E, show a dot at the point
    foundation_fig.add_trace(go.Scatter(
        x=[(x1_dim-x0_dim)/2 + x0_dim],
        y=[b/2],
        mode='markers',
        marker=dict(color='black'),
        showlegend=False,
        hoverinfo='skip'
    ))
    foundation_fig.add_annotation(
        x=(x1_dim-x0_dim)/2 + x0_dim, # x-coordinate of arrow head
        y=b/2, # y-coordinate of arrow head
        text="E",  # The label text
        showarrow=False,  # No arrow for the text itself
        xanchor='left',
        yanchor='bottom'  # Align the text to appear above the line
    )

    
    for layer in layers:
        if layer['thickness'] > 0:
            # Add a line at the top and bottom of each layer
            soil_layers_fig.add_trace(go.Scatter(
                x=[0, 4*a], 
                y=[layer['top'], layer['top']],  # Horizontal line at the top of the layer
                mode='lines',
                line=dict(color='black', width=1, dash='dash'),
                showlegend=False,  # Hide legend for these lines
                hoverinfo='skip'  # Skip the hover info for these lines
            ))
            
    # horizantal line at the bottonm of the third layer
    soil_layers_fig.add_trace(go.Scatter(
        x=[0, 4*a],  # Start at -1 and end at 1
        y=[total_depth, total_depth],  
        mode='lines',
        line=dict(color='black', width=1, dash='dash'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    ))

    # Add a line at the water table
    soil_layers_fig.add_trace(go.Scatter(
        x=[0, 4*a],  # Start at -1 and end at 1
        y=[water_table, water_table],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='blue', width=2, dash='dot'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    )) 

    # adding arrowas distributed load on the foundation
    num_arrows = a//0.5
    for i in range(0, int(num_arrows+1)):
        soil_layers_fig.add_annotation(
            x=x0_dim + i*0.5, # x-coordinate of arrow head
            y=0, # y-coordinate of arrow head
            ax=x0_dim + i*0.5, # x-coordinate of tail
            ay=y_top, # y-coordinate of tail
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="black"
        )

    soil_layers_fig.add_trace(go.Scatter(
        x=[x0_dim, x1_dim],  
        y=[0, 0],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='black', width=4, dash='solid'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    ))

    # add A text at the begeing and end of the foundation
    soil_layers_fig.add_annotation(
        x=0.95*x0_dim, # x-coordinate of arrow head   
        y=0, # y-coordinate of arrow head
        text="A",  # The label text
        showarrow=False,  # No arrow for the text itself
        # font=dict(size=14, color="black"),
        xanchor='center',
        yanchor='bottom'  # Align the text to appear above the line
    )
    soil_layers_fig.add_annotation(
        x=1.03*x1_dim, # x-coordinate of arrow head
        y=0, # y-coordinate of arrow head
        text="A",  # The label text
        showarrow=False,  # No arrow for the text itself
        # font=dict(size=14, color="black"),
        xanchor='center',
        yanchor='bottom'  # Align the text to appear above the line
    )
    
    # Add the soil layers to the figure

    x_1 = np.arange(start=x0_dim - 1.5*a, stop=x0_dim - 0.5*a, step=0.2*a)
    x_2 = np.arange(start=x0_dim - 0.5*a, stop=x1_dim + 0.5*a, step=0.01*a)
    x_3 = np.arange(start=x1_dim + 0.5*a, stop=x1_dim + 1.5*a, step=0.2*a)

    if total_depth > 3*a:
        z_1 = np.arange(start=0.000000001, stop=3*a, step=0.01*a)
        z_2 = np.arange(start=3*a, stop=total_depth, step=0.2*a)
    else:
        z_1 = np.arange(start=0.000000001, stop=total_depth, step=0.01*a)
        z_2 = []

    x= np.concatenate([x_1, x_2, x_3])
    z = np.concatenate([z_1, z_2])
    X, Z = np.meshgrid(x, z)

    # Initialize I as an array filled with zeros
    I = np.zeros_like(X)

    b1 = b2 = b / 2

    for i, x_val in enumerate(x):
        
        if x_val <= x0_dim:
            a1 = x1_dim - x_val
            a2 = x0_dim - x_val
        elif x_val >= x1_dim:
            a1 = x_val - x0_dim
            a2 = x_val - x1_dim
        else:
            a1 = x1_dim - x_val
            a2 = x_val - x0_dim

        R1 = np.sqrt(a1**2 + b1**2 + Z**2)
        R2 = np.sqrt(a2**2 + b2**2 + Z**2)

        I1 = (1 / (2 * np.pi)) * (
            (np.arctan((a1 * b1) / (R1 * Z))) + (((a1 * b1 * Z) / R1) * ((1 / ((a1**2) + (Z**2))) + (1 / ((b1**2) + (Z**2)))))
        )
        I2 = (1 / (2 * np.pi)) * (
            (np.arctan((a2 * b2) / (R2 * Z))) + (((a2 * b2 * Z) / R2) * ((1 / ((a2**2) + (Z**2))) + (1 / ((b2**2) + (Z**2)))))
        )

        if x_val <= x0_dim or x_val >= x1_dim:
            I[:, i] = 2 * I1[:, i] - 2 * I2[:, i]  # Adjust to take the i-th column slice if needed
        else:
            I[:, i] = 2 * I1[:, i] + 2 * I2[:, i]  # Adjust to take the i-th column slice if needed

    # Ensure I has no negative values
    I = np.where(I < 0, 0, I)
        
    # Create the contour trace with only lines and no color fill
    contour_trace = go.Contour(
        z=I,
        x=x,
        y=z,
        contours=dict(
            start=0,
            end=0.9,
            size=0.1,
            showlabels=True,
            # labelfont=dict(size=12, color='black')  # Ensures labels are visible
        ),
        colorscale='YlOrRd',  # Use 'Cividis' or 'Plasma' for alternatives
        showscale=False,
        showlegend=False,
        hovertemplate='J: %{z:.3f}<br>x: %{x:.3f}<br>y: %{y:.3f}<extra></extra>'
    )

    # Add the contour trace to the figure
    soil_layers_fig.add_trace(contour_trace)

    
    # First figure (soil_layers_fig)
    soil_layers_fig.update_layout(
        plot_bgcolor='white',
        xaxis_title= dict(text='Width (m)', font=dict(weight='bold')),
        xaxis=dict(
            range=[0, 4*a],  # Adjusting the x-range as needed
            side = 'top',
            title_standoff=4,
            showticklabels=True,
            ticks='outside',
            ticklen=5,
            minor_ticks="inside",
            showline=True,
            linewidth=2,
            linecolor='black',
            zeroline=False,
            # scaleanchor="y",  # Link x and y axes scaling
            # scaleratio=1,
        ),
        yaxis_title= dict(text='Depth (m)', font=dict(weight='bold')),
        yaxis=dict(
            range=[total_depth, y_top],  # Adjusted range for the y-axis (inverted for depth)
            showticklabels=True,
            ticks='outside',
            title_standoff=4,
            ticklen=5,
            minor_ticks="inside",
            showline=True,
            linewidth=2,
            linecolor='black',
            zeroline=False,
            # scaleanchor="x",  # Link y-axis scaling with x-axis
            # scaleratio=1,
        ),
        margin=dict(l=30, r=10, t=10, b=20),
    )

    # Get the x-axis range from the first figure
    x_range = soil_layers_fig.layout.xaxis.range

    # Second figure (foundation_fig)
    foundation_fig.update_layout(
        plot_bgcolor='white',
        dragmode=False,  # Disable zooming and panning
        autosize=False,
        xaxis=dict(
            range=x_range,  # Set the same x-range as soil_layers_fig
            showticklabels=False,
            title_standoff=4,
            showgrid=False,
            showline=False,
            title=None,
            zeroline=False,
            fixedrange=True
        ),
        yaxis=dict(
            range=[0, a],  # Adjusted range for the y-axis in this figure
            showticklabels=False,
            title_standoff=4,
            showgrid=False,
            showline=False,
            title=None,
            zeroline=False,
            fixedrange=True,
            scaleanchor="x",  # Link y-axis scaling with x-axis
            scaleratio=1,
        ),
        margin=dict(l=60, r=40, t=10, b=10),
    )

    # Third figure (stress_change_fig)
    
    def stress_change_and_settelment(step):
        # Define depths array
        depths_z1 = np.arange(start=step / 2, stop=int(z1 / step) * step , step=step)
        # Modify depths array for the first layer (z1)
        if (z1 / step) % 1 != 0:  # Check if z1/step is not an integer
            remaining_thickness1 = z1 - (depths_z1[-1] + step / 2)
            depths_z1 = np.append(depths_z1, int(z1 / step) * step +  remaining_thickness1 / 2)
        


        depths_z2 = np.arange(start=z1 + step / 2, stop=z1+int(z2 / step) * step , step=step)
        # Modify depths array for the second layer (z2)
        if (z2 / step) % 1 != 0:  # Check if z2/step is not an integer
            remaining_thickness2 = z1+ z2 - (depths_z2[-1] - step / 2)
            depths_z2 = np.append(depths_z2, depths_z2[-1] +  remaining_thickness2 / 2)
               
        depths_z3 = np.arange(start=z1+z2+step / 2, stop=z1+z2+int(z3 / step) * step, step=step)
        # Modify depths array for the third layer (z3)
        if (z3 / step) % 1 != 0:  # Check if z3/step is not an integer
            remaining_thickness3 = z1 + z2 + z3 - (depths_z3[-1] - step / 2)
            depths_z3 = np.append(depths_z3, depths_z3[-1] +  remaining_thickness3 / 2)

        # Initialize stress_change and settelment arrays
        all_depths = np.concatenate([depths_z1, depths_z2, depths_z3])
        depths = np.sort(all_depths)[::-1]
        stress_change = np.zeros_like(depths)
        settelment = np.zeros_like(depths)

        # Calculate change in stress based on the conditions
        for i, depth in enumerate(depths):
            # Calculate I for each depth
            a_E = a / 2
            b_E = b / 2
            R = np.sqrt(a_E**2 + b_E**2 + depth**2)
            I = (1 / (2 * np.pi)) * (
                (np.arctan((a_E * b_E) / (R * depth))) +
                (((a_E * b_E * depth) / R) * ((1 / ((a_E**2) + (depth**2))) + (1 / ((b_E**2) + (depth**2)))))
            )
            stress_change[i] = 4 * I * q

        # Settlement calculations per depth level under point E
        sigma_i = np.zeros_like(depths)
        sigma_f = np.zeros_like(depths)
        sigma_p = np.zeros_like(depths)
        

           
        # OCR = sigma_c / sigma_i
        for i, depth in enumerate(depths):
            if depth <= z1:
                if depth <= water_table:
                    sigma_i[i] = depth * gamma_1
                else:
                    sigma_i[i] = water_table * gamma_1 + (depth - water_table) * (gamma_r_1 - gamma_water)

                sigma_f[i] = sigma_i[i] + stress_change[i]
                sigma_p[i] = OCR_1 * sigma_i[i]

                if OCR_1 == 1:
                    delta_settlement = 1000 * (step / (1 + e_0_1)) * C_c_1 * np.log10(sigma_f[i] / sigma_i[i])
                elif OCR_1 > 1 and sigma_f[i] <= sigma_p[i]:
                    delta_settlement = 1000 * (step / (1 + e_0_1)) * C_s_1 * np.log10(sigma_f[i] / sigma_i[i])
                elif OCR_1 > 1 and sigma_f[i] > sigma_p[i]:
                    delta_settlement = 1000 * (step / (1 + e_0_1)) * (
                        (C_s_1 * np.log10(sigma_p[i] / sigma_i[i])) +
                        (C_c_1 * np.log10(sigma_f[i] / sigma_p[i]))
                    )
            elif depth > z1 and depth <= z1 + z2:
                if water_table > z1:
                    if depth <= water_table:
                        sigma_i[i] = z1*gamma_1 + (depth - z1) * gamma_2
                    else:
                        sigma_i[i] = z1*gamma_1 + (water_table-z1)*gamma_2  + (depth - water_table) * (gamma_r_2 - gamma_water)
                else:
                    sigma_i[i] = water_table * gamma_1 + (z1 - water_table) * (gamma_r_1 - gamma_water) + (depth - z1) * (gamma_r_2 - gamma_water)

                sigma_f[i] = sigma_i[i] + stress_change[i]
                sigma_p[i] = OCR_2 * sigma_i[i]


                if OCR_2 == 1:
                    delta_settlement = 1000 * (step / (1 + e_0_2)) * C_c_2 * np.log10(sigma_f[i] / sigma_i[i])
                elif OCR_2 > 1 and sigma_f[i] <= sigma_p[i]:
                    delta_settlement = 1000 * (step / (1 + e_0_2)) * C_s_2 * np.log10(sigma_f[i] / sigma_i[i])
                elif OCR_2 > 1 and sigma_f[i] > sigma_p[i]:
                    delta_settlement = 1000 * (step / (1 + e_0_2)) * (
                        (C_s_2 * np.log10(sigma_p[i] / sigma_i[i])) +
                        (C_c_2 * np.log10(sigma_f[i] / sigma_p[i]))
                    )

            else:
                if water_table > z1+z2:
                    if depth <= water_table:
                        sigma_i[i] = z1*gamma_1 + z2*gamma_2 + (depth - z1 - z2) * gamma_3
                    else:
                        sigma_i[i] = z1*gamma_1 + z2*gamma_2 + (water_table - z1 - z2) * gamma_3 + (depth - water_table) * (gamma_r_3 - gamma_water)
                elif water_table > z1 and water_table <= z1+z2:
                    sigma_i[i] = z1*gamma_1 + (water_table-z1)*gamma_2 + (z1+z2-water_table)*(gamma_r_2-gamma_water) +(depth - z1 - z2) * (gamma_r_3 - gamma_water)
                else:
                    sigma_i[i] = water_table * gamma_1 + (z1 - water_table) * (gamma_r_1 - gamma_water) + z2 * (gamma_r_2-gamma_water) + (depth - z1 - z2) * (gamma_r_3 - gamma_water)


                sigma_f[i] = sigma_i[i] + stress_change[i]
                sigma_p[i] = OCR_3 * sigma_i[i]

                if OCR_3 == 1:
                    delta_settlement = 1000 * (step / (1 + e_0_3)) * C_c_3 * np.log10(sigma_f[i] / sigma_i[i])
                elif OCR_3 > 1 and sigma_f[i] <= sigma_p[i]:
                    delta_settlement = 1000 * (step / (1 + e_0_3)) * C_s_3 * np.log10(sigma_f[i] / sigma_i[i])
                elif OCR_3 > 1 and sigma_f[i] > sigma_p[i]:
                    delta_settlement = 1000 * (step / (1 + e_0_3)) * (
                        (C_s_3 * np.log10(sigma_p[i] / sigma_i[i])) +
                        (C_c_3 * np.log10(sigma_f[i] / sigma_p[i]))
                    )
            # Update cumulative settlement
            settelment[i] = delta_settlement + (settelment[i-1] if i > 0 else 0)

            # Total settlement is the final cumulative value
            total_settelment = settelment[-1]

        return depths, stress_change, settelment, total_settelment

    # Initialize the total settlement list
    settelments = []
    # Add the stress change and settlement traces to the figure
    for i, step in enumerate((sublayer_thickness, 0.05)):
        depths, stress_change, settelment, total_settelment = stress_change_and_settelment(step)
        if step != 0.05:
            dashed = 'dash'
            mode = 'lines+markers'
        else:
            dashed = 'solid'
            mode = 'lines'

        # Draw stress change with depth under point E
        stress_change_fig.add_trace(go.Scatter(
            x=stress_change,
            y=depths,
            mode=mode,
            line=dict(color='red', width=3, dash=dashed),
            name='Stress increment, Δσ<sub>z,E</sub>, sublayer thickness = '+str(step)+'m',
            showlegend=True,
        ))

        # Draw settlement with depth under point E
        stress_change_fig.add_trace(go.Scatter(
            x=settelment,
            y=depths,
            mode=mode,
            # line_shape='vhv',
            xaxis='x2',
            line=dict(color='green', width=3, dash=dashed),
            name='Settlement, Δ𝜌<sub>z,E</sub>, sublayer thickness = '+str(step)+'m',
            showlegend=True,
        )) 

        # Append the total settlement to the list
        if step == 0.05:
            settelments.append( f'{round(total_settelment, 2)}')
        else:
            settelments.append( f'{round(total_settelment, 2)}')


            
    for layer in layers:
        if layer['thickness'] > 0:
            # Add a line at the bottom of each layer other graph
            stress_change_fig.add_trace(go.Scatter(
                x=[0, 1.2 * max(stress_change)],  # Start at -1 and end at 1
                y=[layer['top'], layer['top']],  # Horizontal line at the top of the layer
                mode='lines',
                line=dict(color='black', width=1, dash='dash'),
                showlegend=False,  # Hide legend for these lines
                hoverinfo='skip'  # Skip the hover info for these line
            ))
    
    # horizantal line at the bottonm of the third layer
    stress_change_fig.add_trace(go.Scatter(
        x=[0, 1.2 * max(stress_change)],  # Start at -1 and end at 1
        y=[z1 + z2 + z3, z1 + z2 + z3],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='black', width=1, dash='dash'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    ))




    stress_change_fig.update_layout(
        xaxis_title=dict(text='Δσ<sub>z,E</sub> (kPa)', font=dict(weight='bold')),
        plot_bgcolor='white',
        xaxis=dict(
            range=[0, 1.2 * max(stress_change)],
            side='top',
            title_standoff=4,
            zeroline=False,
            showticklabels=True,
            ticks='outside',
            ticklen=5,
            minor_ticks="inside",
            showline=True,
            linewidth=2,
            linecolor='black',
            showgrid=False,
            gridwidth=1,
            gridcolor='lightgrey',
            mirror=True,
            hoverformat=".2f"  # Sets hover value format for x-axis to two decimal places
        ),
        xaxis2=dict(  # Second x-axis (Displacement)
            title=dict(text='Δ𝜌<sub>z,E</sub> (mm)', font=dict(weight='bold')),
            overlaying='x',  # Share the same space as the first x-axis
            title_standoff=1,
            side='top',   
            position = ((total_depth)/(total_depth-y_top)), 
            anchor='free', 
            showticklabels=True,
            ticks='outside',
            ticklen=3,
            minor_ticks="inside",
            showline=True,
            linewidth=2,
            linecolor='black',
            showgrid=False,
            gridwidth=1,
            gridcolor='lightgrey',
            mirror=True,
            hoverformat=".2f",  # Sets hover value format for x-axis to two decimal places
            range=[0,  1.4* max(settelment)],  # Match the range of the first x-axis
        ),
        yaxis_title=dict(text='Depth (m)', font=dict(weight='bold')),
        yaxis=dict(
            range=[total_depth, y_top],
            zeroline=False,
            title_standoff=4,
            showticklabels=True,
            ticks='outside',
            ticklen=5,
            minor_ticks="inside",
            showline=True,
            linewidth=2,
            linecolor='black',
            showgrid=False,
            gridwidth=1,
            gridcolor='lightgrey',
            mirror=True,
            hoverformat=".2f"  # Sets hover value format for y-axis to two decimal places
        ),
        legend=dict(
            yanchor="bottom",  # Align the bottom of the legend box
            y=0,               # Position the legend at the bottom inside the plot
            xanchor="right",    # Align the right edge of the legend box
            x=1,               # Position the legend at the right inside the plot
            font= dict(size=9),  # Adjust font size
            bgcolor="rgba(255, 255, 255, 0.7)",  # Optional: Semi-transparent white background
            bordercolor="black",                 # Optional: Border color
            borderwidth=1                        # Optional: Border width
        ),
        margin=dict(l=30, r=10, t=10, b=20),
    )
    


    return foundation_fig, soil_layers_fig, stress_change_fig, settelments[0], settelments[1]
# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
    

# Expose the server
server = app.server
