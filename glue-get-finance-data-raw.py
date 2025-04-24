import sys
import os
import boto3
import awswrangler as wr
import pandas as pd
import vectorbt as vbt
from datetime import datetime
import json

def main():
    # Parameters
    symbols = ['NVDA']
    start_date = '2021-01-01'
    end_date = datetime.today().strftime('%Y-%m-%d')

    # Download stock data
    price = vbt.YFData.download(
        symbols, 
        start=start_date, 
        end=end_date, 
        interval='1d',
        missing_index='drop'
    )

    # Clean up the DataFrame
    df = price.data[symbols[0]]
    df.drop(['Volume', 'Dividends', 'Stock Splits'], axis=1, inplace=True)
    df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')

    # S3 Output
    s3_bucket = os.getenv('S3_BUCKET', 'bucket-final-msds0144')
    s3_key = os.getenv('S3_KEY', f'vectorbt_output/nvda_{datetime.today().strftime("%Y%m%d")}.csv')
    s3_path = f's3://{s3_bucket}/{s3_key}'

    wr.s3.to_csv(
        df, 
        index=True,
        path=s3_path, 
        mode='overwrite',
        database='project',
        table='raw_yfinance',
        dataset=True
        )

    print(json.dumps({'statusCode': 200, 'message': f'Data for {symbols[0]} saved to {s3_path}'}))

if __name__ == "__main__":
    main()
