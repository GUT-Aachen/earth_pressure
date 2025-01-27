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
                    id='u/h', min=-0.002, max=0.01, step=0.00001, value=0,
                        marks={},
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
                    id='h', min=0, max=30, step=2, value=10,
                    marks={i: f'{i}' for i in range(0, 31, 10)},
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),

                html.Label(children=[
                    'ϕ′ (deg)', 
                            html.Div(className='tooltip', children=[
                                html.Img(src='/assets/info-icon.png', className='info-icon', alt='Info'), 
                                html.Span('Effective friction angle', className='tooltiptext')
                            ])], className='slider-label'),
                dcc.Slider(
                    id='friction_angle', min=20, max=50, step=0.5, value=30,
                    marks={i: f'{i}' for i in range(20, 51, 10)},
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
                    id='water-table', min=0, max=4, step=2, value=0,
                    marks={i: f'{i}' for i in range(0, 31, 5)},
                    className='slider', tooltip={'placement': 'bottom', 'always_visible': True}
                ),
            ]),
        
        # Properties for each layer
        html.Div(className='layer-properties', children=[

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
    Output('u/h', 'max'),
    Output('u/h', 'min'),
    Output('u/h', 'marks'),
    Input('gamma_r_1', 'value') ,
    Input('h', 'value'),
    Input('friction_angle', 'value')
    )
def update_gamma_prime(gamma_r1, h, friction_angle):
    # Calculate γ′ as γ_r - 9.81 for each layer
    gamma_prime1 = round(gamma_r1 - 10, 2) if gamma_r1 is not None else None

    # water table max cannot be more than u
    water_table_max = h
    if friction_angle < 25:
        h_u_max = 0.04
        h_u_min = -0.008
    elif friction_angle < 30:
        h_u_max = 0.02
        h_u_min = -0.004
    elif friction_angle < 35:
        h_u_max = 0.012
        h_u_min = -0.002
    elif friction_angle < 40:
        h_u_max = 0.008
        h_u_min = -0.0015
    else:
        h_u_max = 0.004
        h_u_min = -0.0006
    marks= {h_u_max: "Passive", 0: "At-Rest", h_u_min: "Active"}

    

    return f"= {gamma_prime1} kN/m³",  water_table_max, h_u_max, h_u_min, marks



# Callback to handle the animations and input updates
@app.callback(
    [Output('soil-layers-graph', 'figure'),
     Output('pressure-graph', 'figure')],
    [Input('update-button', 'n_clicks')],   
    [State('u/h', 'value'),
     State('u/h', 'max'),
     State('u/h', 'min'),
     State('h', 'value'),
     State('gamma_1', 'value'),
     State('gamma_r_1', 'value'),
     State('water-table', 'value'),
     State('friction_angle', 'value')]
)

def update_graphs(n_clicks,u_r, u_r_max, u_r_min, h,gamma_1, gamma_r_1, water_table, friction_angle):
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
                x=[0.1*(u_r_min+u_r_max)+u_r, 0.1*(u_r_min+u_r_max), 2*(u_r_max), 2*(u_r_max)],  # Create a rectangle-like shape
                y=[layer['top'], layer['bottom'], layer['bottom'], layer['top']],
                line=dict(width=1, color='black'),
                name=layer['name'],
                showlegend=False,
                mode='lines',  # Show only the lines, no markers (dots)
                hoverinfo='skip'
            ))

    # add at rest earth pressure with dash line
    soil_layers_fig.add_trace(go.Scatter(
        x=[-0.1*(u_r_min+u_r_max), -0.1*(u_r_min+u_r_max), 0.1*(u_r_min+u_r_max), 0.1*(u_r_min+u_r_max), -0.1*(u_r_min+u_r_max)],  # Create a rectangle-like shape
        y=[0, h, h, 0,0],
        fill='none',
        line=dict(width=1, color='black', dash='dash'),
        name='at rest earth pressure',
        showlegend=False,
        hoverinfo='skip',  # Skip the hover info for these layers
        mode='lines'  # Show only the lines, no markers (dots)
    ))

    # add the earth retaining wall
    soil_layers_fig.add_trace(go.Scatter(
        x=[-0.1*(u_r_min+u_r_max)+u_r, -0.1*(u_r_min+u_r_max), 0.1*(u_r_min+u_r_max), 0.1*(u_r_min+u_r_max)+u_r,-0.1*(u_r_min+u_r_max)+u_r],  # Create a rectangle-like shape
        y=[0, h, h, 0,0],
        fill='toself',
        fillcolor='lightgrey',  # Transparent background to see the pattern
        line=dict(width=1, color='black'),
        name='Retaining Wall',
        showlegend=False,
        hoverinfo='skip',  # Skip the hover info for these layers
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
        x=[0, ((h-y_top)/h)*u_r],  
        y=[h, y_top],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='red', width=1, dash='dash'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    ))


    # add arrow  from to show the direction of passive 
    soil_layers_fig.add_annotation(
        x=0.8*u_r_max,  
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
        x=0.5*u_r_max,  # Position the text slightly to the right of the layer box
        y=0.8*y_top,
        text='Passive (compression)',  # Layer name as text
        font = dict(size=14, color="green", weight='bold'),
        showarrow=False,  # Don't show an arrow
        xanchor='center',  # Anchor text to the left
        yanchor='middle'  # Center text vertically with the midpoint
    )

    # add arrow  from to show the direction of  active
    soil_layers_fig.add_annotation(
        x=3*u_r_min,  
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
        x=2*u_r_min,  # Position the text slightly to the right of the layer box
        y=0.8*y_top,
        text='Active (extension)',  # Layer name as text
        font = dict(size=14, color="blue", weight='bold'),
        showarrow=False,  # Don't show an arrow
        xanchor='center',  # Anchor text to the left
        yanchor='middle'  # Center text vertically with the midpoint
    )

    # Add a line at the ground table
    soil_layers_fig.add_trace(go.Scatter(
        x=[u_r, 2*u_r_max], 
        y=[0, 0],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='black', width=2),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    )) 


    # add a line for the water table
    soil_layers_fig.add_trace(go.Scatter(
        x=[u_r, 2*u_r_max],  # Start at -1 and end at 1
        y=[water_table, water_table],  # Horizontal line at the top of the layer
        mode='lines',
        line=dict(color='blue', width=2, dash='dot'),
        showlegend=False,  # Hide legend for these lines
        hoverinfo='skip'  # Skip the hover info for these line
    ))

    # u vs k 
    u_data = np.linspace(2*u_r_min, 2*u_r_max, 500)
    k_0 = 1 - np.sin(np.radians(friction_angle))
    k_a_ult = (1 - np.sin(np.radians(friction_angle)))/(1 + np.sin(np.radians(friction_angle)))
    k_p_ult = 1/k_a_ult
    sigma_n =0

    a_a = 3.5
    a_b = 5

    k_a_data = k_0 - (k_0 - k_a_ult) * (1 - np.exp(-a_a * u_data[u_data < 0]/u_r_min))
    k_p_data =k_0 + (k_p_ult-k_0)  * (1 - np.exp(-a_b* (u_data[u_data > 0])/u_r_max))
    k = np.zeros_like(u_data)
    k[u_data < 0] = k_a_data
    k[u_data > 0] = k_p_data
    k[u_data == 0] = k_0

    k_a = k_0 - (k_0 - k_a_ult) * (1 - np.exp(-a_a * u_r/u_r_min))
    k_p = k_0 + (k_p_ult-k_0) * (1 - np.exp(-a_b * u_r/u_r_max))



    # create a trcae for the k vs u in yaxis 2
    soil_layers_fig.add_trace(go.Scatter(
        x=u_data,
        y=k,
        yaxis='y2',
        mode='lines',
        line=dict(color='red', width=3),
        name='K',
        showlegend=False
    ))

    # add a scatter point for k_a and k_p
    soil_layers_fig.add_trace(go.Scatter(
        x=[u_r],
        y=[k_a if u_r < 0 else k_p],
        yaxis='y2',
        mode='markers',
        marker=dict(color='blue' if u_r<0 else 'black' if u_r == 0 else 'green', size=10),
        name='Active_K' if u_r < 0 else 'K_0(At-rest)' if u_r == 0 else 'Passive_K',
        showlegend=False
    ))


   
    # First figure (soil_layers_fig)
    soil_layers_fig.update_layout(
        plot_bgcolor='white',
        xaxis_title= dict(text='u/h', font=dict(weight='bold')),
        xaxis=dict(
            range=[4*u_r_min, 2*u_r_max],  # Adjusting the x-range as needed
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
        # add another y-axis for k
        yaxis2=dict(
            title=dict(text='K', font=dict(weight='bold')),
            overlaying='y',
            side='left',
            range=[0, 1.1*k_p_ult],
            ticks='outside',
            title_standoff=4,
            ticklen=5,
            minor_ticks="inside",
            showline=True,
            linewidth=2,
            linecolor='black',
            zeroline=False,

        ),
        
        margin=dict(l=20, r=10),
    )



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
        sigma_h_a = sigma_v_0*k_a
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
        sigma_h_p = sigma_v_0*k_p 
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
    shear_stress_max = sigma_n * np.tan(np.radians(friction_angle))
    Mohr_circle_fig.add_trace(go.Scatter(
        x=[0, sigma_n],  # From origin to max normal stress
        y=[0, shear_stress_max],  # From cohesion to max shear stress
        mode='lines',
        line=dict(color='black', width=2),
        name='Critical State Line',
        showlegend=True
    ))

    Mohr_circle_fig.add_trace(go.Scatter(
        x=[0, sigma_n],  # From origin to max normal stress
        y=[0, -shear_stress_max],  # From cohesion to max shear stress
        mode='lines',
        line=dict(color='black', width=2),
        name='Critical State Line',
        showlegend=True
    ))



    Mohr_circle_fig.update_layout(
        # adding title to the plot at the center top
        title=dict(text='Mohr Circle for Effective Stresses at depth = h/2', 
                   x=0.5, 
                   xanchor='center', 
                   yanchor='top',
                    
                   font=dict(size=20, color='red', weight='bold', family='Arial', style='italic')
                   ),
   
        xaxis_title=dict(text='σ (kPa)', font=dict(weight='bold')),
        plot_bgcolor='white',
        xaxis=dict(
            range=[0, sigma_n],  # Adjusting the x-range as needed
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
            range=[-shear_stress_max, shear_stress_max],  # Adjusted range for the y-axis (inverted for depth)
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
