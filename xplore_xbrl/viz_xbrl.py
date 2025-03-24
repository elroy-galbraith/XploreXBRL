import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import networkx as nx
from pyvis.network import Network
import tempfile
import streamlit as st

def build_calc_graph(enriched_df):
    G = nx.DiGraph()

    # Add edges with labels
    for _, row in enriched_df.iterrows():
        parent = row['from']
        child = row['to']
        parent_label = row['japanese_from'] or parent
        child_label = row['japanese_to'] or child

        G.add_node(parent, label=parent_label)
        G.add_node(child, label=child_label)
        G.add_edge(parent, child, weight=row.get('weight', 1))

    return G

def show_graph_in_streamlit(G, height=600):
    net = Network(height=f"{height}px", directed=True, notebook=False)
    net.from_nx(G)

    net.repulsion(node_distance=120, spring_length=200)
    net.set_options("""
    var options = {
      "nodes": {
        "font": {
          "size": 16,
          "face": "arial"
        }
      },
      "edges": {
        "arrows": {
          "to": {
            "enabled": true
          }
        }
      }
    }
    """)

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        net.save_graph(tmp_file.name)
        tmp_path = tmp_file.name

    # Read HTML and embed
    with open(tmp_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    st.components.v1.html(html_content, height=height, scrolling=True)

    # Clean up
    os.remove(tmp_path)
