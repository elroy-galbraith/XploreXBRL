import streamlit as st
import os
from parse_xbrl import *
import plotly.express as px

st.set_page_config(layout="wide")

# Streamlit app title
def main():
    st.title('Xplore XBRL')
    
    st.write("""
    This app allows you to explore the XBRL taxonomy files for the Japanese Financial Reporting Standards (JFRs).
    
    The app currently supports the following standards:
    - JPPFS (Japanese Private Placement Fund Standards)
    - JPPS (Japanese Public Placement Standards)
    
    """)
    
    # Configuration
    XSD_FOLDER = "タクソノミ/taxonomy/jppfs/2024-11-01"
    XSD_FILE = os.path.join(XSD_FOLDER, "jppfs_cor_2024-11-01.xsd")
    LABEL_FOLDER = os.path.join(XSD_FOLDER, "label")
    R_FOLDER = os.path.join(XSD_FOLDER, "r")
    
    NAMESPACES = {
        "xs": "http://www.w3.org/2001/XMLSchema",
        "link": "http://www.xbrl.org/2003/linkbase",
        "xlink": "http://www.w3.org/1999/xlink",
        "xbrli": "http://www.xbrl.org/2003/instance",
    }
    
    try:
        
        labels = parse_labels(LABEL_FOLDER, NAMESPACES)
        concepts = parse_xsd(XSD_FILE, labels, NAMESPACES)
        relationship_files = find_relationship_files(R_FOLDER)
        hierarchy = extract_hierarchy(relationship_files["pre"], NAMESPACES)
        hierarchy_df = build_hierarchy_dataframe(hierarchy, labels, concepts)
            
        st.header('Visualize Hierarchy')
        # Extract unique parent and child labels
        unique_parents = ['All'] + list(hierarchy_df['Parent English Label'].unique())
        unique_children = ['All'] + list(hierarchy_df['Child English Label'].unique())

        # Add Streamlit widgets for filtering
        col1, col2 = st.columns(2)
        with col1:
            selected_parent = st.selectbox('Select Parent', unique_parents)
        with col2:
            selected_child = st.selectbox('Select Child', unique_children)

        # Filter the DataFrame based on selections
        if selected_parent != 'All':
            hierarchy_df = hierarchy_df[hierarchy_df['Parent English Label'] == selected_parent]
        if selected_child != 'All':
            hierarchy_df = hierarchy_df[hierarchy_df['Child English Label'] == selected_child]

        # Update the treemap visualization with the filtered DataFrame
        fig = visualize_hierarchy(hierarchy_df)
        st.plotly_chart(fig)
    except Exception as e:
        st.error(f"An error occurred: {e}")

def visualize_hierarchy(df):
    fig = px.treemap(df,
                     path=["Parent English Label", "Child English Label"],
                     values=[1] * len(df),
                     title="XBRL Financial Hierarchy (English Labels)")
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    return fig

if __name__ == "__main__":
    main()
