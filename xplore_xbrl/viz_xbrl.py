import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def visualize_hierarchy(df):
    fig = px.treemap(
        df, 
        path=['Parent', 'Child'], 
        values=[1] * len(df), 
        color='Balance Type',
        hover_data=['Parent English Label', 'Child English Label']
    )
    fig.update_layout(
        title='XBRL Hierarchy',
        margin=dict(t=50, l=25, r=25, b=25)
    )
    
    return fig

def visualize_calculations(calculations, labels_dict):
    fig = go.Figure()

    for parent, children in calculations.items():
        for child, weight in children:
            parent_label = labels_dict.get(parent, {}).get("English Label", parent)
            child_label = labels_dict.get(child, {}).get("English Label", child)
            # Ensure the line width is non-negative
            line_width = max(float(weight) * 2, 0.5)  # Use a minimum width of 0.5
            fig.add_trace(go.Scatter(
                x=[parent, child],
                y=[0, 1],
                mode='lines+markers+text',
                text=[f"{parent_label} ({parent})", f"{child_label} ({child})"],
                line=dict(width=line_width),
                hoverinfo='text'
            ))

    fig.update_layout(
        title='XBRL Calculations',
        xaxis_title='Elements',
        yaxis_title='Hierarchy Level',
        showlegend=False,
        margin=dict(t=50, l=25, r=25, b=25)
    )
    return fig
