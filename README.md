<div align="center">

# ⚛️ Quantum Risk Intelligence Platform
### Interactive Portfolio Risk Management & Quantum Simulation Engine

[![Live Demo](https://img.shields.io/badge/Live%20Demo-quantum--risk--analyzer.vercel.app-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://quantum-risk-analyzer.vercel.app/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PennyLane](https://img.shields.io/badge/PennyLane-QML-29B5E8?style=for-the-badge&logo=quantum&logoColor=white)](https://pennylane.ai/)
[![Flask](https://img.shields.io/badge/Flask-Web%20App-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

<br/>

🌐 **Live Application:** [https://quantum-risk-analyzer.vercel.app/](https://quantum-risk-analyzer.vercel.app/)

<p align="center">
  A full-stack financial technology application integrating quantum machine learning simulations with real-time market data streaming to evaluate portfolio risks, identify cross-fund overlaps, and detect asset style shifts.
</p>

[Live Demo](https://quantum-risk-analyzer.vercel.app/) • [Overview](#-overview) • [Core Features](#-core-features) • [Dashboard Modules](#-dashboard-modules) • [Project Layout](#-project-layout) • [Getting Started](#-getting-started) • [API Reference](#-api-reference)

</div>

---

## 🔍 Overview

Managing multi-asset mutual fund portfolios requires tracking subtle asset shifts and concentration risks that basic variance metrics often miss. 

This platform provides investors and analysts with an interactive suite of risk evaluation tools:
- **Live Cloud Deployment**: Accessible online at [quantum-risk-analyzer.vercel.app](https://quantum-risk-analyzer.vercel.app/).
- **Quantum Simulation Backend**: Uses PennyLane quantum circuits to simulate quantum machine learning models on classical hardware.
- **Style Shift Detection**: Classifies market dynamics into Bull, Bear, and Volatile regimes to detect when funds drift outside their expected mandate.
- **Quantum Value-at-Risk**: Employs Maximum Likelihood Amplitude Estimation (MLAE) to calculate tail loss estimates.
- **Holdings Overlap Matrix**: Analyzes underlying equity allocations across funds to expose hidden stock concentrations.
- **Live Streaming Ticks**: Connects to financial APIs with Server-Sent Events (SSE) for continuous intraday tracking.

---

## ⚡ Core Features

### 1. Quantum Support Vector Machine (QSVM)
- **Parameterized Circuit**: Maps a 4-dimensional normalized vector of rolling returns, volatility, and benchmark correlations onto a 4-qubit quantum state using single-qubit $R_Y$ rotations.
- **Entangling Layers**: Circular CNOT gates introduce multi-qubit entanglement to capture higher-order relationships.
- **Regime Classification**: Evaluates quantum kernel matrices to predict current risk regimes (Bull/Stable, Bear/Crisis, Volatile) and alert users to potential manager mandate drift.

### 2. Quantum Amplitude Estimation (MLAE)
- **Phase-Free Estimation**: Avoids deep Quantum Phase Estimation circuits by measuring Grover iterations across scheduled powers.
- **Likelihood Reconstruction**: Maximizes the binomial log-likelihood across measurement outcomes to compute 95% and 99% Value-at-Risk limits.

### 3. Mutual Fund Overlap Analysis
- **Underlying Equity Breakdown**: Cross-references top holdings across broad-market, growth, dividend, balanced, and bond funds.
- **Pairwise Concentration**: Highlights when separate funds carry duplicate exposure to the same underlying mega-cap equities.

### 4. Dynamic Safety Scoring
- Generates a composite score from 0 to 100 reflecting:
  - Volatility alignment relative to user risk profile (Conservative, Balanced, Aggressive).
  - Cross-fund duplication penalties.
  - Active drift warnings flagged by the QSVM classifier.

### 5. Live Telemetry & Capital-at-Risk (CaR)
- Streams real-time market updates over an SSE channel.
- Tracks dynamic portfolio valuation, intraday drift, and real-time Capital-at-Risk metrics.
- Seamlessly falls back to simulated market dynamics if no external API key is supplied.

---

## 🖥️ Dashboard Modules

| Module Tab | Description |
| :--- | :--- |
| **Portfolio Architect** | Dynamic allocation sliders, Three.js 3D money flow, and pairwise holdings overlap analysis. |
| **Quantum Risk Simulator** | Side-by-side comparison of classical and quantum-estimated Value-at-Risk at 95% and 99% confidence. |
| **QSVM Style Drift** | Visualizer for 4-qubit quantum states, regime probability distributions, and active drift alerts. |
| **Live Market Stream** | Real-time quote board, portfolio net drift, live Capital-at-Risk ticker, and VIX indicators. |
| **Cognitive AI Advisor** | Interactive suggestions for rebalancing and history of simulated fund manager reallocation actions. |

---

## 📂 Project Layout

```text
quantum-financial-risk-analyzer/
├── code/
│   ├── app.py                     # Flask server and streaming endpoints
│   ├── quantum_risk_analyzer.py   # QSVM, MLAE, and classical risk calculation engine
│   ├── collect_data.py            # Financial data retrieval script
│   ├── requirements.txt           # Python dependencies
│   ├── Procfile                   # Cloud process specification
│   ├── vercel.json                # Vercel deployment configuration
│   ├── .env.example               # Environment variables template
│   ├── data/                      # Historical prices and fund holdings database
│   │   ├── combined_navs.csv
│   │   ├── daily_returns.csv
│   │   ├── fund_holdings.json
│   │   └── *.csv
│   └── templates/
│       └── index.html             # Glassmorphic single-page web dashboard
├── .gitignore                     # Excludes local environments and secret keys
└── README.md                      # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12
- Git installed on your system
- *(Optional)* Free API key from [Finnhub](https://finnhub.io) for real-time market feeds

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Runa-Rameena/quantum-financial-risk-analyzer.git
   cd quantum-financial-risk-analyzer
   ```

2. **Navigate into the code directory:**
   ```bash
   cd code
   ```

3. **Create and activate a virtual environment:**
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Set up environment variables (Optional):**
   Copy the example template inside the `code` directory:
   - **Windows:**
     ```powershell
     Copy-Item .env.example .env.local
     ```
   - **macOS / Linux:**
     ```bash
     cp .env.example .env.local
     ```
   Add your Finnhub API Key in `.env.local`:
   ```env
   MARKET_DATA_API_KEY=your_key_here
   ```
   *(If not provided, the application automatically uses simulated market updates).*

---

## 🎮 Running the Application

1. **(Optional) Fetch latest market data:**
   ```bash
   python collect_data.py
   ```

2. **Start the Flask server:**
   ```bash
   python app.py
   ```

3. **Open the interface:**
   Navigate in your browser to:
   ```text
   http://127.0.0.1:5000
   ```
   Or visit the live deployed version directly at [quantum-risk-analyzer.vercel.app](https://quantum-risk-analyzer.vercel.app/).

---

## 📡 API Reference

| Endpoint | Method | Purpose |
| :--- | :---: | :--- |
| `/` | `GET` | Serves the main single-page dashboard application. |
| `/api/funds` | `GET` | Returns available fund metadata and top underlying equity weights. |
| `/api/calculate_risk` | `POST` | Computes classical metrics, quantum VaR, QSVM classification, overlaps, and safety score. |
| `/api/stream_market` | `GET` | Server-Sent Events (SSE) live data stream with real-time quotes and intraday CaR. |
| `/api/refresh_data` | `POST` | Updates local historical price series from financial providers. |

---

## 🛠️ Tech Stack

- **Quantum Computing Simulation**: PennyLane (`default.qubit`)
- **Backend & Deployment**: Python, Flask, Gunicorn, Vercel
- **Quantitative Analytics**: NumPy, SciPy, Pandas, Scikit-Learn
- **Market Data**: yfinance, Finnhub REST & WebSocket APIs
- **User Interface**: HTML5, Vanilla JavaScript, Chart.js, Three.js, CSS Glassmorphism
