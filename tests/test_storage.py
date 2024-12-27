import pytest
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError
import pandas as pd
from src.data.storage import S3Handler

# Create a fake DataFrame to replicate our stock data
@pytest.fixture
def sample_stock_data():
    data = {
        'Date': ['2024-01-01', '2024-01-02'],
        'Open': [150, 152],
        'Close': [155, 153],
        'Volume': [1000, 1200]
    }
    return pd.DataFrame(data)

def test_save_stock_data_success(sample_stock_data):
    with patch('boto3.client') as mock_boto3:
        # Create a mock S3 client that returns success
        mock_s3 = Mock()
        mock_boto3.return_value = mock_s3
        
        # Create our S3Handler with a test bucket
        handler = S3Handler('test-bucket')
        
        # Test saving some sample data
        result = handler.save_stock_data(sample_stock_data, 'AAPL')
        
        # Verify the save was successful
        assert result == True
        # Verify put_object was called with correct bucket
        mock_s3.put_object.assert_called_once()
        call_args = mock_s3.put_object.call_args[1]
        assert call_args['Bucket'] == 'test-bucket'
        assert 'AAPL' in call_args['Key']

def test_save_stock_data_failure(sample_stock_data):
    with patch('boto3.client') as mock_boto3:
        # Create a mock S3 client that raises an error
        mock_s3 = Mock()
        mock_s3.put_object.side_effect = ClientError(
            {"Error": {"Code": "SomeError", "Message": "Test error"}}, 
            "put_object"
        )
        mock_boto3.return_value = mock_s3
        
        handler = S3Handler('test-bucket')
        result = handler.save_stock_data(sample_stock_data, 'AAPL')
        
        # Verify the save failed gracefully
        assert result == False
