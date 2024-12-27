import boto3
import logging
from botocore.exceptions import ClientError
from datetime import datetime


logger = logging.getLogger(__name__)

# This class will manage the storing and retrieving of data from the S3 buckets
class S3Handler:
    # Initialize the S3 client and set a bucket name
    def __init__(self, bucket_name):
        self.s3 = boto3.client("s3")
        self.bucket = bucket_name

    # Args: data (Pandas DataFrame) is the stock data to save
    #       symbol is the stock 
    # Return type: bool (true if successful, false otherwise)
    def save_stock_data(self, data, symbol):
        try:
            date = datetime.now()
            path = f"raw/stock_data/{symbol}/{date.year}/{date.month:02d}/data.csv"

            # convert the dataframe to csv
            csv_buffer = data.to_csv(index=True)

            self.s3.put_object(
                Bucket = self.bucket,
                Key = path,
                Body = csv_buffer
            )

            logger.info(f"Successfully saved {symbol} data to {path}")

            return True
        except ClientError as e:
            logger.error(f"Error saving to S3: {str(e)}")
            return False


    