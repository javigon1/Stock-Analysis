import pandas as pd
import numpy as np
import logging


logger = logging.getLogger(__name__)


class StockDataProcessor:
    def __init__(self):
        self.required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    def validate_data(self, data):
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