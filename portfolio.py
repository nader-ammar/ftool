import requests
import pandas as pd
import matplotlib.pyplot as plt
from Api_key3 import Api_Key3  # API key for authentication
class Portfolio:
    def __init__(self):
        self.api_key = Api_Key3
        self.stocks = {}
    def stock_add(self, ticker_symbol, shares):
        ticker_symbol = ticker_symbol.upper()
        self.stocks[ticker_symbol] = {
            "Shares": shares,
            "Current Price": "N/A",
            "Dividends": [],
            "Company Name": "N/A"
        }
    def stock_info(self, ticker_symbol):
        ticker_symbol = ticker_symbol.upper()
        # Get company details
        url = (
            "https://api.polygon.io/v3/reference/tickers/" + ticker_symbol
            + "?apiKey=" + self.api_key
        )
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            details = data.get("results", {})
            self.stocks[ticker_symbol]["Company Name"] = details.get("name", "N/A")
        else:
            print(f"Error getting company information for {ticker_symbol}")
        # Get latest stock price
        url_price = (
            "https://api.polygon.io/v2/aggs/ticker/" + ticker_symbol
            + "/prev?adjusted=true&apiKey=" + self.api_key
        )
        response = requests.get(url_price)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [{}])[0]
            self.stocks[ticker_symbol]["Current Price"] = results.get("c", "N/A")
        else:
            print(f"Error getting price for {ticker_symbol}")
    def dividend_data(self, ticker_symbol):
        ticker_symbol = ticker_symbol.upper()
        # Get dividend data for the specific ticker
        url_dividends = (
            "https://api.polygon.io/v3/reference/dividends?ticker=" + ticker_symbol
            + "&limit=10&apiKey=" + self.api_key
        )
        response = requests.get(url_dividends)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            # Extract and store relevant dividend details
            dividends = []
            for div in results:
                dividends.append({
                    "cash_amount": div.get("cash_amount", 0),
                    "currency": div.get("currency", "N/A"),
                    "declaration_date": div.get("declaration_date", "N/A"),
                    "ex_dividend_date": div.get("ex_dividend_date", "N/A"),
                    "pay_date": div.get("pay_date", "N/A"),
                    "record_date": div.get("record_date", "N/A"),
                    "dividend_type": div.get("dividend_type", "N/A"),
                    "frequency": div.get("frequency", "N/A")
                })
            self.stocks[ticker_symbol]["Dividends"] = dividends
        else:
            print(f"Error getting dividend information for {ticker_symbol}: {response.status_code}")
    def calc_market_value(self):
        total_value = sum(
            stock["Shares"] * (stock["Current Price"] if stock["Current Price"] != "N/A" else 0)
            for stock in self.stocks.values()
        )
        return total_value
    def calc_dividend_income(self):
        total_income = 0
        for stock in self.stocks.values():
            for dividend in stock["Dividends"]:
                total_income += dividend.get("cash_amount", 0) * stock["Shares"]
        return total_income
    def portfolio_visualization(self):
        tickers = list(self.stocks.keys())
        values = [
            stock["Shares"] * (stock["Current Price"] if stock["Current Price"] != "N/A" else 0)
            for stock in self.stocks.values()
        ]
        if not any(values):
            print("No valid market values to display.")
            return
        plt.figure(figsize=(10, 8))
        plt.pie(values, labels=tickers, autopct="%1.1f%%", startangle=140)
        plt.title("Portfolio Market Value Distribution")
        plt.show()
    def portfolio_display(self):
        portfolio_data = []
        for ticker, stock in self.stocks.items():
            market_value = stock["Shares"] * (stock["Current Price"] if stock["Current Price"] != "N/A" else 0)
            portfolio_data.append({
                "Ticker": ticker,
                "Company Name": stock["Company Name"],
                "Shares": stock["Shares"],
                "Current Price": stock["Current Price"],
                "Market Value": market_value
            })
        df = pd.DataFrame(portfolio_data)
        print(df)
        print(f"\nTotal Market Value: ${self.calc_market_value():,.2f}")
        print(f"Total Dividend Income: ${self.calc_dividend_income():,.2f}")