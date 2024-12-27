import pytest
from datetime import datetime, timedelta
from src.data.collector import StockDataCollector 
# get the class from the src code

def test_fetch_stock_data():
    # create an instance of the class
    collector = StockDataCollector()

    data = collector.fetch_stock_data("AAPL", start_date="2024-01-01", end_date="2024-01-07")

    assert data is not None
    assert not data.empty   
    assert "Close" in data.columns
    assert "Volume" in data.columns
    assert len(data) > 0

def test_invalid_symbol():
    collector = StockDataCollector()

    data = collector.fetch_stock_data("INVALID_STOCK", start_date="2024-01-01", end_date="2024-01-07")

    assert data is None
