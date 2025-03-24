# --- parse_xbrl.py ---
import os
import xml.etree.ElementTree as ET
import pandas as pd

def parse_lab_xml(filepath, namespaces):
    tree = ET.parse(filepath)
    root = tree.getroot()

    # Collect labels: id → (text, label)
    label_map = {}
    for label in root.findall('.//link:label', namespaces):
        role = label.get('{http://www.w3.org/1999/xlink}role')
        if role != "http://www.xbrl.org/2003/role/label":
            continue
        id_ = label.get('id')
        text = label.text
        label_ = label.get('{http://www.w3.org/1999/xlink}label')
        label_map[label_] = {
            'id': id_,
            'japanese': text,
            'label': label_
        }

    # Collect arcs (linking loc "from" to label "to")
    arcs = []
    for arc in root.findall('.//link:labelArc', namespaces):
        from_ = arc.get('{http://www.w3.org/1999/xlink}from')
        to_ = arc.get('{http://www.w3.org/1999/xlink}to')
        if to_ in label_map:
            entry = label_map[to_].copy()
            entry['from'] = from_
            entry['to'] = to_
            arcs.append(entry)

    return pd.DataFrame(arcs)

# Find relationship files
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

# 
def parse_calculations(filepath, namespaces):
    tree = ET.parse(filepath)
    root = tree.getroot()

    calc_arcs = []
    for arc in root.findall('.//link:calculationArc', namespaces):
        from_label = arc.get('{http://www.w3.org/1999/xlink}from')
        to_label = arc.get('{http://www.w3.org/1999/xlink}to')
        weight = arc.get('weight')
        order = arc.get('order')
        calc_arcs.append({
            'from': from_label,
            'to': to_label,
            'weight': weight,
            'order': order
        })
    return pd.DataFrame(calc_arcs)

def enrich_calculations_with_labels(calc_df, label_df):
    # Rename columns in label_df to avoid collisions
    label_from = label_df.rename(columns={
        'id': 'id_from',
        'japanese': 'japanese_from',
        'from': 'label_from',
        'to': 'label_to_from'
    })

    label_to = label_df.rename(columns={
        'id': 'id_to',
        'japanese': 'japanese_to',
        'from': 'label_to',
        'to': 'label_to_to'
    })

    # Merge: calc.from == label.label
    merged = calc_df \
        .merge(label_from, left_on='from', right_on='label_from', how='left') \
        .merge(label_to, left_on='to', right_on='label_to', how='left')

    return merged[[
        'from', 'japanese_from', 'to', 'japanese_to', 'weight', 'order'
    ]]
    