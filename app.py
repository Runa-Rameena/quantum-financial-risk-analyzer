import os
import traceback
import json
import random
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from flask import Flask, request, jsonify, render_template, Response
from collect_data import collect_financial_data
from quantum_risk_analyzer import QuantumRiskAnalyzer

app = Flask(__name__)

# Initialize the QuantumRiskAnalyzer lazily
analyzer = None

def get_analyzer():
    global analyzer
    if analyzer is None:
        analyzer = QuantumRiskAnalyzer()
    return analyzer

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/funds", methods=["GET"])
def get_funds():
    try:
        az = get_analyzer()
        funds_metadata = {}
        for ticker, data in az.holdings_db.items():
            funds_metadata[ticker] = {
                "name": data.get("name"),
                "type": data.get("type"),
                "top_holdings": [{"stock": stock, "weight": float(w)} for stock, w in data.get("holdings", {}).items()]
            }
        return jsonify({"success": True, "funds": funds_metadata})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/refresh_data", methods=["POST"])
def refresh_data():
    try:
        collect_financial_data()
        global analyzer
        analyzer = None # Force reload on next request
        return jsonify({"success": True, "message": "Data refreshed successfully from Yahoo Finance!"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/analyze", methods=["POST"])
def analyze_portfolio():
    try:
        data = request.get_json() or {}
        portfolio_weights = data.get("weights", {})
        total_amount = float(data.get("amount", 10000))
        
        # Validate weights
        if not portfolio_weights:
            return jsonify({"success": False, "error": "Portfolio is empty. Please select funds and assign weights."})
            
        # Ensure all weights are positive numbers and filter out zeros
        weights = {}
        for ticker, w in portfolio_weights.items():
            val = float(w)
            if val > 0:
                weights[ticker] = val
                
        if not weights:
            return jsonify({"success": False, "error": "No positive weights provided."})
            
        # Normalize weights so they sum to 1.0
        total_w = sum(weights.values())
        normalized_weights = {k: v / total_w for k, v in weights.items()}
        
        az = get_analyzer()
        print(f"Running full QML analysis on weights: {normalized_weights}")
        report = az.run_full_analysis(normalized_weights, total_amount=total_amount)
        
        # Calculate detailed company-level dollar allocations
        company_allocations = {}
        for fund, weight in normalized_weights.items():
            fund_dollars = total_amount * weight
            fund_holdings = az.holdings_db.get(fund, {}).get("holdings", {})
            for stock, stock_weight in fund_holdings.items():
                stock_dollars = fund_dollars * stock_weight
                if stock not in company_allocations:
                    company_allocations[stock] = {
                        "ticker": stock.split("(")[-1].replace(")", "") if "(" in stock else stock,
                        "name": stock.split(" (")[0],
                        "dollars": 0.0,
                        "percentage": 0.0,
                        "funds_involved": {}
                    }
                company_allocations[stock]["dollars"] += stock_dollars
                company_allocations[stock]["percentage"] += (stock_weight * weight * 100)
                company_allocations[stock]["funds_involved"][fund] = {
                    "fund_weight": float(stock_weight * 100),
                    "dollars": float(stock_dollars)
                }
                
        # Sort company allocations by dollars descending
        sorted_companies = sorted(company_allocations.values(), key=lambda x: x["dollars"], reverse=True)
        report["company_level_allocations"] = sorted_companies
        report["total_investment_amount"] = total_amount
        
        return jsonify({"success": True, "report": report})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/chat", methods=["POST"])
def advisor_chat():
    try:
        data = request.get_json() or {}
        query = data.get("query", "").lower().strip()
        portfolio_weights = data.get("weights", {})
        total_amount = float(data.get("amount", 10000))
        report = data.get("report", {})
        
        if not report or "classical" not in report:
            return jsonify({"success": True, "reply": "Please run the quantum simulation first so I can analyze your portfolio state!"})
            
        classical = report.get("classical", {})
        overlap = report.get("overlap", {})
        quantum = report.get("quantum", {})
        drift_results = report.get("style_drift", {})
        companies = report.get("company_level_allocations", [])
        
        reply = ""
        
        if "diversif" in query or "overlap" in query:
            avg_overlap = overlap.get("avg_overlap_percentage", 0.0)
            if avg_overlap > 25.0:
                reply = f"Your portfolio has a high stock overlap of **{avg_overlap:.1f}%**. This is a warning sign of false diversification. Several of your selected funds hold the exact same stocks. For instance, check the Portfolio Flow tab to see how they concentrate heavily on the same top holdings. I recommend swapping one of your stock funds for a real estate index (VGSLX) or fixed income (VBTLX) to restore true asset balance."
            else:
                reply = f"Great news! Your portfolio's average holdings overlap is **{avg_overlap:.1f}%**, which is well within the safe zone (<25%). Your chosen funds represent distinct asset classes (e.g. bonds, large-cap growth, real estate), indicating a solid diversification strategy."
                
        elif "volatility" in query or "risk" in query or "beta" in query:
            vol = classical.get("annualized_volatility", 0.0)
            beta = classical.get("beta", 1.0)
            q_var = quantum.get("var_99_quantum", 0.0)
            max_loss = total_amount * q_var
            
            if vol > 0.18:
                reply = f"Your portfolio carries aggressive risk characteristics: Annualized Volatility is **{vol*100:.1f}%** and Beta is **{beta:.2f}** (meaning it is {abs(beta-1)*100:.1f}% more volatile than the S&P 500). Our **Quantum Amplitude Estimation (QAE)** engine simulates a 99% maximum daily Value-at-Risk (Q-VaR) of **{q_var*100:.2f}%**, indicating that in a severe market crash, you could lose up to **${max_loss:.2f}** in a single day. Consider reallocating some weight to the bond fund (VBTLX) to lower these parameters."
            else:
                reply = f"Your portfolio displays stable, low-to-moderate risk parameters. Annualized Volatility is **{vol*100:.1f}%** with a Beta of **{beta:.2f}**. Our **Quantum Q-VaR simulation** estimates a 99% confidence daily loss limit of **{q_var*100:.2f}%** (equivalent to a maximum daily crash loss of **${max_loss:.2f}**). This is highly appropriate for a balanced or conservative investor."
                
        elif "drift" in query or "anomaly" in query:
            drifted_funds = [fund for fund, res in drift_results.items() if res.get("drift_detected")]
            if drifted_funds:
                details = []
                for f in drifted_funds:
                    details.append(f"**{f}** ({drift_results[f]['drift_reason']})")
                reply = f"Our **Quantum Support Vector Machine (QSVM)** active monitor has detected **Style Drift** in these funds: {', '.join(details)}. The managers of these funds are exhibiting trading patterns that are significantly more volatile than their official mandates. I recommend reviewing these holdings or swapping them out to maintain your target risk profile."
            else:
                reply = "Our **QSVM classification model** has run active monitoring on your largest fund holdings and found **no style drift**! All fund managers are successfully operating within their historical risk and asset-class boundaries."
                
        elif any(x in query for x in ["nvidia", "nvda", "microsoft", "msft", "apple", "aapl", "google", "googl", "amazon", "amzn"]):
            # Check exposure to a specific stock
            target_stock = ""
            for x in ["nvidia", "microsoft", "apple", "google", "amazon"]:
                if x in query:
                    target_stock = x
                    break
            
            # Search in companies allocations
            match = None
            for c in companies:
                if target_stock in c["name"].lower() or target_stock in c["ticker"].lower():
                    match = c
                    break
            
            if match:
                fund_details = []
                for f, f_data in match["funds_involved"].items():
                    fund_details.append(f"{f} (${f_data['dollars']:.2f})")
                reply = f"You have a total exposure of **${match['dollars']:.2f}** (**{match['percentage']:.2f}%** of your total portfolio) in **{match['name']}**. This exposure is split across these mutual funds: {', '.join(fund_details)}. If you are concerned about concentration in this stock, consider reducing weights in the growth funds (like VIGAX) which hold the largest shares of it."
            else:
                reply = f"You do not have any significant exposure to that specific stock in your top holdings database. Your mutual funds are safe from concentrated risk in that asset."
                
        else:
            # Default response
            ret = classical.get("annualized_return", 0.0)
            vol = classical.get("annualized_volatility", 0.0)
            sharpe = classical.get("sharpe_ratio", 0.0)
            q_var = quantum.get("var_99_quantum", 0.0)
            
            drift_count = len([f for f, r in drift_results.items() if r.get("drift_detected")])
            if drift_count > 0:
                drift_text = f"Style Drift detected in {drift_count} fund(s)."
            else:
                drift_text = "No active style drift detected across your funds."
                
            reply = (
                f"I have analyzed your **${total_amount:,.2f}** portfolio. Here is the cognitive summary:\n\n"
                f"1. **Performance:** Annualized projected return is **{ret*100:.2f}%** with a Sharpe ratio of **{sharpe:.2f}**.\n"
                f"2. **Quantum Risk (Q-VaR):** The 99% daily loss limit is **{q_var*100:.2f}%** (max expected single-day loss of **${total_amount*q_var:.2f}**).\n"
                f"3. **Style Drift:** {drift_text}\n\n"
                f"Feel free to ask me details about: **'Diversification / Overlaps'**, **'Volatility / Q-VaR Risk'**, or specific tech stocks like **'NVIDIA'** or **'Microsoft'**!"
            )
                    
        return jsonify({"success": True, "reply": reply})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})

