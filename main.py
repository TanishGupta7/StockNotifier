import datetime
import time
from plyer import notification
import yfinance as yf
import logging

# Setup logging
logging.basicConfig(filename='stock_notifier.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Predefined mapping for company names to tickers
company_to_ticker = {
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Meta (Facebook)": "META",
    "NVIDIA": "NVDA",
    "Netflix": "NFLX",
    "Adobe": "ADBE",
    "Intel": "INTC",
    "IBM": "IBM",
    "Samsung": "005930.KS",
    "Oracle": "ORCL",
    "PayPal": "PYPL",
    "Uber": "UBER",
    "Zoom": "ZM",
    "Walmart": "WMT",
    "Procter & Gamble": "PG",
    "Coca-Cola": "KO",
    "PepsiCo": "PEP",
    "Johnson & Johnson": "JNJ",
    "Pfizer": "PFE",
    "Disney": "DIS",
    "Boeing": "BA",
    "Ford": "F",
    "General Motors": "GM"
}


def get_ticker_from_company():
    """Fetch ticker based on user-provided company name."""
    print("Available Companies: ", ", ".join(company_to_ticker.keys()))
    while True:
        company = input("Enter the company name: ").strip().capitalize()
        if company in company_to_ticker:
            return company_to_ticker[company]
        else:
            print("Invalid company name. Please choose from the available list.")

def get_valid_interval():
    """Get a valid interval (in seconds) from the user."""
    while True:
        try:
            interval = int(input("Enter the interval (in seconds) for stock notifications: "))
            if interval > 0:
                return interval
            print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def get_alert_thresholds():
    """Allow users to set thresholds for stock price alerts."""
    while True:
        try:
            lower_threshold = float(input("Enter the lower price threshold (or 0 to disable): "))
            upper_threshold = float(input("Enter the upper price threshold (or 0 to disable): "))
            return lower_threshold, upper_threshold
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

def fetch_stock_data(ticker):
    """Fetch stock data dynamically using Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        fast_info = stock.fast_info
        return {
            "currentPrice": fast_info["last_price"],
            "dayLow": fast_info["day_low"],
            "dayHigh": fast_info["day_high"]
        }
    except Exception as e:
        logging.error(f"Error fetching stock data for {ticker}: {e}")
        return None

def notify_user(ticker, data):
    """Send desktop notification with stock data."""
    try:
        today = datetime.date.today()
        notification.notify(
            title=f"{ticker} Stock Data ({today})",
            message=f"Current Price = ${data['currentPrice']}\nDay Low = ${data['dayLow']}\nDay High = ${data['dayHigh']}",
            app_icon="Notification_icon.ico",  # Optional: Add a valid icon file path
            timeout=10
        )
        print(f"Notification sent for {ticker}!")
    except Exception as e:
        logging.error(f"Error sending notification: {e}")

def log_stock_data(ticker, data):
    """Log stock data to a file."""
    logging.info(f"{ticker} | Current Price: ${data['currentPrice']} | Day Low: ${data['dayLow']} | Day High: ${data['dayHigh']}")

def main():
    print("Welcome to the Stock Price Notifier!")
    
    # Get the ticker symbol
    ticker = get_ticker_from_company()
    
    # Get notification interval
    interval = get_valid_interval()
    
    # Get alert thresholds
    lower_threshold, upper_threshold = get_alert_thresholds()
    
    print(f"Monitoring {ticker} every {interval} seconds...")
    print(f"Alerts set for price below ${lower_threshold} and above ${upper_threshold}.")
    
    # Main loop to fetch and notify stock data
    while True:
        stock_data = fetch_stock_data(ticker)
        if stock_data:
            current_price = stock_data['currentPrice']
            
            # Check thresholds
            if (lower_threshold > 0 and current_price < lower_threshold) or (upper_threshold > 0 and current_price > upper_threshold):
                notify_user(ticker, stock_data)
                log_stock_data(ticker, stock_data)
            else:
                print(f"Price is within thresholds: ${current_price}")
        else:
            print("Failed to fetch stock data. Retrying...")
        
        time.sleep(interval)

if __name__ == "__main__":
    main()
