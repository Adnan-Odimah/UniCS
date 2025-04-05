import json
import re
import math
import requests
import yfinance as yf

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
    data = [{"ticker": ticker, "quantity": quantity} for ticker, quantity in weighted_stocks]
    return send_post_request("/submit", data=data)

def extract_budget(message):
    """
    Extracts the budget from the investor context message.
    Looks for a pattern like '$204' and returns the numeric value.
    """
    match = re.search(r'\$\s*(\d+)', message)
    if match:
        return int(match.group(1))
    else:
        # Default fallback if budget is not found
        return None

def build_portfolio(context):
    """
    Build a portfolio based on investor context.
    This function extracts the budget from the context message and then uses Yahoo Finance
    to get current stock prices for candidate stocks. It then allocates the budget equally
    across the stocks, buying as many shares as possible for each without exceeding the allocation.
    """
    # Parse the JSON context and extract the message
    context_dict = json.loads(context)
    message = context_dict.get("message", "")
    print("Investor context:", message)
    
    budget = extract_budget(message)
    budget/=2
    if budget is None:
        raise ValueError("Could not extract budget from context message.")
    print("Extracted budget:", budget)
    
    # Define a candidate list of low-priced US stocks (has to be exclusivley US)
    # For example, these tickers are known to often trade at lower prices.
    candidate_stocks = ["GE", "F", "SIRI", "HPQ"]
    
    # Use yfinance to retrieve the current market price for each candidate stock.
    prices = {}
    for ticker in candidate_stocks:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get("regularMarketPrice")
            if price is None:
                print(f"Warning: Could not retrieve price for {ticker}. Skipping.")
            else:
                prices[ticker] = price
        except Exception as e:
            print(f"Error retrieving data for {ticker}: {e}")
    
    if not prices:
        raise ValueError("No candidate stock prices could be retrieved.")
    
    print("Retrieved stock prices:")
    for ticker, price in prices.items():
        print(f"  {ticker}: ${price}")
    
    # Allocate the budget equally across the stocks for simplicity.
    n = len(prices)
    allocation_per_stock = budget / n
    spent = 0
    portfolio = []
    for ticker, price in prices.items():
        # Calculate maximum shares without exceeding the per-stock allocation
        max_quantity = math.floor(allocation_per_stock / price)
        # Also ensure that buying these shares does not exceed the overall budget.
        if max_quantity > 0:
            cost = max_quantity * price
            if spent + cost > budget:
                # Adjust the quantity so total spent remains within the budget.
                max_quantity = math.floor((budget - spent) / price)
                cost = max_quantity * price
            if max_quantity > 0:
                portfolio.append((ticker, max_quantity))
                spent += cost
                print(f"Allocating {max_quantity} shares of {ticker} at ${price} each for a cost of ${cost}.")
            else:
                print(f"Not enough remaining budget to buy a share of {ticker}.")
        else:
            print(f"Not enough allocated budget for {ticker} to buy a single share.")
    
    print(f"Total spent: ${spent} out of ${budget}")
    
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