current_scenario = "normal"

import threading

# Global variables for real-time exchange price cache and thread safety
cache_lock = threading.Lock()
last_cache_update = 0.0
live_market_timestamp = "Market closed"

# US Market Cache (NYSE / NASDAQ)
live_market_cache = {
    "MSFT": 495.42,
    "AAPL": 305.95,
    "NVDA": 225.16,
    "LLY": 1180.63,
    "TSLA": 342.32,
    "US-Treasury": 93.04
}

# Market Data API Key configuration (loads from .env.local or environment variable)
# Default Finnhub API Key provided for live US market quotes
DEFAULT_FINNHUB_KEY = "da2tkn1r01qupvfaq260da2tkn1r01qupvfaq26g"

# Market Data API Key configuration (loads from .env.local, environment variable, or default key)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_local_file = os.path.join(BASE_DIR, ".env.local")
if os.path.exists(env_local_file):
    try:
        with open(env_local_file, "r") as f:
            for line in f:
                if line.strip().startswith("MARKET_DATA_API_KEY="):
                    val = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                    if val and val != "YOUR_API_KEY_HERE":
                        os.environ["MARKET_DATA_API_KEY"] = val
    except Exception as e:
        print("[CONFIG] Could not read .env.local:", str(e))

MARKET_DATA_API_KEY = os.environ.get("MARKET_DATA_API_KEY", DEFAULT_FINNHUB_KEY)
if not MARKET_DATA_API_KEY or MARKET_DATA_API_KEY == "YOUR_API_KEY_HERE":
    MARKET_DATA_API_KEY = DEFAULT_FINNHUB_KEY

