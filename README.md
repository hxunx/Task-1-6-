# Group 5 — Cosmetics Ingredient Finder & Comparison

**Course:** Data Literacy Foundations, 2026 Fall  
**Final Project — Task 1:** Data Exploration & Service Idea  
**Team:** Group 5 (check members and student IDs in the notebook's `CONFIG` cell before submitting)

## Project idea

Our proposed interactive website lets users choose a skincare category, desired ingredients, ingredients to avoid, a skin-type tag (if available in the data), and a maximum price. The service filters real products and explains why each item matches. Users can compare two product ingredient lists to find shared and unique ingredients, or find lower-priced products with similar lists.

**Input → Data analysis → Output:** preferences and price ceiling → category/price/ingredient filtering, set comparison → candidate list and ingredient differences.

This is a **product-information comparison tool**, not a medical/safety recommendation.

## Data sources

1. **Selected:** [Cosmetics Datasets](https://www.kaggle.com/datasets/kingabzpro/cosmetics-datasets) — Kaggle, `kingabzpro/cosmetics-datasets`. Intended fields include product, brand, category, listed price, rating, full ingredient string, and skin-type tags.
2. **Comparison candidate:** [Skincare Products Clean Dataset](https://www.kaggle.com/datasets/eward96/skincare-products-clean-dataset) — Kaggle, `eward96/skincare-products-clean-dataset`. Product, type, ingredient list, and listed price; fewer filtering fields.

The source files are **not included** in this repository. The notebook fetches them through `kagglehub`, or reads locally downloaded CSV files via the environment variables described below. **Check each dataset's actual license, attribution and redistribution conditions on Kaggle before publishing source data**. Data-source update periods and product prices may be historical.

## Files

| File | Role |
|---|---|
| `data_exploration.ipynb` | Reproducible data inspection, quality checks, EDA, figures, and service prototypes |
| `build_report.py` | Generates the 2–3-page Task 1 report from actual notebook results |
| `requirements.txt` | Python dependencies |
| `SUBMISSION_CHECKLIST.md` | Submission steps and remaining verification tasks |

The notebook creates `outputs/Task1_Report.pdf`, `outputs/eda_figure.png`, `outputs/results.json`, `outputs/summary_by_category.csv` and `outputs/top_ingredients.csv` **only after it runs successfully on real data**.

## Run the analysis

From the repository folder:

```bash
python -m pip install -r requirements.txt
jupyter notebook
```

Open `data_exploration.ipynb`. In the first `CONFIG` code cell, confirm the **Group 5** member names and IDs, paste in the **real GitHub repository URL**, and verify the dataset license/provenance. Select **Kernel → Restart & Run All**. If Kaggle authentication is required, follow [KaggleHub setup](https://github.com/Kaggle/kagglehub) and retry.

Alternatively, download the selected Kaggle dataset CSV and set `COSMETICS_CSV` to its path before launching Jupyter. Optionally set `COSMETICS_B_CSV` for the comparison candidate. The report can use a documented secondary source for Candidate B's profile if its CSV is unavailable, but the selected dataset **must** be loaded and analyzed.

### Windows PowerShell example for a local CSV

```powershell
$env:COSMETICS_CSV="C:\path\to\cosmetics.csv"
jupyter notebook
```

### macOS / Linux shell example

```bash
export COSMETICS_CSV="/path/to/cosmetics.csv"
jupyter notebook
```

## Create and use the team's GitHub repository

1. Sign in to GitHub → **New repository** (e.g., `group5-cosmetic-match`).
2. Upload this folder's `data_exploration.ipynb`, `build_report.py`, `requirements.txt`, `README.md` and `SUBMISSION_CHECKLIST.md`. Do not upload restricted source CSV files.
3. Copy the repository URL, e.g. `https://github.com/ACCOUNT/group5-cosmetic-match`.
4. Replace `CONFIG["github_url"]` in the notebook with your *actual* URL; **the placeholder is not a valid submission link**.
5. Run the notebook against real Kaggle data to generate the actual PDF and figure; review the results and upload the PDF or submit it as your instructor requires.
6. Confirm that the GitHub repository link appears in the generated PDF and opens the code files.

## Data integrity and limitations

- The notebook is built to calculate every numeric result, sample record, chart, and observation from loaded CSV data. It does **not** contain a pre-filled or fabricated EDA report.
- Preliminary exploratory filter: `price > 0` and at least three parsed ingredients. Cleaning, matching synonyms, and duplicate resolution are Task 2 decisions.
- Name normalization matters: e.g. `water` and `aqua` may refer to the same ingredient. A missing term or a binary skin-type tag does **not** prove that a product is clinically safe or appropriate.
- The team's analysis must accurately distinguish **product-catalog ingredient frequency** from sales or consumer popularity.
