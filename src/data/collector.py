import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta # datetime gives me the time and date while 
# delta time represents durations (arithmetic on datetime objects)
import logging


# Set up the logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class StockDataCollector:
    def __init__(self):
        # set a 1 year window
        self.default_start = datetime.now() - timedelta(days=365)
        self.default_end = datetime.now()

    # Main method to fetch data for a single stock
    def fetch_stock_data(self, symbol, start_date=None, end_date=None):
        # Dates are expected in the YYYY-MM-DD format
        try:
            logger.info(f"Trying to fetch stock data for {symbol}")
            stock = yf.Ticker(symbol)

            start = start_date or self.default_start
            end = end_date or self.default_end

            # History is a DataFrame containing the stock info of symbol from start to end
            history = stock.history(start=start, end=end, interval="1d")

            if history.empty:
                logger.warning(f"No data was found for {symbol}")
                return None
            
            logger.info(f"Data successfully fetched for {symbol}. Size of data: {len(history)}")
            return history
        
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            raise

    # Check data quality and completeness
    def validate_data(self, data):
        if data is None or data.empty:
            logger.error("No data")
            return False
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_columns):
            logger.error("Missing expected columns")
            return False

    # Handle batch processing of multiple stocks
    def process_multiple_stocks(self, symbols):
        results = {}
        for symbol in symbols:
            try:
                data = self.fetch_stock_data(symbol)
                if data is not None:
                    results[symbol] = data
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
        return results

    # Proper error handling and logging
    # def handle_errors(self, error, symbols):


    