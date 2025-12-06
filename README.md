# RIM Engine DE-LU – 4-Factor Risk Intelligence Model for the German/Luxembourg Power Market

This repository contains a **Risk Intelligence Model (RIM) engine** for the DE-LU day-ahead power market.  
It ingests real market fundamentals (prices, load, renewables) and constructs a **0–100 risk score** mapped into interpretable regimes.

The project is designed as a **quant/risk research tool** and a prototype for an **AI-driven risk assistant** for short-term power trading and portfolio management.

---

## 1. What this engine does

- Loads **real German day-ahead price data** (DE-LU zone) from SMARD.
- Merges it with:
  - **Grid load** (demand)
  - **Renewable generation (RES)** – wind, solar, biomass, hydro, etc.
- Constructs a **4-factor RIM framework**:

1. **RIM_PD** – Price Dynamics  
   - Volatility, returns, z-scores vs rolling window  
   - Detection of spikes and stress behaviour

2. **RIM_LD** – Load Dynamics  
   - Load ramps (1h/3h)  
   - Deviations vs 24h rolling baseline

3. **RIM_RES** – Renewable Dynamics  
   - Total RES output and ramps  
   - Undershoot / overshoot vs recent patterns

4. **RIM_IMB** – Imbalance Stress (proxy)  
   - Residual load = load – RES  
   - Residual ramps and positive stress indicators

Each factor is normalised to 0–10 and then aggregated into a **global RIM score (0–100)**, which is mapped into regimes:

- `REGIME_0_CALM`  
- `REGIME_1_NORMAL`  
- `REGIME_2_ATTENTION`  
- `REGIME_3_STRESSED`  
- `REGIME_4_SEVERE`

---

## 2. AI Agents: Analyst, Forecaster, Evaluator

On top of the numerical engine, the notebook defines an **AI agent layer** (currently with a dummy fallback if no API key is set):

- **Analyst LLM**  
  Takes the latest RIM context and produces:
  - short risk summary  
  - key diagnostics (price, load, RES, residual load)  
  - factor-level drivers (PD, LD, RES, IMB)

- **Forecaster LLM**  
  Produces qualitative scenarios for:
  - 0–6h horizon  
  - 6–24h horizon  
  With indications of:
  - price direction (UP / DOWN / SIDEWAYS / UNCERTAIN)  
  - volatility outlook  
  - regime transition risk

- **Evaluator LLM**  
  Acts as a **judge** over the Analyst/Forecaster outputs:
  - scores the quality of the briefing  
  - flags missing elements or weak structure  
  - suggests corrections

If no Gemini API key is configured, the notebook uses **deterministic dummy logic** so the full pipeline still runs end-to-end.

---

## 3. Notebook

The main entry point today is:

- `notebooks/rim_engine_4factor.ipynb` (currently located in repo root, will be moved into `/notebooks` in a later refactor)

It contains, in order:

1. Environment setup and imports  
2. Data loading from SMARD-exported CSV files (prices, load, RES)  
3. Feature engineering for price, load, and RES  
4. RIM factor construction (PD, LD, RES, IMB)  
5. Regime classification and 0–100 risk score  
6. Construction of a **latest risk context** object  
7. AI agent calls (Analyst, Forecaster, Evaluator)  
8. Generation of a **4-factor Risk Intelligence panel** in text + JSON-like form

---

## 4. Data

The project uses **publicly available SMARD data**, exported as CSV:

- `de_power_data.csv` – DE-LU day-ahead prices  
- `de_load_data.csv` – grid load (MWh)  
- `de_res_data.csv` – actual RES generation (15-min, aggregated to hourly)

These files are **not committed** to the public repo for size and licensing reasons.  
You can download equivalent datasets yourself from SMARD:

- SMARD data portal: https://www.smard.de

---

## 5. Roadmap

Planned future work:

- [ ] Refactor notebook logic into modular Python package under `/src`
- [ ] Add proper configuration layer (zones, horizons, factor weights)
- [ ] Integrate real LLM calls (Gemini or OpenAI) via API keys
- [ ] Add simple daily dashboard and plotting utilities
- [ ] Extend to additional bidding zones and cross-border spreads
- [ ] Introduce basic forecasting models (ML/TS) for RIM and prices
- [ ] Package as a reusable library + CLI tool

---

## 6. License

This project is released under the **MIT License**.
