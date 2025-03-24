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
        df = parse_lab_xml("タクソノミ/taxonomy/jppfs/2024-11-01/label/jppfs_2024-11-01_lab.xml", NAMESPACES)
        # st.dataframe(df.head())
        
        relationship_files = find_relationship_files(R_FOLDER)
        # st.write(relationship_files["cal"])
        
        final_df = pd.DataFrame()
        for cal_file in relationship_files["cal"]:
            calc_df = parse_calculations(cal_file, NAMESPACES)
            final_df = pd.concat([final_df, calc_df])
        # st.write(final_df.head())
        
        enriched_df = enrich_calculations_with_labels(final_df, df)
        st.dataframe(enriched_df.head())
        
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
