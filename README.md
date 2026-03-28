# Data Workflow Studio

A Streamlit app for uploading a dataset, profiling it, cleaning and transforming a working copy, building matplotlib charts, and exporting the final dataset together with a transformation report and reproducible recipe.

## What is included

- Upload support for CSV, Excel, JSON, and public Google Sheets
- Two bundled sample datasets in `sample_data/`
- Upload & Overview page with shape, dtypes, summary stats, missingness, duplicates, and outlier summaries
- Cleaning & Preparation Studio with:
  - null handling
  - duplicate removal
  - type conversion and parsing
  - categorical standardization and mapping
  - rare category grouping
  - one-hot encoding
  - outlier capping or row removal
  - min-max and z-score scaling
  - rename/drop/formula/binning column operations
  - validation rules and exportable violation tables
- Visualization Builder using `matplotlib`
- Export page for cleaned CSV, Excel, transformation report, and JSON recipe
- Undo last step and reset-to-original workflow support

## Project structure

```text
app.py
src/
  data/
    functions/
  pages/
    upload/
    prepare/
    visualize/
    export/
sample_data/
examples/
task.md
AI_USAGE.md
```

## Run locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the app:

```bash
streamlit run streamlit_app.py
```

## Notes

- The task asks for a deployed Streamlit URL and a demo video; those are not generated locally in this repo.
- The task also asks for a report where AI use is forbidden, so that document is intentionally not authored here.
- Transformation recipes are exported as JSON, which is the recommended path from the task brief.
