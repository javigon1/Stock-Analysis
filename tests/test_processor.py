import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data.processor import StockDataProcessor

# First, let's create some test fixtures that will provide our test data
@pytest.fixture
def valid_stock_data():
    dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
    # Creating data with a clear upward trend for testing
    return pd.DataFrame({
        'Open':  [100.0 + i * 0.5 for i in range(60)],
        'High':  [105.0 + i * 0.5 for i in range(60)],
        'Low':   [98.0 + i * 0.5 for i in range(60)],
        'Close': [103.0 + i * 0.5 for i in range(60)],
        'Volume':[1000 + i * 10 for i in range(60)]
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


def test_validate_high_lower_than_low():
    processor = StockDataProcessor()
    invalid_data = pd.DataFrame({
        'Open': [100.0],
        'High': [95.0],  # High is less than Low
        'Low': [98.0],
        'Close': [103.0],
        'Volume': [1000]
    })
    assert processor.validate_data(invalid_data) == False


def test_moving_averages_calculation(valid_stock_data):
    processor = StockDataProcessor()
    result = processor.calculate_technical_indicators(valid_stock_data)
    
    # For our test data, MA20 should exist after 20 days
    assert pd.isna(result['MA20'].iloc[18])  # Should be NaN before 20 days
    assert not pd.isna(result['MA20'].iloc[20])  # Should have value after 20 days
    
    # Test MA50 similarly
    assert pd.isna(result['MA50'].iloc[48])
    assert not pd.isna(result['MA50'].iloc[50])

def test_volume_indicators(valid_stock_data):
    processor = StockDataProcessor()
    result = processor.calculate_technical_indicators(valid_stock_data)
    
    # Volume MA should exist after 20 days
    assert pd.isna(result['Volume_MA20'].iloc[18])
    assert not pd.isna(result['Volume_MA20'].iloc[20])
    
    # Volume Ratio should be positive where it exists
    assert all(result['Volume_Ratio'].dropna() > 0)


def test_rsi_calculation(valid_stock_data):
    processor = StockDataProcessor()
    result = processor.calculate_technical_indicators(valid_stock_data)
    
    # RSI should always be between 0 and 100
    assert all((result['RSI'].dropna() >= 0) & (result['RSI'].dropna() <= 100))


def test_bollinger_bands_calculation(valid_stock_data):
    processor = StockDataProcessor()
    result = processor.calculate_technical_indicators(valid_stock_data)
    
    # Test band relationships after the initial 20-day period
    valid_bands = result.dropna(subset=['BB_Upper', 'BB_Middle', 'BB_Lower'])
    assert all(valid_bands['BB_Upper'] > valid_bands['BB_Middle'])
    assert all(valid_bands['BB_Middle'] > valid_bands['BB_Lower'])


def test_error_handling():
    processor = StockDataProcessor()
    
    # Test with empty DataFrame
    assert processor.validate_data(pd.DataFrame()) == False
    
    # Test with None
    assert processor.validate_data(None) == False
    
    # Test with invalid data types
    with pytest.raises(Exception):
        processor.calculate_technical_indicators("not a dataframe")