Task: create a Streamlit app that lets users upload a dataset, clean it, transform and visualize it, ending with a final exported dataset + dashboard.

The flow should be like:

- User uploads a file (CSV/Exel/JSON)
- App profiles the data (types, missingness, duplicates, outliers)
- User selects cleaning & preparation actions from the UI
- App applies transformations to a working copy of the dataset.
- User dynamically creates visualizations from the transformed data.
- User exports the final dataset + a report of transformations performed.

App must support repeatable workflows: the same sequence of operations should be reproducible (via an exported “recipe” or logged steps).

## Page A **— Upload & Overview**

### Upload:

CSV / Excel / JSON: 

- ≥ 1,000 rows
- ≥ 8 columns
- Mixed types (numeric + categorical + datetime)
- Some missing values
- 2 sample datasets

### Display:

- shape (rows, cols)
- column names & inferred dtypes
- basic summary stats (numeric + categorical)
- missing values by column (count + %)
- duplicates count
- number of columns
- “Reset session” button.

## Page B - Cleaning & Preparation Studio

### Missing Values (Null Handling)

- Show missing value summarry (count + % per column)
- Offer per-column actions:
    - Drop rows with missing values (selected columns)
    - Drop columns with missing values above a threshold(%)
    - Replace with:
        - constant value (user input)
        - mean/median/mode (numeric)
        - most frequent (categorical)
        - forward fill /backward fill(time series)
- Must show a before/after preview (e.g., row count + affected colulmns).

### Dublicates

- Detect dublicats:
    - full-row duplicates
    - duplicates by subset of columns (user-selected keys)
- Provide actions:
    - remove duplicates (keep first/keep last)
    - show duplicates groups in a table

### Data Types & Parsing

- Provide tools to:
    - convert column types: numeric, categorical, datetime
    - datetime parsing with format selection ( or auto parse with errors coerced)
    - handle “dirty numeric” strings (commas, currency signs)

### Categorical Data Tools

- Value standardization
    - trim whitespace, lower/title case
- Mapping/ replacement
    - user provides a mapping dictionary (UI table editor)
    - apply mapping; unmatched values remain unchanged (or optional “set to Other”)
- Rare category grouping
    - group categories below a frequency threshold into “Other”
- One-hot encoding

### Numeric Cleaning

- Outlier detection summary (simple IQR or z-score)
- User chooses action:
    - cap/winsorize at quantiles
    - remove outlier rows
    - do nothing
- Must show impact (rows removed or values capped).

### Normalization/Scaling

- Min-max scaling
- Z-score standardization must allow the user to choose columns and show before/after stats.

### Column Operations

- Rename columns
- Drop columns
- Create new column using:
    - simple formulas (e.g., colA / colB, log(col), colA - mean(colA))
    - binning numeric columns into categories (equal-width or quantile bins)

### Data Validations Rules

User can define basic rules and see violations:

- numeric range check (min/max)
- allowed categories list
- Non-null constraints for selected columns. The app should show the “violations table” and allow export.

## **Page C — Visualization Builder:**

### Choose ur chart:

> must use **matplotlib**
> 
- User selection:
    - Plot type:
        - histogram
        - box plot
        - scatter plot
        - line chart (time series)
        - bar chart (grouped)
        - heatmap or correlation matrix (numeric only)
    - x and y columns
    - *optional* color/group column
    - *optional* aggregation (sum/mean/count/median)
- showing “top N” for bar charts
- filtering (by category and numeric range at least)

## **Page D — Export & Report:**

- Export cleaned dataset (CSV + optionally Excel)
- Export a **transformation report**:
    - list of steps
    - parameters used
    - timestamp
- Export either:
    - a JSON “recipe” (recommended), or
    - a Python script snippet that replays the pipeline (stretch)

## Commit history:

### **Transformation Log:**

- each step: operation name + parameters + affected columns
- show log to the user
- allow “undo last step” OR “reset all” (one is required)

### **Performance:**

- Must not re-run heavy steps unnecessarily:
    - use st.cache_data for loading and profiling
    - keep a working dataframe in st.session_state

### **Safety / Guardrails:**

- Don’t crash on bad input.
- user-friendly error messages.
- Validate column selections (e.g., scaling only numeric columns).

## Deliverables:

### Zip

- app.py (or streamlit_app.py)
- requirements.txt
- README.md
- sample_data/ with at least two dataset
- All chat and prompts used from A to Z for the dev

### Transformation report output (example file)

### AI_USAGE.md

- what we verified manually
