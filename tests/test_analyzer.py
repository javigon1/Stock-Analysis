import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data.analyzer import StockDataAnalyzer

# Strong upward trend
@pytest.fixture
def uptrend_data():
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    
    # Create base price data
    base_price = 100
    closes = [base_price + i * 0.5 + np.random.normal(0, 0.2) for i in range(100)]
    
    # Create DataFrame with all required base columns
    df = pd.DataFrame({
        'Open': [p - 0.5 for p in closes],
        'High': [p + 1 for p in closes],
        'Low': [p - 1 for p in closes],
        'Close': closes,
        'Volume': [10000 + np.random.normal(0, 1000) for _ in range(100)]
    }, index=dates)
    
    return df

def test_trend_analysis_bullish(uptrend_data):
    analyzer = StockDataAnalyzer()
    # First prepare the data
    analyzer.prepare_data(uptrend_data)
    # Then analyze
    trend_analysis = analyzer.analyze_trend()
    
    assert trend_analysis['direction'] == 'BULLISH'
    assert 'strength' in trend_analysis
    assert trend_analysis['ma_crossover'] in ['BULLISH', 'BEARISH']
    assert trend_analysis['price_momentum'] in ['INCREASING', 'DECREASING']

def test_momentum_analysis_overbought():
    analyzer = StockDataAnalyzer()
    # Create 60 days of data to ensure we have enough history
    dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
    
    # Create price data that will generate an overbought condition
    closes = []
    current_price = 100
    # Create an upward trend that will push RSI into overbought territory
    for i in range(60):
        if i > 45:  # Last 15 days showing strong upward movement
            current_price *= 1.02  # 2% daily increase
        closes.append(current_price)
    
    data = pd.DataFrame({
        'Open': [p * 0.99 for p in closes],  # Open slightly lower
        'High': [p * 1.02 for p in closes],  # High slightly higher
        'Low': [p * 0.98 for p in closes],   # Low slightly lower
        'Close': closes,
        'Volume': [10000 + np.random.normal(0, 1000) for _ in range(60)]
    }, index=dates)
    
    analyzer.prepare_data(data)
    momentum = analyzer.analyze_momentum()
    
    assert momentum['rsi_status'] == 'OVERBOUGHT'

def test_risk_analysis_high_volatility():
    analyzer = StockDataAnalyzer()
    dates = pd.date_range(start='2024-01-01', periods=60, freq='D')  # Need enough data for indicators
    
    # Create volatile price movement
    closes = [100]
    for _ in range(59):
        closes.append(closes[-1] * (1 + np.random.uniform(-0.03, 0.03)))
    
    data = pd.DataFrame({
        'Open': [p * 0.99 for p in closes],
        'High': [p * 1.02 for p in closes],
        'Low': [p * 0.98 for p in closes],
        'Close': closes,
        'Volume': [1000 * (1 + abs(np.random.normal(0, 0.5))) for _ in range(60)]
    }, index=dates)
    
    analyzer.prepare_data(data)
    risk = analyzer.analyze_risk()
    
    assert 'volatility_level' in risk
    assert 'volume_analysis' in risk
    assert 'bb_position' in risk

def test_pattern_recognition():
    analyzer = StockDataAnalyzer()
    dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
    
    # Create a double bottom pattern
    base_pattern = [100, 95, 90, 92, 88, 95, 92, 88, 95, 100]  # Repeat pattern

    closes = base_pattern * 6
    
    data = pd.DataFrame({
        'Open': [p - 1 for p in closes],
        'High': [p + 2 for p in closes],
        'Low': [p - 2 for p in closes],
        'Close': closes,
        'Volume': [1000 + np.random.normal(0, 100) for _ in range(60)]
    }, index=dates)
    
    analyzer.prepare_data(data)
    patterns = analyzer.analyze_patterns()
    
    assert isinstance(patterns['double_bottom'], bool)
    assert 'pattern_quality' in patterns

def test_complete_analysis_integration(uptrend_data):
    analyzer = StockDataAnalyzer()
    
    # The fixture is now correctly providing all required columns
    analysis = analyzer.get_complete_analysis(uptrend_data)
    
    assert 'trend_analysis' in analysis
    assert 'momentum_analysis' in analysis
    assert 'risk_analysis' in analysis
    assert 'pattern_analysis' in analysis
    assert 'market_context' in analysis
    assert 'trading_signals' in analysis