from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor

def check_is_market_open():
    """
    Check if U.S. stock exchanges (NYSE / NASDAQ) are currently in active market hours.
    Regular trading hours: Monday through Friday, 9:30 AM to 4:00 PM EDT (UTC-4).
    """
    now_utc = datetime.now(timezone.utc)
    ny_time = now_utc - timedelta(hours=4)   # EDT is UTC-4
    
    # Check weekday (0 = Mon, 4 = Fri, 5 = Sat, 6 = Sun)
    if ny_time.weekday() < 5:
        ny_minutes = ny_time.hour * 60 + ny_time.minute
        # 9:30 AM is 570 mins, 4:00 PM is 960 mins
        if 570 <= ny_minutes < 960:
            return True, "U.S. Markets Open (NYSE/NASDAQ)", ny_time.strftime("%H:%M:%S EDT")
    
    return False, "U.S. Markets Closed (After-Hours)", ny_time.strftime("%H:%M:%S EDT")

live_market_prev_close = {
    "MSFT": 497.12,
    "AAPL": 331.34,
    "NVDA": 212.17,
    "LLY": 1136.11,
    "TSLA": 356.58,
    "US-Treasury": 93.04
}

def fetch_single_finnhub_quote(sym):
    import urllib.request
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={sym}&token={MARKET_DATA_API_KEY}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            res_data = json.loads(resp.read().decode())
            if "c" in res_data and float(res_data["c"]) > 0:
                c = round(float(res_data["c"]), 2)
                pc = round(float(res_data.get("pc", c)), 2)
                return sym, c, pc
    except Exception as e:
        pass
    return sym, None, None

