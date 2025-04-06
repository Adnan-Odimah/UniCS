import json
import re
import math
import datetime
import requests
import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime
from scipy.optimize import minimize

# Server and API credentials (DO NOT share sensitive info)
URL = "mts-prism.com"
PORT = 8082
TEAM_API_CODE = "039acbf2cceb770afa2b59b4cb856a80"

def send_get_request(path):
    headers = {"X-API-Code": TEAM_API_CODE}
    response = requests.get(f"http://{URL}:{PORT}/{path}", headers=headers)
    if response.status_code != 200:
        return False, f"Error - something went wrong when requesting [CODE: {response.status_code}]: {response.text}"
    return True, response.text

def send_post_request(path, data=None):
    headers = {"X-API-Code": TEAM_API_CODE, "Content-Type": "application/json"}
    data = json.dumps(data)
    response = requests.post(f"http://{URL}:{PORT}{path}", data=data, headers=headers)
    if response.status_code != 200:
        return False, f"Error - something went wrong when requesting [CODE: {response.status_code}]: {response.text}"
    return True, response.text

def get_context():
    """Retrieve investor context details."""
    return send_get_request("/request")

def get_my_current_information():
    """Retrieve your team's current points and profits."""
    return send_get_request("/info")

def send_portfolio(weighted_stocks):
    """
    Submit the portfolio.
    Format: [{"ticker": "AAPL", "quantity": 1}, ...]
    """
    #data = [{"ticker": ticker, "quantity": quantity} for ticker, quantity in weighted_stocks]
    #temp_data = [{"ticker": "AAPL", "quantity": 1}, {"ticker": "MSFT", "quantity": 10}]
    #print("tempdata", temp_data)
    return send_post_request("/submit", data=weighted_stocks)


def get_candidate_universe():
    """
    Returns a list of candidate US equities with their ticker, industry, and volatility.
    Only US equities are included.
    """
    return [
        {"ticker": "AAPL", "industry": "Technology", "volatility": 0.2},
        {"ticker": "MSFT", "industry": "Technology", "volatility": 0.18},
        {"ticker": "GOOGL", "industry": "Technology", "volatility": 0.25},
        {"ticker": "TSLA", "industry": "Automotive", "volatility": 0.35},
        {"ticker": "WMT", "industry": "Retail", "volatility": 0.15},
        {"ticker": "JPM", "industry": "Financial Services", "volatility": 0.22},
        {"ticker": "V", "industry": "Financial Services", "volatility": 0.19},
        {"ticker": "NFLX", "industry": "Entertainment", "volatility": 0.3},
        {"ticker": "CVS", "industry": "Healthcare", "volatility": 0.17},
    ]

def compute_volatility_threshold(investment_period, age, employed, salary):
    """
    Compute the maximum acceptable volatility for candidate stocks based on:
    - Investment period (in days)
    - Age of the investor
    - Employment status
    - Salary level
    """
    # For a young, employed investor with a high salary and a long investment period,
    # allow higher risk.
    if age < 30 and employed and salary > 50000 and investment_period >= 365:
        return 0.35
    # For young investors without all these advantages, moderate risk is allowed.
    elif age < 30:
        return 0.3
    # Middle-aged investors get a moderate-to-conservative threshold.
    elif age < 50:
        return 0.25
    # Older investors require the lowest risk.
    else:
        return 0.2

def advanced_allocate_portfolio(budget, candidate_tickers, risk_profile):
    """
    Given a list of candidate tickers and a budget, this function fetches the previous closing
    price and one year of historical daily prices for each candidate.
    
    For low-risk profiles, it uses a minimum-variance optimization (via SLSQP) on daily returns
    to compute optimal weights. For moderate risk, equal weighting is used.
    
    The budget is then allocated according to these weights, converting dollar allocations to whole shares.
    Returns a list of dictionaries with keys "ticker" and "quantity".
    """
    prices = {}
    returns_list = []
    tickers_for_opt = []
    
    # Retrieve price and historical data for each candidate.
    for ticker in candidate_tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get("previousClose")
            if price is None:
                print(f"Warning: Could not retrieve previous closing price for {ticker}. Skipping.")
                continue
            prices[ticker] = price
            
            # Get one year of historical daily data.
            hist = stock.history(period="1y")
            if hist.empty:
                print(f"Warning: No historical data for {ticker}. Skipping.")
                continue
            daily_returns = hist['Close'].pct_change().dropna()
            returns_list.append(daily_returns)
            tickers_for_opt.append(ticker)
        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")
    
    if not tickers_for_opt:
        raise ValueError("No candidate stock data could be retrieved.")
    
    # Align returns data and compute the covariance matrix.
    returns_df = pd.concat(returns_list, axis=1, join='inner')
    returns_df.columns = tickers_for_opt
    cov_matrix = returns_df.cov().values

    n = len(tickers_for_opt)
    if risk_profile == "low":
        # Optimize for minimum variance.
        def objective(w):
            return np.dot(w, np.dot(cov_matrix, w))
        cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})
        bounds = [(0, 1) for _ in range(n)]
        w0 = np.array([1/n] * n)
        result = minimize(objective, w0, method='SLSQP', bounds=bounds, constraints=cons)
        if result.success:
            weights = result.x
        else:
            print("Optimization failed; falling back to equal weighting.")
            weights = w0
    else:
        # For moderate risk, use equal weights.
        weights = np.array([1/n] * n)
    
    print("Optimized Weights:", {ticker: round(weight, 4) for ticker, weight in zip(tickers_for_opt, weights)})

    # Allocate the budget based on these weights.
    portfolio = []
    total_spent = 0
    for ticker, weight in zip(tickers_for_opt, weights):
        allocated = weight * budget
        price = prices[ticker]
        quantity = math.floor(allocated / price)
        cost = quantity * price
        total_spent += cost
        if quantity > 0:
            portfolio.append({"ticker": ticker, "quantity": quantity})
        else:
            print(f"Not enough allocated budget for {ticker} to buy a single share.")
    
    print(f"Total spent: ${round(total_spent, 2)} out of ${budget}")
    return portfolio

