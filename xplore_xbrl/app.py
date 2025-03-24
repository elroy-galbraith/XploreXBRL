import streamlit as st
import os
from parse_xbrl import *
from viz_xbrl import *

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
        hierarchy_df["Parent Combined Label"] = hierarchy_df["Parent English Label"] + " / " + hierarchy_df["Parent Japanese Label"]
        hierarchy_df["Child Combined Label"] = hierarchy_df["Child English Label"] + " / " + hierarchy_df["Child Japanese Label"]

        unique_parents = ['All'] + sorted(hierarchy_df["Parent Combined Label"].unique())
        unique_children = ['All'] + sorted(hierarchy_df["Child Combined Label"].unique())

        col1, col2 = st.columns(2)
        with col1:
            selected_parent = st.selectbox('Select Parent (EN / JA)', unique_parents)
        with col2:
            selected_child = st.selectbox('Select Child (EN / JA)', unique_children)

        # Filter
        filtered_df = hierarchy_df.copy()
        if selected_parent != 'All':
            filtered_df = filtered_df[filtered_df["Parent Combined Label"] == selected_parent]
        if selected_child != 'All':
            filtered_df = filtered_df[filtered_df["Child Combined Label"] == selected_child]
            
        st.dataframe(filtered_df)

        # Update the treemap visualization with the filtered DataFrame
        fig = visualize_hierarchy(filtered_df)
        st.plotly_chart(fig)
        
        st.header('Visualize Calculations')
        calculations = parse_calculations(relationship_files["cal"], NAMESPACES)
        calculations_df = calculations_to_dataframe(calculations, labels)
        st.dataframe(calculations_df)
        
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