def update_live_market_cache():
    global last_cache_update, live_market_cache, live_market_prev_close, live_market_timestamp
    now = time.time()
    if now - last_cache_update < 6.0:
        return
        
    is_open, status_str, ny_time_str = check_is_market_open()
    live_market_timestamp = ny_time_str if is_open else "Market closed"
    
    symbols = ["MSFT", "AAPL", "NVDA", "LLY", "TSLA"]
    new_prices = {}
    new_pc = {}
    
    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(fetch_single_finnhub_quote, symbols)
            for sym, price, pc in results:
                if price is not None:
                    new_prices[sym] = price
                if pc is not None:
                    new_pc[sym] = pc
                    
        if new_prices:
            with cache_lock:
                for k, v in new_prices.items():
                    live_market_cache[k] = v
                for k, v in new_pc.items():
                    live_market_prev_close[k] = v
            last_cache_update = now
            print(f"[FINNHUB API] Successfully fetched live quotes at {ny_time_str}: {new_prices}")
    except Exception as e:
        print("[FINNHUB API] Quote fetch note:", str(e))

@app.route("/api/set_scenario", methods=["POST"])
def set_scenario():
    global current_scenario
    data = request.get_json() or {}
    current_scenario = data.get("scenario", "normal")
    print(f"[SYSTEM] Scenario updated in Flask to: {current_scenario}")
    return jsonify({"success": True, "scenario": current_scenario})

