import streamlit as st
import os
import xml.etree.ElementTree as ET
import pandas as pd
import csv
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

# Function to parse labels
def parse_labels(label_folder, namespaces):
    labels_dict = {}
    for file in os.listdir(label_folder):
        if file.endswith("_lab.xml") or file.endswith("lab-en.xml"):
            path = os.path.join(label_folder, file)
            tree = ET.parse(path)
            root = tree.getroot()

            concept_map = {
                loc.attrib.get("{http://www.w3.org/1999/xlink}label"): loc.attrib.get("{http://www.w3.org/1999/xlink}href", "").split("#")[-1]
                for loc in root.findall(".//link:loc", namespaces)
            }

            label_map = {}
            for label in root.findall(".//link:label", namespaces):
                label_id = label.attrib.get("{http://www.w3.org/1999/xlink}label")
                lang = label.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", "N/A")
                if label_id and lang in ["ja", "en"]:
                    label_map.setdefault(label_id, {})[lang] = label.text.strip() if label.text else ""

            for arc in root.findall(".//link:labelArc", namespaces):
                concept_ref = arc.attrib.get("{http://www.w3.org/1999/xlink}from")
                label_ref = arc.attrib.get("{http://www.w3.org/1999/xlink}to")
                concept_name = concept_map.get(concept_ref)
                if concept_name and label_ref in label_map:
                    labels_dict.setdefault(concept_name, {"concept_id": concept_ref, "ja": "N/A", "en": "N/A"})
                    labels_dict[concept_name].update(label_map[label_ref])
    return labels_dict

# Function to parse XSD file
def parse_xsd(xsd_file, labels_dict, namespaces):
    concepts = []
    tree = ET.parse(xsd_file)
    root = tree.getroot()
    for element in root.findall(".//xs:element", namespaces):
        concept_name = element.attrib.get("name", "Unknown")
        concept_id = element.attrib.get("id", "Unknown")
        data_type = element.attrib.get("type", "Unknown")
        substitution_group = element.attrib.get("substitutionGroup", "N/A")
        balance_type = element.attrib.get("{http://www.xbrl.org/2003/instance}balance", "N/A")
        ja_label = labels_dict.get(concept_id, {}).get("ja", "N/A")
        en_label = labels_dict.get(concept_id, {}).get("en", "N/A")
        concepts.append([concept_id, concept_name, en_label, ja_label, data_type, substitution_group, balance_type])
    return concepts

# Function to find relationship files
def find_relationship_files(folder):
    files = {"pre": [], "def": [], "cal": []}
    for subdir, _, file_list in os.walk(folder):
        for file in file_list:
            path = os.path.join(subdir, file)
            if "_pre_" in file:
                files["pre"].append(path)
            elif "_def_" in file:
                files["def"].append(path)
            elif "_cal_" in file:
                files["cal"].append(path)
    return files

def extract_hierarchy(pre_files, namespaces):
    hierarchy = {}
    for file in pre_files:
        tree = ET.parse(file)
        root = tree.getroot()
        for arc in root.findall(".//link:presentationArc", namespaces):
            parent = arc.attrib.get("{http://www.w3.org/1999/xlink}from")
            child = arc.attrib.get("{http://www.w3.org/1999/xlink}to")
            if parent and child:
                hierarchy.setdefault(parent, []).append(child)
    return hierarchy

def build_hierarchy_dataframe(hierarchy, labels_dict, concepts_list):
    df = pd.DataFrame([(p, c) for p, children in hierarchy.items() for c in children], columns=["Parent", "Child"])

    label_lookup = {row[0]: {"English Label": row[2], "Japanese Label": row[3],
                             "Data Type": row[4], "Substitution Group": row[5], "Balance Type": row[6]}
                    for row in concepts_list}

    df["Parent English Label"] = df["Parent"].map(lambda x: label_lookup.get(x, {}).get("English Label", x))
    df["Parent Japanese Label"] = df["Parent"].map(lambda x: label_lookup.get(x, {}).get("Japanese Label", x))
    df["Child English Label"] = df["Child"].map(lambda x: label_lookup.get(x, {}).get("English Label", x))
    df["Child Japanese Label"] = df["Child"].map(lambda x: label_lookup.get(x, {}).get("Japanese Label", x))
    df["Data Type"] = df["Parent"].map(lambda x: label_lookup.get(x, {}).get("Data Type", "N/A"))
    df["Substitution Group"] = df["Parent"].map(lambda x: label_lookup.get(x, {}).get("Substitution Group", "N/A"))
    df["Balance Type"] = df["Parent"].map(lambda x: label_lookup.get(x, {}).get("Balance Type", "N/A"))

    return df

def visualize_hierarchy(df):
    fig = px.treemap(df,
                     path=["Parent English Label", "Child English Label"],
                     values=[1] * len(df),
                     title="XBRL Financial Hierarchy (English Labels)")
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    return fig

if __name__ == "__main__":
    main()
