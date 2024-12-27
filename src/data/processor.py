import pandas as pd
import numpy as np
import logging


logger = logging.getLogger(__name__)


class StockDataProcessor:
    def __init__(self):
        self.required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    def validate_data(self, data: pd.DataFrame) -> bool:
        try:
            if data is None or data.empty:
                logger.error("Data is empty or None")
                return False
                
            if not all(col in data.columns for col in self.required_columns):
                logger.error(f"Missing required columns")
                return False
            
            # checks missing values
            if data[self.required_columns].isnull().any().any():
                logger.error("Found missing values in critical columns")
                return False
            
            # High should be >= Low
            if not (data['High'] >= data['Low']).all():
                logger.error("Found High prices lower than Low prices")
                return False
            
            # non-negative price check
            if (data[['Open', 'High', 'Low', 'Close']] < 0).any().any():
                logger.error("Found negative prices")
                return False
            
            # Volume validation
            if (data['Volume'] < 0).any():
                logger.error("Found negative volume values")
                return False
            
            logger.info("Data validation successful")
            return True
                
            return True
        
        except Exception as e:
            logger.error("Error during data validation")
            return False
        
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        try: 
            df = data.copy() # copy the data to avoid having to modify the original

            # Calculate moving averages
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA50'] = df['Close'].rolling(window=50).mean()

            # Calculate daily returns
            df['Daily_Return'] = df['Close'].pct_change() # pct calculates % change from curr and previous row

            # Calculate volatility (20-day rolling standard deviation of returns)
            df['Volatility'] = df['Daily_Return'].rolling(window=20).std()
                
            # Calculate trading volume moving average
            df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
                
            logger.info("Successfully calculated technical indicators")
            return df
        
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            raise

    