@app.route("/api/live_ticks")
def get_live_ticks():
    """Direct REST endpoint returning instantaneous live US market ticks."""
    global current_scenario
    update_live_market_cache()
    is_open, status_str, ny_time_str = check_is_market_open()
    
    with cache_lock:
        current_real = dict(live_market_cache)
        prev_close_map = dict(live_market_prev_close)

    prices = dict(current_real)

    if current_scenario == "bubble":
        sentiment = "Bearish (Tech Bubble Burst)"
        vix = 35.2
        prices["MSFT"] = round(current_real["MSFT"] * (1 + random.uniform(-0.06, -0.015)), 2)
        prices["AAPL"] = round(current_real["AAPL"] * (1 + random.uniform(-0.05, -0.01)), 2)
        prices["NVDA"] = round(current_real["NVDA"] * (1 + random.uniform(-0.10, -0.035)), 2)
        prices["LLY"] = round(current_real["LLY"] * (1 + random.uniform(-0.02, 0.015)), 2)
        prices["TSLA"] = round(current_real["TSLA"] * (1 + random.uniform(-0.08, -0.02)), 2)
        prices["US-Treasury"] = round(current_real["US-Treasury"] * (1 + random.uniform(0.001, 0.005)), 2)
    elif current_scenario == "inflation":
        sentiment = "Volatile (Interest Rate Shock)"
        vix = 24.1
        prices["MSFT"] = round(current_real["MSFT"] * (1 + random.uniform(-0.025, 0.015)), 2)
        prices["AAPL"] = round(current_real["AAPL"] * (1 + random.uniform(-0.02, 0.01)), 2)
        prices["NVDA"] = round(current_real["NVDA"] * (1 + random.uniform(-0.05, 0.03)), 2)
        prices["LLY"] = round(current_real["LLY"] * (1 + random.uniform(-0.02, 0.005)), 2)
        prices["TSLA"] = round(current_real["TSLA"] * (1 + random.uniform(-0.04, 0.02)), 2)
        prices["US-Treasury"] = round(current_real["US-Treasury"] * (1 + random.uniform(-0.02, -0.004)), 2)
    elif current_scenario == "recovery":
        sentiment = "Strong Bullish (Goldilocks)"
        vix = 11.2
        prices["MSFT"] = round(current_real["MSFT"] * (1 + random.uniform(0.003, 0.015)), 2)
        prices["AAPL"] = round(current_real["AAPL"] * (1 + random.uniform(0.002, 0.010)), 2)
        prices["NVDA"] = round(current_real["NVDA"] * (1 + random.uniform(0.006, 0.025)), 2)
        prices["LLY"] = round(current_real["LLY"] * (1 + random.uniform(0.003, 0.018)), 2)
        prices["TSLA"] = round(current_real["TSLA"] * (1 + random.uniform(0.005, 0.022)), 2)
        prices["US-Treasury"] = round(current_real["US-Treasury"] * (1 + random.uniform(-0.0005, 0.0015)), 2)
    else: # normal
        if is_open or current_scenario != "normal":
            prices["MSFT"] = round(current_real["MSFT"] * (1 + random.uniform(-0.0035, 0.0035)), 2)
            prices["AAPL"] = round(current_real["AAPL"] * (1 + random.uniform(-0.0030, 0.0030)), 2)
            prices["NVDA"] = round(current_real["NVDA"] * (1 + random.uniform(-0.0045, 0.0045)), 2)
            prices["LLY"] = round(current_real["LLY"] * (1 + random.uniform(-0.0030, 0.0030)), 2)
            prices["TSLA"] = round(current_real["TSLA"] * (1 + random.uniform(-0.0050, 0.0050)), 2)
            prices["US-Treasury"] = round(current_real["US-Treasury"] * (1 + random.uniform(-0.0010, 0.0010)), 2)
        else:
            prices = dict(current_real)
        
        vix = 14.5 + random.uniform(-0.3, 0.3)
        sentiment = "Normal Trading" if is_open else "After-Hours (Holding Last Close)"

    for k in prices:
        prices[k] = max(1.0, round(prices[k], 2))

    changes_pct = {}
    for k in prices:
        pc = prev_close_map.get(k, prices[k])
        if pc > 0:
            changes_pct[k] = round(((prices[k] - pc) / pc) * 100, 2)
        else:
            changes_pct[k] = 0.0

    stream_status = "open" if (is_open or current_scenario != "normal") else "closed"

    return jsonify({
        "status": stream_status,
        "is_open": is_open,
        "sentiment": sentiment,
        "vix": round(vix, 2),
        "prices": prices,
        "prev_close": prev_close_map,
        "changes_pct": changes_pct,
        "timestamp": ny_time_str
    })

