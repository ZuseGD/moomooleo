# README

This repository contains a full analytical workflow for CM4 (Leo Cup) data, including:
- Data cleaning & normalization
- Debuffer classification (Speed / Stamina / Other)
- Finals & R1/R2 processing pipelines
- Meta share & win rate visualizations
- Kitasan LB correlation studies
- Exportable Excel summaries
- Reusable modular Python scripts

## 🔧 Project Structure


## 📊 Highlights
- **Bubble charts** showing meta share vs win rate
- **Debuffer impact heatmaps**
- **Team composition role archetype win rates**
- **Kitasan LB effects on performance**
- **Cross-round comparisons**

## 📦 Requirements
Python 3.10+

pip install pandas numpy matplotlib seaborn openpyxl xlsxwriter adjustText

## ▶ How to Run
1. Place raw CM data into: `data/raw/`
2. Run notebooks in order:
   - `01_data_cleaning.ipynb`
   - `02_feature_engineering.ipynb`
   - `03_finals_analysis.ipynb`
   - `04_rounds_analysis.ipynb`
3. Outputs will generate into:
   - `outputs/figures/`
   - `outputs/summary_excel/`

## 📚 Notes
This project is built to support future CMs with minimal changes.  
Place any future CM sheets into `data/raw/` and re-run the pipeline.

---
Maintained by **James Zhang**