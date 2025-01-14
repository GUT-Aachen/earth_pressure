import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objs as go
import time


app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

app.title = 'Earth Pressure 1'
app._favicon = ('assets/favicon.ico')

# Updated layout with sliders on top and layer properties below
app.layout = html.Div([
    # Main container
    html.Div(style={'display': 'flex', 'flexDirection': 'row', 'width': '100%', 'height': '100vh'}, children=[
        # Control container (sliders)
        html.Div(id='control-container', style={'width': '25%', 'padding': '2%', 'flexDirection': 'column'}, children=[
            html.H1('Earth Pressure 1', className='h1'),

            # Add the update button
            html.Button("Update Graphs", id='update-button', n_clicks=0, style={'width': '100%', 'height': '5vh', 'marginBottom': '1vh'}),

            # Sliders for each layer
            html.Div(className='slider-container', children=[
                # horizantal movement Slider
                html.Label(children=[
                    'u/h', 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Ratio of horizantal to wall height of the wall', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='u/h', min=-0.1, max=0.1, step=0.0001, value=0,
                        marks={
                                0.1: "Passive",
                                0: "At-Rest",
                                -0.1: "Active"
                                },
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),

                # height
                html.Label(children=[
                    'h (m)', 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Height of the wall', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='h', min=0, max=20, step=0.25, value=2,
                    marks={i: f'{i}' for i in range(0, 21, 5)},
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),

                # Clay Slider
                html.Label(children=[
                    'ϕ′ (deg)', 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Effective friction angle', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='friction_angle', min=10, max=50, step=0.5, value=30,
                    marks={i: f'{i}' for i in range(0, 51, 10)},
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),

                # Sand-2 Slider
                html.Label(children=[
                    'c′ (kPa)', 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Thickness of Sand-2.', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='c', min=0, max=100, step=2, value=0,
                    marks={i: f'{i}' for i in range(0, 101, 20)},
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
                    id='water-table', min=0, max=4, step=0.25, value=0,
                    marks={i: f'{i}' for i in range(0, 5, 2)},
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),
            ]),
        
        # Properties for each layer
        html.Div(className='layer-properties', children=[
                # foundation Properties
                # html.H3('Load:', style={'textAlign': 'left'}, className='h3'),
                #     html.Label(["Δσ", 
                #             html.Div(className='tooltip', children=[
                #                 html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                #                 html.Span('Chnage of stress', className='tooltiptext')
                #             ]),'(kPa)'], className='input-label'),
                # dcc.Input(id='delta_sigma', type='number', value=100, step=1, className='input-field'),


                # Soil Properties
                html.H3('Soil:', style={'textAlign': 'left'}, className='h3'),
                html.Label([f'γ', html.Sub('d'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Dry unit weight of Sand-1', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_1', type='number', value=18, step=0.01, className='input-field'),
                html.Label([f'γ', html.Sub('sat'), 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Saturated unit weight of Sand-1', className='tooltiptext')
                            ]),' (kN/m³)'], className='input-label'),
                dcc.Input(id='gamma_r_1', type='number', value=19, step=0.01, className='input-field'),
                html.Div(style={'display': 'flex', 'alignItems': 'center', 'whiteSpace': 'nowrap'}, children=[
                    html.Label([f'γ′', 
                                html.Div(className='tooltip', children=[
                                    html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                    html.Span('Submerged unit weight of Sand-1', className='tooltiptext')
                                ])], className='input-label', style={'marginRight': '5px'}),
                    html.Div(id='gamma_prime_1', className='input-field')  
                ]),
            ]),
        ]),

        # Graphs container
        html.Div(className='graph-container', id='graphs-container', style={'display': 'flex', 'flexDirection': 'row', 'width': '75%'},
        children=[
            html.Div(style={'width': '50%', 'height': '100%'}, children=[
                dcc.Graph(id='soil-layers-graph', style={'height': '100%', 'width': '100%'})
            ]),
            html.Div(style={'width': '50%', 'height': '100%'}, children=[
                dcc.Graph(id='pressure-graph', style={'height': '100%', 'width': '100%'})
            ])
        ]),

        
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
    Output('gamma_prime_1', 'children'),
    Output('water-table', 'max'),
    Input('gamma_r_1', 'value') ,
    Input('h', 'value'),
    )
def update_gamma_prime(gamma_r1, h):
    # Calculate γ′ as γ_r - 9.81 for each layer
    gamma_prime1 = round(gamma_r1 - 10, 2) if gamma_r1 is not None else None

    # water table max cannot be more than u
    water_table_max = h
    

    return f"= {gamma_prime1} kN/m³",  water_table_max


# Callback to handle the animations and input updates
@app.callback(
    [Output('soil-layers-graph', 'figure'),
     Output('pressure-graph', 'figure')],
    [Input('update-button', 'n_clicks')],   
    [State('u/h', 'value'),
     State('h', 'value'),
     State('gamma_1', 'value'),
     State('gamma_r_1', 'value'),
     State('water-table', 'value'),
     State('c', 'value'),
     State('friction_angle', 'value')]
)

def update_graphs(n_clicks,u_r, h,gamma_1, gamma_r_1, water_table, c, friction_angle):
    # Constants
    gamma_water = 10 # kN/m³ for water
    u= u_r*h

    # Ensure y_top has a default value
    y_top = -0.1*h

    # Define soil layers and their boundaries with specified patterns
    layers = [
        {'layer_id': '2', 'name': 'Soil', 'thickness' : h, 'top': 0, 'bottom': h, 'color': 'rgb(244,164,96)',
         'fillpattern': {'shape': '.'}, 'x0': 0
         },  # Dots for Sand  
    ]

    # Create the soil layers figure (139,69,19)
    soil_layers_fig = go.Figure()
    Mohr_circle_fig = go.Figure()

    # Add the soil layers to the figure
    
    for layer in layers:
        if layer['thickness'] > 0:
            soil_layers_fig.add_trace(go.Scatter(
                x=[0.01*h+u, 0.01*h, 0.5*h, 0.5*h],  # Create a rectangle-like shape
                y=[layer['top'], layer['bottom'], layer['bottom'], layer['top']],
                fill='toself',
                fillcolor=layer['color'],  # Transparent background to see the pattern
                line=dict(width=1, color='black'),
                name=layer['name'],
                showlegend=False,
                mode='lines',  # Show only the lines, no markers (dots)
                hoverinfo='skip',  # Skip the hover info for these layers
                fillpattern=layer['fillpattern']  # Use the specified fill pattern
            ))
            # Add the annotation for the layer name
            mid_depth = (layer['top'] + layer['bottom']) / 2  # Midpoint of the layer
            soil_layers_fig.add_annotation(
                x=0.25*h,  # Position the text slightly to the right of the layer box
                y=mid_depth,
                text=layer['name'],  # Layer name as text
                font = dict(size=14, color="white", weight='bold'),
                showarrow=False,  # Don't show an arrow
                xanchor='left',  # Anchor text to the left
                yanchor='middle'  # Center text vertically with the midpoint             
            )

    # add the ground surface

    soil_layers_fig.add_trace(go.Scatter(
        x=[0, 1],  
        y=[0, 0],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='black', width=4, dash='solid'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    ))
    # add at rest earth pressure with dash line
    soil_layers_fig.add_trace(go.Scatter(
        x=[-0.01*h, -0.01*h, 0.01*h, 0.01*h],  # Create a rectangle-like shape
        y=[0, h, h, 0],
        fill='none',
        line=dict(width=1, color='black', dash='dash'),
        name='at rest earth pressure',
        showlegend=False,
        hoverinfo='skip',  # Skip the hover info for these layers
        mode='lines'  # Show only the lines, no markers (dots)
    ))

    # add the earth retaining wall
    soil_layers_fig.add_trace(go.Scatter(
        x=[-0.01*h+u, -0.01*h, 0.01*h, 0.01*h+u],  # Create a rectangle-like shape
        y=[0, h, h, 0],
        fill='toself',
        fillcolor='black',  # Transparent background to see the pattern
        line=dict(width=1, color='black'),
        name='Retaining Wall',
        showlegend=False,
        hoverinfo='skip',  # Skip the hover info for these layers
        fillpattern={'shape': '/'},
        mode='lines'  # Show only the lines, no markers (dots)
    ))

    # add a line at the 0 axis and y-top dash
    soil_layers_fig.add_trace(go.Scatter(
        x=[0, 0],  # Start at -1 and end at 1
        y=[h, y_top],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='black', width=1, dash='dash'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    ))

    # add a line to show the movement of the wall
    soil_layers_fig.add_trace(go.Scatter(
        x=[0, (h-y_top)*u_r],  # Start at -1 and end at 1
        y=[h, y_top],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='red', width=1, dash='dash'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    ))


    # add arrow  from to show the direction of passive 
    soil_layers_fig.add_annotation(
        x=0.1*h,  
        y=0.5*y_top,
        ax=0,  # x-coordinate of arrow head
        ay=0.5*y_top,  # y-coordinate of arrow head
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=3,
        arrowcolor="green"
    )
    # add annotation for the passive
    soil_layers_fig.add_annotation(
        x=0.05*h,  # Position the text slightly to the right of the layer box
        y=0.8*y_top,
        text='Passive',  # Layer name as text
        font = dict(size=14, color="green", weight='bold'),
        showarrow=False,  # Don't show an arrow
        xanchor='center',  # Anchor text to the left
        yanchor='middle'  # Center text vertically with the midpoint
    )

    # add arrow  from to show the direction of  active
    soil_layers_fig.add_annotation(
        x=-0.1*h,  
        y=0.5*y_top,
        ax=0,  # x-coordinate of arrow head
        ay=0.5*y_top,  # y-coordinate of arrow head
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=3,
        arrowcolor="blue"
    )
    # add annotation for the passive
    soil_layers_fig.add_annotation(
        x=-0.05*h,  # Position the text slightly to the right of the layer box
        y=0.8*y_top,
        text='Active',  # Layer name as text
        font = dict(size=14, color="blue", weight='bold'),
        showarrow=False,  # Don't show an arrow
        xanchor='center',  # Anchor text to the left
        yanchor='middle'  # Center text vertically with the midpoint
    )

    # Add a line at the water table
    soil_layers_fig.add_trace(go.Scatter(
        x=[0, 1],  # Start at -1 and end at 1
        y=[0, 0],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='blue', width=2, dash='dot'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    )) 

    # # adding arrowas distributed load on the foundation
    # num_arrows = 10
    # for i in range(0, int(num_arrows+1)):
    #     soil_layers_fig.add_annotation(
    #         x=i*0.1*(0.1*h), # x-coordinate of arrow head
    #         y=0, # y-coordinate of arrow head
    #         ax=i*0.1*(0.1*h), # x-coordinate of tail
    #         ay=0.9*y_top, # y-coordinate of tail
    #         xref="x",
    #         yref="y",
    #         axref="x",
    #         ayref="y",
    #         showarrow=True,
    #         arrowhead=2,
    #         arrowsize=1,
    #         arrowwidth=2,
    #         arrowcolor="black"
    #     )



    # #  adding text for the load delta sigma
    # soil_layers_fig.add_annotation(
    #     x=0.05*h,  # Position the text slightly to the right of the layer box
    #     y=y_top,
    #     text='Δσ',  # Layer name as text
    #     font = dict(size=14, color="black", weight='bold'),
    #     showarrow=False,  # Don't show an arrow
    #     xanchor='center',  # Anchor text to the left
    #     yanchor='middle'  # Center text vertically with the midpoint
    # )
    # add a line for the water table
    soil_layers_fig.add_trace(go.Scatter(
        x=[0, 1],  # Start at -1 and end at 1
        y=[water_table, water_table],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='blue', width=2, dash='dot'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    ))

   
    # First figure (soil_layers_fig)
    soil_layers_fig.update_layout(
        plot_bgcolor='white',
        xaxis_title= dict(text='u (m)', font=dict(weight='bold')),
        xaxis=dict(
            range=[-0.2*h, 0.5*h],  # Adjusting the x-range as needed
            showticklabels=True,
            ticks='outside',
            title_standoff=4,
            ticklen=5,
            minor_ticks="inside",
            showline=True,
            linewidth=2,
            linecolor='black',
            zeroline=False,
            side='bottom'
        ),
        yaxis_title= dict(text='h (m)', font=dict(weight='bold')),
        yaxis=dict(
            range=[h, y_top],  # Adjusted range for the y-axis (inverted for depth)
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
            side='right'
        ),
        margin=dict(l=20, r=10),
    )

    # Mohr circle figure
    k_0 = 1 - np.sin(np.radians(friction_angle))
    print(k_0)
    k_a = (1 - np.sin(np.radians(friction_angle)))/(1 + np.sin(np.radians(friction_angle)))
    k_p = 1/k_a
    sigma_n =0



    # At-rest effective stresses
    if water_table > h/2:
        sigma_v_0 = gamma_1 * (h - water_table) + (gamma_r_1 - gamma_water) * (water_table-h/2)
    else:
        sigma_v_0 = gamma_1 * h/2
    sigma_h_0 = sigma_v_0 * k_0
    r_0 = (sigma_v_0 - sigma_h_0)/2
    center_0 = (sigma_v_0 + sigma_h_0) / 2

    # Generate points for the Mohr circle
    theta_0 = np.linspace(0, 2 * np.pi, 100)  # 100 points for a smooth circle
    x_circle_0 = center_0 + r_0 * np.cos(theta_0)
    y_circle_0 = r_0 * np.sin(theta_0)

    # Add the Mohr circle to the figure
    Mohr_circle_fig.add_trace(go.Scatter(
        x=x_circle_0,
        y=y_circle_0,
        mode='lines',
        line=dict(color='red', width=2),
        name='At Rest',
        showlegend=True
    ))
    sigma_n = 1.2 * sigma_v_0


    if u_r < 0:
        # active effectives stresses
        sigma_h_a = sigma_v_0*k_a * np.exp(u_r)
        R_a = (sigma_v_0 - sigma_h_a)/2
        center_a = (sigma_v_0 + sigma_h_a)/2
        # Generate points for the active Mohr circle
        theta_a = np.linspace(0, 2 * np.pi, 100)
        x_circle_a = center_a + R_a * np.cos(theta_a)
        y_circle_a = R_a * np.sin(theta_a)
        # Add the active Mohr circle to the figure
        Mohr_circle_fig.add_trace(go.Scatter(
            x=x_circle_a,
            y=y_circle_a,
            mode='lines',
            line=dict(color='blue', width=2),
            name='Active',
            showlegend=True
        ))
    elif u_r > 0:
        # passive effectives stresses
        sigma_h_p = sigma_v_0*k_p * np.exp(u_r)
        R_p = (sigma_v_0 - sigma_h_p)/2
        ceneter_p = (sigma_v_0 + sigma_h_p)/2
        # Generate points for the passive Mohr circle
        theta_p = np.linspace(0, 2 * np.pi, 100)
        x_circle_p = ceneter_p + R_p * np.cos(theta_p)
        y_circle_p = R_p * np.sin(theta_p)
        # Add the passive Mohr circle to the figure
        Mohr_circle_fig.add_trace(go.Scatter(
            x=x_circle_p,
            y=y_circle_p,
            mode='lines',
            line=dict(color='green', width=2),
            name='Passive',
            showlegend=True
        ))
        sigma_n = 1.2 * sigma_h_p
        

    # Correct critical state line
    shear_stress_max = c + sigma_n * np.tan(np.radians(friction_angle))
    Mohr_circle_fig.add_trace(go.Scatter(
        x=[0, sigma_n],  # From origin to max normal stress
        y=[c, shear_stress_max],  # From cohesion to max shear stress
        mode='lines',
        line=dict(color='black', width=2),
        name='Critical State Line',
        showlegend=True
    ))






    # # active effectives stresses
    # sigma_h_a = sigma_v_0*k_a
    # R_a = (sigma_v_0 - sigma_h_a)/2
    # center_a = (sigma_v_0 + sigma_h_a)/2
    # # draw the active mohr circle
    # # Mohr_circle_fig.add_trace(go.Scatter(
    # #     x=[sigma_h_a, sigma_v_0],
    # #     y=[0, 2*R_a],
    # #     mode='lines',
    # #     line=dict(color='blue', width=2),
    # #     name='Active',
    # #     showlegend=True,
    # #     hoverinfo='skip'
    # # ))

    # # passive effectives stresses
    # sigma_h_p = sigma_v_0*k_p
    # R_p = (sigma_v_0 - sigma_h_p)/2
    # ceneter_p = (sigma_v_0 + sigma_h_p)/2
    # # draw the passive mohr circle
    # # Mohr_circle_fig.add_trace(go.Scatter(
    # #     x=[sigma_h_p, sigma_v_0],
    # #     y=[0, 2*R_p],
    # #     mode='lines',
    # #     line=dict(color='green', width=2),
    # #     name='Passive',
    # #     showlegend=True,
    # #     hoverinfo='skip'
    # # ))

    Mohr_circle_fig.update_layout(
        xaxis_title=dict(text='σ (kPa)', font=dict(weight='bold')),
        plot_bgcolor='white',
        xaxis=dict(
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
        yaxis_title=dict(text='𝜏 (kPa)', font=dict(weight='bold')),
        yaxis=dict(
            zeroline=True,
            zerolinecolor= "black",
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
            hoverformat=".3f",  # Sets hover value format for y-axis to two decimal places
            scaleanchor="x",  # Link y-axis scaling with x-axis
            scaleratio=1,
        ),
        legend=dict(
            yanchor="top",  # Align the bottom of the legend box
            y=1,               # Position the legend at the bottom inside the plot
            xanchor="right",    # Align the right edge of the legend box
            x=1,               # Position the legend at the right inside the plot
            font= dict(size=10),  # Adjust font size
            bgcolor="rgba(255, 255, 255, 0.7)",  # Optional: Semi-transparent white background
            bordercolor="black",                 # Optional: Border color
            borderwidth=1                        # Optional: Border width
        ),
        margin=dict(l=10, r=10),
    )
    

     




    return soil_layers_fig, Mohr_circle_fig
if __name__ == '__main__':
    app.run_server(debug=True)
    

# Expose the server
server = app.server
