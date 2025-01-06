import datetime
import time
from plyer import notification
import yfinance as yf
import logging
import smtplib
from tkinter import Tk, Label, Button, Entry, StringVar, Listbox, END

# Setup logging
logging.basicConfig(filename='stock_notifier.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Email credentials (Configure with your credentials)
EMAIL = "your_email@example.com"
PASSWORD = "your_password"

def fetch_ticker(company_name):
    """Fetch the ticker symbol for a company using Yahoo Finance."""
    try:
        stock = yf.Ticker(company_name)
        info = stock.info
        return info.get('symbol', None)
    except Exception as e:
        logging.error(f"Error fetching ticker for {company_name}: {e}")
        return None

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

def send_email_notification(email, subject, message):
    """Send an email notification."""
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            email_message = f"Subject: {subject}\n\n{message}"
            server.sendmail(EMAIL, email, email_message)
        logging.info(f"Email sent to {email}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def notify_user(ticker, data):
    """Send desktop notification with stock data."""
    try:
        today = datetime.date.today()
        notification.notify(
            title=f"{ticker} Stock Data ({today})",
            message=f"Current Price = ${data['currentPrice']}\nDay Low = ${data['dayLow']}\nDay High = ${data['dayHigh']}",
            app_icon="Notification_icon.ico",
            timeout=10
        )
        print(f"Notification sent for {ticker}!")
    except Exception as e:
        logging.error(f"Error sending notification: {e}")

def log_stock_data(ticker, data):
    """Log stock data to a file."""
    logging.info(f"{ticker} | Current Price: ${data['currentPrice']} | Day Low: ${data['dayLow']} | Day High: ${data['dayHigh']}")

class StockNotifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Price Notifier")
        
        # Variables
        self.company_var = StringVar()
        self.interval_var = StringVar()
        self.email_var = StringVar()
        self.stocks_list = []
        
        # UI Elements
        Label(root, text="Enter Company Name:").grid(row=0, column=0, padx=10, pady=5)
        Entry(root, textvariable=self.company_var).grid(row=0, column=1, padx=10, pady=5)
        
        Label(root, text="Notification Interval (seconds):").grid(row=1, column=0, padx=10, pady=5)
        Entry(root, textvariable=self.interval_var).grid(row=1, column=1, padx=10, pady=5)
        
        Label(root, text="Email for Alerts (optional):").grid(row=2, column=0, padx=10, pady=5)
        Entry(root, textvariable=self.email_var).grid(row=2, column=1, padx=10, pady=5)
        
        Button(root, text="Add Stock", command=self.add_stock).grid(row=3, column=0, padx=10, pady=5)
        Button(root, text="Start Monitoring", command=self.start_monitoring).grid(row=3, column=1, padx=10, pady=5)
        
        Label(root, text="Stocks to Monitor:").grid(row=4, column=0, padx=10, pady=5)
        self.stock_listbox = Listbox(root)
        self.stock_listbox.grid(row=4, column=1, padx=10, pady=5)

    def add_stock(self):
        company_name = self.company_var.get().strip()
        ticker = fetch_ticker(company_name)
        if ticker:
            self.stocks_list.append(ticker)
            self.stock_listbox.insert(END, f"{company_name} ({ticker})")
            logging.info(f"Added stock {company_name} ({ticker}) for monitoring.")
        else:
            print("Invalid company name. Could not fetch ticker.")

    def start_monitoring(self):
        try:
            interval = int(self.interval_var.get())
            email = self.email_var.get().strip()
            
            while True:
                for ticker in self.stocks_list:
                    stock_data = fetch_stock_data(ticker)
                    if stock_data:
                        notify_user(ticker, stock_data)
                        log_stock_data(ticker, stock_data)
                        
                        if email:
                            send_email_notification(
                                email,
                                f"Stock Alert for {ticker}",
                                f"Current Price = ${stock_data['currentPrice']}\nDay Low = ${stock_data['dayLow']}\nDay High = ${stock_data['dayHigh']}"
                            )
                time.sleep(interval)
        except ValueError:
            print("Invalid interval. Please enter a valid number.")
        except Exception as e:
            logging.error(f"Error in monitoring: {e}")

if __name__ == "__main__":
    root = Tk()
    app = StockNotifierApp(root)
    root.mainloop()
