# Finance Signal Lab

**A Tesla-inspired financial analytics portfolio prototype** (independent, not affiliated with Tesla).

A modern Streamlit web app that helps users explore synthetic manufacturing cost data through budget-to-actual analysis, reconciled price/quantity variances, a rule-based review queue, and a guided finance copilot.

## Pages
1. **Overview:** 4 KPI cards, cost-category comparison, monthly trend, and a direct link to investigate the largest unfavorable category.
2. **Variance Explorer:** reconciled budget-to-actual waterfall bridge, category breakdown, and cost driver explanation.
3. **Anomaly Monitor:** configurable percentage threshold and downloadable review queue. Flags are screening signals, not audit findings.
4. **Finance Copilot:** four guided, deterministic questions with supporting records. **Not a generative AI model.**
5. **About:** methods, technologies, data limitations and future development.

## Run locally on a Mac

```bash
cd finance_signal_lab_app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit opens a local browser tab (usually `http://localhost:8501`).

## Publish free using GitHub + Streamlit Community Cloud

1. Create a new **public** GitHub repository named `finance-signal-lab`.
2. Upload `app.py`, `analytics.py`, `sample_finance.csv`, `requirements.txt`, `.streamlit/config.toml`, `tests/` and this README to the repository root.
3. Visit https://share.streamlit.io and sign in with GitHub.
4. Choose **Create app** / **Deploy app**, select your repository and branch, set the main file path to `app.py`, then deploy.
5. Open the published link in an incognito window and check every page and filter before sharing.

No API keys or paid services required. Free-host availability and limits are controlled by Streamlit.

## Mathematical model

- Budget cost = budget quantity × budget unit price
- Actual cost = actual quantity × actual unit price
- Price effect = (actual unit price − budget unit price) × actual quantity
- Quantity effect = (actual quantity − budget quantity) × budget unit price
- **Price effect + quantity effect = actual cost − budget cost**

Positive variance indicates unfavorable cost increase. The price/quantity decomposition is valid for comparable items and quantity units, not for arbitrary mixed-unit aggregations interpreted as a single product.

## Data disclosure

`sample_finance.csv` contains **synthetic, illustrative** records. Names of locations are examples, not representations of actual site operations. There is no real Tesla financial data, proprietary information, live data access, LLM integration or predictive model.

## Run tests

```bash
pip install pytest
pytest -q
```
