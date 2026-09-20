# 🏭 MES Downtime Intelligence

Performance analytics and AI-generated reporting on Manufacturing Execution System (MES) data from a soda bottling line — finding where production time is lost, why, and what to do about it.

![Dashboard](docs/dashboard.png)

## The problem

A Manufacturing Execution System records what happens on the factory floor: every batch, operator, and downtime event. This project builds the **performance-analysis layer of an MES**: it turns raw production records into answers a plant manager needs:

- How efficient is the line, and how much time is lost?
- Which downtime causes matter most?
- Are losses driven by operator errors or by machines and materials?
- Where should training and maintenance be focused?

## Key findings

- **Line efficiency: 64.5%.** 18.8 of 53.0 hours were lost to downtime.
- **Five causes explain 80.8% of lost time:** machine failure, inventory shortage, machine adjustment, batch change, and batch coding error (Pareto analysis).
- **Losses split almost evenly:** 51.6% operator errors, 48.4% machines, materials, and other causes, so improvement needs both training *and* equipment/supply fixes.
- **Operator patterns (small sample, worth investigating rather than proof):** the largest operator-error areas were batch changes for one operator and machine adjustments for another; the best performer's methods could serve as a model; one operator's high lost time came mostly from causes outside their control.
- **Product type is not a major driver.** Efficiency was similar across products once batch size was accounted for.

## Pipeline

Raw CSVs → Clean & validate → Analyze → AI report → Dashboard

| Notebook | Purpose |
|---|---|
| `01_explore_data` | Explore raw data and identify quality issues |
| `02_clean_data` | Clean, validate, and reshape into analysis-ready tables |
| `03_analysis` | KPIs, Pareto analysis, operator and product performance |
| `04_model` | ML experiment: can batch features predict downtime? |
| `05_ai_report` | AI-generated performance report with a local LLM |

## Data engineering highlights

The raw data had several real-world quality issues, each found and fixed:

- Mixed file separators (pipe vs. comma)
- A duplicate header row inside the downtime table
- An Excel date artifact (`1900-01-01`) in one timestamp
- A batch that crossed midnight, which would have produced a negative duration
- 7 orphan downtime records with no matching production record (excluded and documented)

**Validation:** calculated lost time (actual − ideal batch time) was reconciled against recorded downtime for all 31 batches, with **zero mismatches**.

## AI approach

**1. Prediction experiment.** A random forest was tested against a mean baseline using leave-one-out cross-validation. It did **not** beat the baseline: 31 batches are too few, and about half of lost time (machine failures, shortages) can't be predicted from the available features. This was documented rather than overfit.

**2. AI-generated report.** A local open-source LLM (Llama 3.2 via Ollama, free, with no data leaving the machine) writes the report summary. Early versions showed the model misattributing numbers, so the design was changed:

- **Code generates every fact and recommendation** using explicit, explainable rules.
- **The LLM writes only a short narrative summary** from a few key facts.
- **A guardrail automatically checks** that every number in the summary appears in the source facts.

Sample output: [`reports/performance_report.md`](reports/performance_report.md)

## How to run

```bash
git clone https://github.com/YOUR-USERNAME/mes-downtime-intelligence.git
cd mes-downtime-intelligence
python -m venv venv
venv\Scripts\activate          # Windows (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app/dashboard.py
```

For the AI report, install [Ollama](https://ollama.com), run `ollama pull llama3.2:3b`, then run `notebooks/05_ai_report.ipynb`.

## Project structure
├── app/
│ ├── analysis.py # data loading and calculations
│ └── dashboard.py # Streamlit dashboard
├── data/
│ ├── (raw CSV files)
│ └── processed/ # cleaned tables
├── notebooks/ # 01–05, one per project stage
├── reports/ # generated performance report
└── docs/ # screenshots



## Limitations

- Only 31 batches over 5 production days, so operator-level differences are patterns, not proof.
- The dataset lacks machine sensor, maintenance, and inventory data, which would be needed to predict machine failures and shortages.

## Future work

- "Generate AI report" button inside the dashboard
- Date, operator, and product filters
- Predictive modeling on a larger dataset with sensor data

## Dataset

[Manufacturing Efficiency in Downtime Operations](KAGGLE-LINK-HERE) on Kaggle.

## Tech stack

Python · pandas · scikit-learn · Altair · Streamlit · Ollama (Llama 3.2)