def build_portfolio(context):
    """
    Integrate advanced risk profiling with thematic screening.
    
    Steps:
      - Extract parameters from the context JSON message (budget, age, investment period, employed, salary, dislikes).
      - Use 2/3 of the budget for stock purchases.
      - Retrieve the candidate universe.
      - Compute a volatility threshold based on investment period, age, employment, and salary.
      - Filter out candidate stocks whose industry is in the investor's dislikes or whose volatility exceeds the threshold.
      - Determine risk profile: "low" if the investment period is short or investor is older; otherwise "moderate".
      - Use advanced allocation (optimization for low risk, equal weighting for moderate) to allocate the available budget.
      - Return the final portfolio as a list of dictionaries with keys "ticker" and "quantity".
    """
    # Parse the context. Expect the context message to be a JSON string with keys:
    # "budget", "age", "start", "end", "employed", "salary", "dislikes"
    context_dict = json.loads(context)
    message = context_dict.get("message", "{}")
    print("Investor context:", message)
    
    msg = json.loads(message)
    budget = msg.get("budget")
    age = msg.get("age")
    start_date = datetime.strptime(msg.get("start"), "%Y-%m-%d")
    end_date = datetime.strptime(msg.get("end"), "%Y-%m-%d")
    employed = msg.get("employed")
    salary = msg.get("salary")
    dislikes = msg.get("dislikes", [])
    
    if budget is None or age is None:
        raise ValueError("Could not extract budget or age from context message.")
    
    # Calculate investment period (in days) and determine available budget (2/3 of total).
    investment_period = (end_date - start_date).days
    print(f"Calculated investment period: {investment_period} days")
    available_budget = budget * 2/3
    print(f"Available budget for stocks: {available_budget}")
    
    # Retrieve candidate universe.
    candidates = get_candidate_universe()
    
    # Compute the volatility threshold.
    volatility_threshold = compute_volatility_threshold(investment_period, age, employed, salary)
    print(f"Using volatility threshold: {volatility_threshold}")
    
    # Filter candidates: remove those in industries the investor dislikes and with volatility above threshold.
    filtered_candidates = []
    for stock in candidates:
        if stock["industry"].lower() in [d.lower() for d in dislikes]:
            continue
        if stock["volatility"] <= volatility_threshold:
            filtered_candidates.append(stock)
    # Fallback: if filtering removes all candidates, relax volatility.
    if not filtered_candidates:
        for stock in candidates:
            if stock["industry"].lower() not in [d.lower() for d in dislikes]:
                filtered_candidates.append(stock)
    
    print("Filtered candidate stocks:", filtered_candidates)
    
    ticker_list = [stock["ticker"] for stock in filtered_candidates]
    
    # Determine risk profile: low risk if investment period is short (< 365 days) or investor is older (>= 65).
    risk_profile = "low" if (investment_period < 365 or age >= 65) else "moderate"
    print(f"Determined risk profile: {risk_profile}")
    
    # Allocate the available budget among the filtered candidate stocks using advanced allocation.
    portfolio = advanced_allocate_portfolio(available_budget, ticker_list, risk_profile)
    return portfolio




def main():
    # Retrieve and print team information
    success, info = get_my_current_information()
    if not success:
        print(f"Error: {info}")
        return
    print("Team Information:", info)

    # Get investor context details
    success, context = get_context()
    if not success:
        print(f"Error: {context}")
        return
    print("Context Provided:", context)

    # Build a portfolio based on the investor context
    try:
        portfolio = build_portfolio(context)
    except Exception as e:
        print("Error building portfolio:", e)
        return
    print("Constructed Portfolio:", portfolio)

    # Submit the portfolio and print the evaluation response
    success, response = send_portfolio(portfolio)
    if not success:
        print(f"Error: {response}")
    else:
        print("Evaluation Response:", response)

if __name__ == "__main__":
    main()