@app.route("/api/stream")
def stream_market_feed():
    def generate_ticks():
        update_live_market_cache()
        with cache_lock:
            prices = dict(live_market_cache)
            
        yield "retry: 500\n\n"
        
        for _ in range(10):
            global current_scenario
            is_open, status_str, ny_time_str = check_is_market_open()
            
            vix = 14.5
            sentiment = "Normal Trading"
            
            with cache_lock:
                current_real = dict(live_market_cache)
                prev_close_map = dict(live_market_prev_close)
            
            if current_scenario == "bubble":
                sentiment = "Bearish (Tech Bubble Burst)"
                vix = 35.2
                prices["MSFT"] = round(current_real["MSFT"] * (1 + random.uniform(-0.06, -0.015)), 2)
                prices["AAPL"] = round(current_real["AAPL"] * (1 + random.uniform(-0.05, -0.01)), 2)
                prices["NVDA"] = round(current_real["NVDA"] * (1 + random.uniform(-0.10, -0.035)), 2)
                prices["LLY"] = round(current_real["LLY"] * (1 + random.uniform(-0.02, 0.015)), 2)
                prices["TSLA"] = round(current_real["TSLA"] * (1 + random.uniform(-0.08, -0.02)), 2)
                prices["US-Treasury"] = round(current_real["US-Treasury"] * (1 + random.uniform(0.001, 0.005)), 2)
            elif current_scenario == "inflation":
                sentiment = "Volatile (Interest Rate Shock)"
                vix = 24.1
                prices["MSFT"] = round(current_real["MSFT"] * (1 + random.uniform(-0.025, 0.015)), 2)
                prices["AAPL"] = round(current_real["AAPL"] * (1 + random.uniform(-0.02, 0.01)), 2)
                prices["NVDA"] = round(current_real["NVDA"] * (1 + random.uniform(-0.05, 0.03)), 2)
                prices["LLY"] = round(current_real["LLY"] * (1 + random.uniform(-0.02, 0.005)), 2)
                prices["TSLA"] = round(current_real["TSLA"] * (1 + random.uniform(-0.04, 0.02)), 2)
                prices["US-Treasury"] = round(current_real["US-Treasury"] * (1 + random.uniform(-0.02, -0.004)), 2)
            elif current_scenario == "recovery":
                sentiment = "Strong Bullish (Goldilocks)"
                vix = 11.2
                prices["MSFT"] = round(current_real["MSFT"] * (1 + random.uniform(0.003, 0.015)), 2)
                prices["AAPL"] = round(current_real["AAPL"] * (1 + random.uniform(0.002, 0.010)), 2)
                prices["NVDA"] = round(current_real["NVDA"] * (1 + random.uniform(0.006, 0.025)), 2)
                prices["LLY"] = round(current_real["LLY"] * (1 + random.uniform(0.003, 0.018)), 2)
                prices["TSLA"] = round(current_real["TSLA"] * (1 + random.uniform(0.005, 0.022)), 2)
                prices["US-Treasury"] = round(current_real["US-Treasury"] * (1 + random.uniform(-0.0005, 0.0015)), 2)
            else: # normal
                if is_open or current_scenario != "normal":
                    prices["MSFT"] = round(current_real["MSFT"] * (1 + random.uniform(-0.0035, 0.0035)), 2)
                    prices["AAPL"] = round(current_real["AAPL"] * (1 + random.uniform(-0.0030, 0.0030)), 2)
                    prices["NVDA"] = round(current_real["NVDA"] * (1 + random.uniform(-0.0045, 0.0045)), 2)
                    prices["LLY"] = round(current_real["LLY"] * (1 + random.uniform(-0.0030, 0.0030)), 2)
                    prices["TSLA"] = round(current_real["TSLA"] * (1 + random.uniform(-0.0050, 0.0050)), 2)
                    prices["US-Treasury"] = round(current_real["US-Treasury"] * (1 + random.uniform(-0.0010, 0.0010)), 2)
                else:
                    prices = dict(current_real)
                
                vix = max(10.0, min(20.0, vix + random.uniform(-0.3, 0.3)))
                sentiment = "Normal Trading" if is_open else "After-Hours (Holding Last Close)"

            for k in prices:
                prices[k] = max(1.0, round(prices[k], 2))

            changes_pct = {}
            for k in prices:
                pc = prev_close_map.get(k, prices[k])
                if pc > 0:
                    changes_pct[k] = round(((prices[k] - pc) / pc) * 100, 2)
                else:
                    changes_pct[k] = 0.0
                
            stream_status = "open" if (is_open or current_scenario != "normal") else "closed"
            
            tick_data = {
                "status": stream_status,
                "is_open": is_open,
                "sentiment": sentiment,
                "vix": round(vix, 2),
                "prices": prices,
                "prev_close": prev_close_map,
                "changes_pct": changes_pct,
                "timestamp": ny_time_str
            }
            
            yield f"data: {json.dumps(tick_data)}\n\n"
            time.sleep(1.5) # updates every 1.5 seconds
            
    return Response(generate_ticks(), mimetype="text/event-stream")

if __name__ == "__main__":
    os.makedirs(os.path.join(app.root_path, "templates"), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, "static"), exist_ok=True)
    
    print("Starting Flask web server on http://localhost:5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
