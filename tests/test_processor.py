import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data.processor import StockDataProcessor

# First, let's create some test fixtures that will provide our test data
@pytest.fixture
def valid_stock_data():
    dates = pd.date_range(start='2024-01-01', periods=5, freq='D')
    return pd.DataFrame({
        'Open':  [100.0, 101.0, 102.0, 101.0, 103.0],
        'High':  [105.0, 104.0, 106.0, 103.0, 107.0],
        'Low':   [98.0,  99.0,  100.0, 98.0,  102.0],
        'Close': [103.0, 102.0, 104.0, 102.0, 106.0],
        'Volume':[1000,  1100,  950,   1200,  1300]
    }, index=dates)

@pytest.fixture
def invalid_stock_data():
    dates = pd.date_range(start='2024-01-01', periods=3, freq='D')
    return pd.DataFrame({
        'Open':  [100.0, -101.0, 102.0],  # Contains negative price
        'High':  [98.0,  104.0,  106.0],  # High less than Low on first day
        'Low':   [99.0,  99.0,   100.0],
        'Close': [103.0, 102.0,  np.nan], # Contains missing value
        'Volume':[1000,  -100,   950]     # Contains negative volume
    }, index=dates)

def test_validate_valid_data(valid_stock_data):
    processor = StockDataProcessor()
    assert processor.validate_data(valid_stock_data) == True

def test_validate_invalid_data(invalid_stock_data):
    processor = StockDataProcessor()
    assert processor.validate_data(invalid_stock_data) == False

def test_validate_data_with_missing_columns():
    processor = StockDataProcessor()
    #Missing the 'Volume' column
    incomplete_data = pd.DataFrame({
        'Open': [100.0],
        'High': [105.0],
        'Low': [98.0],
        'Close': [103.0]
    })
    assert processor.validate_data(incomplete_data) == False

def test_technical_indicators_calculation(valid_stock_data):
    processor = StockDataProcessor()
    result = processor.calculate_technical_indicators(valid_stock_data)
    
    # Verify that all of the expected columns exist
    expected_columns = [
        'MA20', 'MA50', 'Daily_Return', 'Volatility', 'Volume_MA20'
    ]

    for col in expected_columns:
        assert col in result.columns

def test_handle_empty_dataframe():
    processor = StockDataProcessor()
    empty_df = pd.DataFrame()
    assert processor.validate_data(empty_df) == False

def test_handle_none_input():
    processor = StockDataProcessor()
    assert processor.validate_data(None) == False

