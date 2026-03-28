# DWV CW

## What This App Is For

This project is a **Streamlit data workflow app** for uploading a dataset, cleaning it, transforming it, visualizing it, and exporting the final results.

The app is designed to support a simple end-to-end workflow:

1. **Upload & Overview**  
   Load a CSV, Excel, or JSON dataset, or use one of the bundled sample datasets.
2. **Cleaning Studio**  
   Review missing values, duplicates, and data types, then apply cleaning and preparation steps.
3. **Visualization Builder**  
   Create charts from the transformed dataset using **Matplotlib**.
4. **Export & Report**  
   Download the cleaned dataset, saved charts, a transformation report, and a reproducible JSON recipe.

```text
streamlit_app.py
src/
  data/
    ..files
  pages/
    upload/
    prepare/
    visualize/
    export/
  sidebars/
    ..files
sample_data/
requirements.txt
task.md
AI_USAGE.md
.github/
.streamlit/
.gitignore
docker-compose.yml
Dockerfile
README.md
```
 
## How To Run
 
### Option 1: Run Locally
 
#### Prerequisites
 
- Python **3.11+**
- `pip`
 
#### Steps
 
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Then open:

```text
http://localhost:8501
```

### Option 2: Run With Docker

Build the image:

```bash
docker build -t dwv-cw .
```

Run the container:

```bash
docker run -p 8501:8501 dwv-cw
```

Then open:

```text
http://localhost:8501
```

### Option 3: Run With Docker Compose

```bash
docker compose up --build
```

Then open:

```text
http://localhost:8501
```

## Project Entry Point

The main app entry file is [`streamlit_app.py`].