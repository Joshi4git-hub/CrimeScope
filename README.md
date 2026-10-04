# CrimeScope — Chicago Crime Analytics & Prediction Dashboard

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Dash](https://img.shields.io/badge/Dash-2.14%2B-orange.svg)](https://dash.plotly.com/)
[![Plotly](https://img.shields.io/badge/Plotly-Dark-black.svg)](https://plotly.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-green.svg)](https://scikit-learn.org/)

**CrimeScope** is a production-quality Data Analytics and Visualization (DAV) web application designed to explore, map, analyze, and predict spatio-temporal crime patterns across the City of Chicago. Built using the official Chicago Police Department CLEAR dataset (City of Chicago Data Portal, dataset `ijzp-q8t2`).

---

## 🌟 Key Features

- **Dark SaaS Analytics Dashboard**: Premium dark-mode UI with `#0B0B0B` background, custom glowing card containers, Inter typography, and orange/amber/yellow color palettes.
- **Global Filter State**: Filter all pages dynamically by Crime Category, Police District, Year Range (2020–2024), Arrest Status, and Domestic Incident status via an offcanvas drawer.
- **7 Comprehensive Views**:
  1. **Overview**: KPI summary cards with micro sparklines, Crime Volume Trend (grouped by Year/Month/Day/Hour), Donut distribution, Hour × Day Heatmap, Top Districts ranking, and auto-generated analytical insights.
  2. **Trends**: Multi-period seasonality, 24-hour crime profile, weekday comparison, and a multi-category line comparison tool.
  3. **Map**: Dark geospatial visualization featuring Heatmap, Sampled Points (up to 20,000 incidents), and District Bubbles views, paired with a Top 10 Community Areas side panel.
  4. **Districts**: Police District volume benchmarks, Top 15 Community Areas, and a detailed breakdown table showing arrest rates and domestic incident shares.
  5. **Prediction**: Interactive machine-learning estimation tool predicting primary crime categories from hour, day, month, and district with class probability breakdown.
  6. **Model Comparison**: Supervised benchmark evaluating `RandomForestClassifier`, `LogisticRegression`, and `DecisionTreeClassifier` with metrics, confusion matrix heatmaps, and Gini feature importances.
  7. **About & Data**: Data provenance citations, preprocessing logs, interactive column dictionary, and one-click CSV data exporter.

---

## 🛠️ Tech Stack

- **Framework**: Dash (Plotly Dash) & `dash-bootstrap-components`
- **Data Processing**: Pandas, NumPy, PyArrow
- **Visualization**: Plotly Graph Objects & Express (Custom `crimescope_dark` template)
- **Machine Learning**: Scikit-Learn (`RandomForestClassifier`, `LogisticRegression`, `DecisionTreeClassifier`, `ColumnTransformer`, `Pipeline`)
- **Model Persistence**: Joblib
- **Styling**: Custom CSS (`assets/custom.css`), Google Fonts (Inter), Bootstrap Icons

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Installation
Clone or navigate to the repository directory and install required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Data Setup & Preprocessing
The application automatically checks for raw data in `data/raw/crimes.csv`. If missing, you can download recent data from the Chicago Socrata API or generate a fallback dataset:

- **Generate Synthetic Dataset (Offline/Fast, 50,000 rows)**:
  ```bash
  python scripts/make_sample_data.py
  ```
- **Fetch Socrata API Dataset (2020–2024)**:
  ```bash
  python scripts/download_data.py
  ```
- **Process & Preprocess Dataset**:
  ```bash
  python src/data_prep.py
  ```

### 4. Train Machine Learning Models
```bash
python src/ml.py
```

### 5. Launch the Dashboard
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:8050`**

---

## 📸 Screenshots

| View | Preview |
| :--- | :--- |
| **Overview Page** | ![Overview](docs/screenshots/overview.png) |
| **Trends Analysis** | ![Trends](docs/screenshots/trends.png) |
| **Chicago Map** | ![Map](docs/screenshots/map.png) |
| **Police Districts** | ![Districts](docs/screenshots/districts.png) |
| **ML Risk Prediction** | ![Prediction](docs/screenshots/prediction.png) |
| **Model Comparison** | ![Model Comparison](docs/screenshots/model_comparison.png) |
| **About & Data** | ![About & Data](docs/screenshots/about.png) |

---

## 🤖 Machine Learning Model Benchmarks

| Model Architecture | Accuracy | Weighted Precision | Weighted Recall | Weighted F1 | Train Time (s) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **RandomForestClassifier** | **8.45%** | **9.42%** | **8.45%** | **9.38%** | 1.10s |
| **DecisionTreeClassifier** | 4.59% | 4.88% | 4.59% | 3.65% | 0.35s |
| **LogisticRegression** | 4.41% | 2.80% | 4.41% | 3.10% | 0.29s |

> [!NOTE]
> **Methodological Note on Predictive Limitations**:
> Predicting specific crime categories solely from spatio-temporal features (hour, day, district, location coordinates) is an inherently difficult multi-class problem (13 distinct categories). Moderate predictive accuracy is expected due to high variance and overlapping spatial-temporal patterns across crime types. Outputs from the prediction page are provided as model estimates based on historical patterns, not certainty.

---

## 📜 Citation & License

Data provided by the **Chicago Police Department CLEAR system** via the City of Chicago Data Portal (`ijzp-q8t2`). Crime records are preliminary and subject to investigation updates; geographic locations are anonymized to block centroids.
