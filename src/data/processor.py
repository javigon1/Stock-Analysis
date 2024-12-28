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
        print(data)
        if not self.validate_data(data):
            raise ValueError("Input data failed validation checks")
    
        try: 
            required_days = 50  # We need at least 50 days for MA50
            if len(data) < required_days:
                raise ValueError(f"Need at least {required_days} days of data for reliable indicators. Current data has {len(data)} days.")
        
            df = data.copy() # copy the data to avoid having to modify the original

            # Calculate moving averages
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA50'] = df['Close'].rolling(window=50).mean()

            # Exponential Moving Average (EMA)
            # .ewm() calculates the exponential weighted mean
            df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean() 

            # Calculate the daily returns
            df['Daily_Return'] = df['Close'].pct_change() # pct calculates % change from curr and previous row

            # Calculate volatility (20-day rolling standard deviation of returns)
            df['Volatility'] = df['Daily_Return'].rolling(window=20).std()
                
            # Volume indicators
            df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']

            # Relative Strength Index (RSI)
            delta = df['Close'].diff() # .diff() calculates the difference between consecutive rows
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            # rs = average gain over average loss in a time period (e.g. 14 days)
            rs = gain / loss
            # rsi formula
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['BB_Middle'] = df['Close'].rolling(window=20).mean()
            std_dev = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (std_dev * 2)
            df['BB_Lower'] = df['BB_Middle'] - (std_dev * 2)
            
            # Add indicator statuses
            df['Above_MA50'] = (df['Close'] > df['MA50']).astype(int)
            df['RSI_Overbought'] = (df['RSI'] > 70).astype(int)
            df['RSI_Oversold'] = (df['RSI'] < 30).astype(int)
            
            # Clean up any infinite values
            df.replace([np.inf, -np.inf], np.nan, inplace=True)

            # Critical indicators that must be present for valid analysis
            critical_indicators = [
                'MA20', 'MA50', 'RSI', 'BB_Middle', 'BB_Upper', 'BB_Lower',
                'Volatility', 'Volume_MA20', 'Volume_Ratio'
            ]

            # Remove rows where any critical indicator is missing
            df_valid = df.dropna(subset=critical_indicators)

            if len(df_valid) == 0:
                raise ValueError("No valid data points after calculating indicators")

                
            logger.info("Successfully calculated technical indicators")
            return df
        
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            raise

    