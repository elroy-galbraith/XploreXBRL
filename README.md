# 📊 Xplore

Ever looked at XBRL taxonomy files and thought, “What am I even looking at?” This tool makes sense of the chaos. It extracts financial concepts, connects them into a hierarchy, labels them in English and Japanese, and visualizes everything with an interactive treemap.

---

## 🚀 Features

- Parses English and Japanese labels from XBRL label linkbases.
- Extracts concept metadata (e.g. data type, balance type, substitution group) from the `.xsd` file.
- Builds a concept hierarchy from `_pre.xml` files.
- Enriches hierarchy with human-readable labels and metadata.
- **Interactive Filtering**: Allows users to filter the treemap visualization by selecting specific parent and child concepts.
- Saves to CSV for downstream processing.
- Visualizes the hierarchy using an interactive **Plotly treemap**.

---

## 🧰 Requirements

- Python 3.7+
- Install dependencies using Poetry:

```bash
poetry install
```

---

## 📁 Project Structure

```
.
├── app.py                          # Streamlit application
├── pyproject.toml                  # Poetry configuration file
├── README.md
|── タクソノミ
    ...
|   └── jppfs/
│       └── 2024-11-01/
│           ├── jppfs_cor_2024-11-01.xsd
│           ├── label/
│           │   ├── jp_lab.xml
│           │   └── en_lab.xml
│           └── r/
│               ├── *_pre.xml
│               ├── *_def.xml
│               └── *_cal.xml
```

---

## 🧪 Usage

Run the parser with:

```bash
poetry run streamlit run app.py
```

It will:
1. Load the XSD and label files
2. Parse the concept definitions and linkbase labels
3. Extract relationships from _pre.xml files
4. Provide an interactive interface to filter and visualize the hierarchy

- `xbrl_financial_concepts_with_labels.csv` – all financial concepts with metadata and labels
- `xbrl_financial_hierarchy.csv` – raw parent-child concept relationships
- `xbrl_financial_hierarchy_with_labels.csv` – enriched hierarchy with readable labels and metadata
- A treemap visualization will appear in your browser, with options to filter by parent and child concepts

---

## 📊 Example Output

| Concept ID       | Concept Name       | English Label       | Japanese Label       | ... |
|------------------|--------------------|---------------------|----------------------|-----|
| jp210000-000001  | CashEquivalents    | Cash and Equivalents| 現金及び同等物         | ... |

---

## ✍️ Author

Elroy Galbraith
Built as part of a financial data tooling project.

---

## 📄 License

MIT License. Use freely, contribute back if you find it useful!

---

## 📂 Source of Taxonomy Files

The taxonomy files used in this project were sourced from the Financial Services Agency (FSA) of Japan. You can find more information and access the files [here](https://www.fsa.go.jp/search/index.html).