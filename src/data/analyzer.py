import pandas as pd
import numpy as np
import logging
from .processor import StockDataProcessor


logger = logging.getLogger(__name__)


class StockDataAnalyzer:
    def __init__(self):
        self.processor = StockDataProcessor()
        self.processed_data = None

    def prepare_data(self, data: pd.DataFrame) -> pd.DataFrame:
        self.processed_data = self.processor.calculate_technical_indicators(data)
        return self.processed_data

    # Make use of various metrics to generate a trend response
    def analyze_trend(self) -> dict:
        try:
            if self.processed_data is None:
                raise ValueError("Data must be processed before analysis. Call prepare_data first.")
            
            current = self.processed_data.iloc[-1]
            previous = self.processed_data.iloc[-2]

            trend_status = {
                'direction': 'BULLISH' if current['Close'] > current['MA50'] else 'BEARISH',
                'strength': abs(current['Close'] - current['MA50']) / current['MA50'] * 100,
                'ma_crossover': 'BULLISH' if current['MA20'] > current['MA50'] else 'BEARISH',
                'price_momentum': 'INCREASING' if current['Close'] > previous['Close'] else 'DECREASING'
            }

            logger.info(f"Trend analysis completed. Direction: {trend_status['direction']}")
            return trend_status

        except Exception as e:
            logger.error(f"Error in trend analysis: {str(e)}")
            raise
    
    # Analyze how the momentum of the stock is doing with the RSI calculation
    def analyze_momentum(self) -> dict:
        try:
            # Should be:
            if self.processed_data is None:
                raise ValueError("Data must be processed before analysis. Call prepare_data first.")
            
            current = self.processed_data.iloc[-1]
            previous = self.processed_data.iloc[-2]

            momentum_status = {
                'rsi_status': ('OVERBOUGHT' if current['RSI'] > 70 else
                              'OVERSOLD' if current['RSI'] < 30 else 'NEUTRAL'),
                'rsi_value': current['RSI'],
                'rsi_trend': 'INCREASING' if current['RSI'] > previous['RSI'] else 'DECREASING'
            }

            return momentum_status
        
        except Exception as e:
            logger.error(f"Error in momentum analysis: {str(e)}")
            raise

    # Figure how reliable the insights are going to be 
    def analyze_risk(self) -> dict:
        try:
            if self.processed_data is None:
                raise ValueError("Data must be processed before analysis. Call prepare_data first.")

            current = self.processed_data.iloc[-1]
            previous = self.processed_data.iloc[-2]

            # Calculate volume-based risk factors
            volume_risk = {
                'volume_trend': 'HIGH' if current['Volume'] > current['Volume_MA20'] * 1.5 
                            else 'LOW' if current['Volume'] < current['Volume_MA20'] * 0.5 
                            else 'NORMAL',
                'volume_change': (current['Volume'] - previous['Volume']) / previous['Volume'] * 100,
                'price_volume_alignment': 'CONFIRMED' if (
                    (current['Close'] > previous['Close'] and current['Volume'] > current['Volume_MA20']) or
                    (current['Close'] < previous['Close'] and current['Volume'] < current['Volume_MA20'])
                ) else 'DIVERGENT'
            }
            
            # Combine volume risk with the other risk metrics (boiller bands and volatility)
            risk_status = {
                'volatility_level': ('HIGH' if current['Volatility'] > self.processed_data['Volatility'].mean() * 1.2 
                                else 'LOW' if current['Volatility'] < self.processed_data['Volatility'].mean() * 0.8 
                                else 'MODERATE'),
                'bb_position': (current['Close'] - current['BB_Lower']) / 
                            (current['BB_Upper'] - current['BB_Lower']),
                'price_vs_bands': ('UPPER_BAND' if current['Close'] >= current['BB_Upper']
                                else 'LOWER_BAND' if current['Close'] <= current['BB_Lower']
                                else 'MIDDLE'),
                'volume_analysis': volume_risk
            }

            return risk_status
        
        except Exception as e:
            logger.error(f"Error in risk analysis: {str(e)}")
            raise

    # Generate a detailed trading signals by analyzing multiple technical indicators
    # and their relationships. Each signal combination represents a different
    # market scenario with its own implications for trading.
    def get_trading_signals(self) -> dict:
        try: 
            trend = self.analyze_trend()
            momentum = self.analyze_momentum()
            risk = self.analyze_risk()
            # current = self.processed_data.iloc[-1]
            
            signal = {
                'recommendation': 'HOLD',
                'confidence': 'LOW',
                'supporting_factors': []
            }

            # Strong Buy Signals
            if (trend['direction'] == 'BULLISH' and 
                momentum['rsi_status'] == 'OVERSOLD' and
                risk['volatility_level'] != 'HIGH' and
                risk['volume_analysis']['volume_trend'] == 'HIGH'):
                signal['recommendation'] = 'STRONG_BUY'
                signal['confidence'] = 'VERY_HIGH'
                signal['supporting_factors'].extend([
                    'Strong bullish trend',
                    'Oversold RSI indicating potential reversal',
                    'High volume confirming trend',
                    'Moderate volatility suggesting stable movement'
                ])

            # Moderate Buy Signal - Recovery Pattern
            elif (trend['direction'] == 'BULLISH' and
                momentum['rsi_value'] > 40 and
                momentum['rsi_trend'] == 'INCREASING' and
                trend['ma_crossover'] == 'BULLISH'):
                signal['recommendation'] = 'BUY'
                signal['confidence'] = 'MODERATE'
                signal['supporting_factors'].extend([
                    'Bullish trend confirmation',
                    'RSI showing recovery',
                    'Positive MA crossover'
                ])

            # Strong Sell Signal - Overbought with Weakening Trend
            elif (trend['direction'] == 'BEARISH' and
                momentum['rsi_status'] == 'OVERBOUGHT' and
                risk['price_vs_bands'] == 'UPPER_BAND' and
                risk['volume_analysis']['price_volume_alignment'] == 'DIVERGENT'):
                signal['recommendation'] = 'STRONG_SELL'
                signal['confidence'] = 'VERY_HIGH'
                signal['supporting_factors'].extend([
                    'Bearish trend developing',
                    'Overbought RSI indicating potential reversal',
                    'Price at upper Bollinger Band',
                    'Volume not supporting price movement'
                ])

            # Moderate Sell Signal - Trend Weakness
            elif (trend['direction'] == 'BEARISH' and
                momentum['rsi_value'] < 60 and
                momentum['rsi_trend'] == 'DECREASING' and
                risk['volatility_level'] == 'HIGH'):
                signal['recommendation'] = 'SELL'
                signal['confidence'] = 'MODERATE'
                signal['supporting_factors'].extend([
                    'Bearish trend',
                    'Declining momentum',
                    'High volatility indicating uncertainty'
                ])

            # Accumulation Signal - Gradual Entry Opportunity
            elif (trend['direction'] == 'BULLISH' and
                40 <= momentum['rsi_value'] <= 60 and
                risk['price_vs_bands'] == 'MIDDLE' and
                risk['volume_analysis']['volume_trend'] == 'INCREASING'):
                signal['recommendation'] = 'ACCUMULATE'
                signal['confidence'] = 'MODERATE'
                signal['supporting_factors'].extend([
                    'Stable bullish trend',
                    'Neutral RSI suggesting room for growth',
                    'Price in middle of Bollinger Bands',
                    'Increasing volume showing growing interest'
                ])

            # Distribution Signal - Gradual Exit Opportunity
            elif (trend['direction'] == 'BEARISH' and
                momentum['rsi_value'] >= 55 and
                risk['volume_analysis']['volume_trend'] == 'HIGH' and
                risk['volatility_level'] == 'INCREASING'):
                signal['recommendation'] = 'DISTRIBUTE'
                signal['confidence'] = 'MODERATE'
                signal['supporting_factors'].extend([
                    'Weakening trend',
                    'Elevated RSI',
                    'High volume suggesting selling pressure',
                    'Increasing volatility'
                ])

            # Wait and Watch Signal - Unclear Market Conditions
            elif (risk['volatility_level'] == 'HIGH' and
                momentum['rsi_value'] > 45 and momentum['rsi_value'] < 55):
                signal['recommendation'] = 'WAIT'
                signal['confidence'] = 'HIGH'
                signal['supporting_factors'].extend([
                    'High market volatility',
                    'Neutral RSI indicating no clear direction',
                    'Better to wait for clearer signals'
                ])

            return signal

        except Exception as e:
            logger.error(f"Error generating trading signals: {str(e)}")
            raise

        
    # Identifies common chart patterns that might indicate future price movements.
    # Think of this like recognizing shapes in the price movement that often
    # predict what might happen next.
    def analyze_patterns(self) -> dict:
        try:
            if self.processed_data is None:
                raise ValueError("Data must be processed before analysis. Call prepare_data first.")
            
            # We typically need several days of data to identify patterns
            recent_data = self.processed_data.tail(20)  # Look at last 20 days
            
            pattern_status = {
                'double_bottom': False,
                'double_top': False,
                'trend_line_break': False,
                'support_level': None,
                'resistance_level': None,
                'pattern_quality': 'LOW'
            }

            # Example of double bottom detection
            lows = recent_data['Low'].values
            if len(lows) >= 10:
                # Look for two similar lows with a peak in between
                # This is a simplified version - real pattern detection would be more complex
                potential_bottoms = [i for i in range(1, len(lows)-1) if 
                                lows[i] < lows[i-1] and lows[i] < lows[i+1]]
                if len(potential_bottoms) >= 2:
                    pattern_status['double_bottom'] = True
                    pattern_status['pattern_quality'] = 'MODERATE'

            return pattern_status

        except Exception as e:
            logger.error(f"Error in pattern analysis: {str(e)}")
            raise

    # Analyzes broader market context to provide a more complete picture.
    # This is like stepping back to see the bigger picture beyond just
    # the immediate price movements.
    def analyze_market_context(self) -> dict:
        try:
            if self.processed_data is None:
                raise ValueError("Data must be processed before analysis. Call prepare_data first.")
            
            context = {
                'trend_strength': {
                    'short_term': self._calculate_trend_strength(5),  # 5-day trend
                    'medium_term': self._calculate_trend_strength(20),  # 20-day trend
                    'long_term': self._calculate_trend_strength(50)  # 50-day trend
                },
                'price_levels': {
                    'year_high': self.processed_data['High'].rolling(window=252).max().iloc[-1],
                    'year_low': self.processed_data['Low'].rolling(window=252).min().iloc[-1],
                    'distance_from_high': None,
                    'distance_from_low': None
                },
                'volatility_context': {
                    'current_vs_historical': None,
                    'trend': None
                }
            }

            # Calculate distances from yearly high/low
            current_price = self.processed_data['Close'].iloc[-1]
            context['price_levels']['distance_from_high'] = \
                (context['price_levels']['year_high'] - current_price) / current_price * 100
            context['price_levels']['distance_from_low'] = \
                (current_price - context['price_levels']['year_low']) / context['price_levels']['year_low'] * 100

            return context

        except Exception as e:
            logger.error(f"Error in market context analysis: {str(e)}")
            raise

    # Helper method to calculate trend strength over a given period
    def _calculate_trend_strength(self, period: int) -> str:
        if self.processed_data is None:
            raise ValueError("Data must be processed before analysis. Call prepare_data first.")
            
        recent_data = self.processed_data.tail(period)

        price_change = (recent_data['Close'].iloc[-1] - recent_data['Close'].iloc[0]) / \
                    recent_data['Close'].iloc[0] * 100
        
        if abs(price_change) < 2:
            return 'SIDEWAYS'
        elif price_change > 5:
            return 'STRONG_UP'
        elif price_change > 2:
            return 'MODERATE_UP'
        elif price_change < -5:
            return 'STRONG_DOWN'
        else:
            return 'MODERATE_DOWN'


    # Provide a comprehensive analysis combining all our analytical components.
    # This is our main method that external code will typically call.
    def get_complete_analysis(self, data: pd.DataFrame) -> dict:
        try:
            # First, ensure we have processed data with all needed indicators
            self.prepare_data(data)

            # Combine all our analyses into one complete report
            analysis = {
                'timestamp': str(self.processed_data.index[-1]),
                'current_price': self.processed_data.iloc[-1]['Close'],
                'trend_analysis': self.analyze_trend(),
                'momentum_analysis': self.analyze_momentum(),
                'risk_analysis': self.analyze_risk(),
                'pattern_analysis': self.analyze_patterns(),
                'market_context': self.analyze_market_context(),
                'trading_signals': self.get_trading_signals()
            }

            logger.info("Completed full stock analysis")
            return analysis

        except Exception as e:
            logger.error(f"Error in complete analysis: {str(e)}")
            raise