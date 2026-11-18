# Quantum Financial Risk Intelligence Platform

A hybrid quantum-classical application that combines quantum machine learning algorithms with portfolio risk analytics and real-time market data streaming.

[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![Quantum Framework](https://img.shields.io/badge/Framework-PennyLane-9cf)](https://pennylane.ai/)
[![Web Framework](https://img.shields.io/badge/Web-Flask-lightgrey)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Overview

This project provides an interactive analytics dashboard for monitoring multi-asset mutual fund portfolios. It integrates quantum computing simulations to enhance portfolio risk assessment and detect behavioral shifts in asset management.

### Key Capabilities

- **Quantum Support Vector Machine (QSVM)**: Uses a parameterized 4-qubit quantum circuit to classify market regimes and detect style drift across fund holdings.
- **Quantum Value-at-Risk (Q-VaR)**: Implements phase-free Maximum Likelihood Amplitude Estimation (MLAE) to calculate 95% and 99% Value-at-Risk metrics with theoretical quadratic speedup over classical sampling.
- **Holdings Overlap Analysis**: Computes cross-fund asset commonalities to expose hidden concentration risks across multi-fund allocations.
- **Dynamic Safety Scoring**: Evaluates volatility, concentration levels, and regime indicators to assign a composite portfolio safety score (0–100).
- **Live Market Telemetry**: Streams real-time asset quotes and capital-at-risk indicators via Server-Sent Events (SSE).

---

## Project Structure

```text
├── app.py                     # Flask server and API routing
├── quantum_risk_analyzer.py   # QSVM, MLAE, and portfolio metric algorithms
├── collect_data.py            # Historical data collection module
├── requirements.txt           # Python dependencies
├── Procfile                   # Web process definition
├── vercel.json                # Vercel deployment configuration
├── .env.example               # Template for environment configuration
├── data/                      # Historical fund data and holdings cache
│   ├── combined_navs.csv
│   ├── daily_returns.csv
│   ├── fund_holdings.json
│   └── *.csv                  # Individual fund historical data
├── templates/
│   └── index.html             # Dashboard frontend interface
├── .gitignore                 # Git ignore rules
└── README.md                  # Project documentation
```

---

## Getting Started

### Prerequisites

- Python 3.10, 3.11, or 3.12
- Git
- (Optional) Finnhub API Key for live streaming market ticks (free registration at [finnhub.io](https://finnhub.io))

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Runa-Rameena/quantum-financial-risk-analyzer.git
   cd quantum-financial-risk-analyzer
   ```

2. **Create and activate a virtual environment:**
   - **On Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **On macOS/Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Copy the `.env.example` file to create your local environment file:
   - **On Windows (PowerShell):**
     ```powershell
     Copy-Item .env.example .env.local
     ```
   - **On macOS/Linux:**
     ```bash
     cp .env.example .env.local
     ```
   Add your Finnhub API key to `.env.local` if you wish to stream live market quotes. If left blank, simulated telemetry data will be used automatically.

---

## Running the Application

1. **(Optional) Fetch/Refresh historical market data:**
   ```bash
   python collect_data.py
   ```

2. **Start the Flask server:**
   ```bash
   python app.py
   ```

3. **Open the dashboard:**
   Navigate to `http://127.0.0.1:5000` in your web browser.

---

## API Summary

| Route | Method | Description |
|---|---|---|
| `/` | `GET` | Main interactive dashboard |
| `/api/funds` | `GET` | List of supported funds and underlying holdings |
| `/api/calculate_risk` | `POST` | Executes classical and quantum risk evaluation |
| `/api/stream_market` | `GET` | Server-Sent Events (SSE) live data stream |
| `/api/refresh_data` | `POST` | Fetches recent market data from Yahoo Finance |

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
