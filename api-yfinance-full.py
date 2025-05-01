import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

import sys
import os
import boto3
import awswrangler as wr
import pandas as pd
import vectorbt as vbt
import pandas_ta as ta
from datetime import datetime, timedelta
import json

def main():
    # Parameters
    symbols = ['NVDA']
    start_date = '2021-01-01'
    end_date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    # Download stock data
    price = vbt.YFData.download(
        symbols, 
        start=start_date, 
        end=end_date, 
        interval='1d',
        missing_index='drop'
    )

    df = price.data[symbols[0]].copy()
    df.drop(['Volume', 'Dividends', 'Stock Splits'], axis=1, inplace=True)
    df.reset_index(inplace=True)
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    # Add indicators
    df['RSI'] = ta.rsi(df.Close, length=14)
    df['SMA'] = ta.sma(df.Close, length=50)
    df['EMA'] = ta.ema(df.Close, length=50)
    df['ATR'] = ta.atr(high=df.High, low=df.Low, close=df.Close, length=14)
    macd_df = ta.macd(df.Close)
    df['MACD'] = macd_df['MACD_12_26_9']
    df.columns = [c.lower() for c in df.columns]

    # Add symbol column for partitioning
    df['symbol'] = symbols[0]

    # S3 paths and metadata
    s3_bucket = os.getenv('S3_BUCKET', 'bucket-final-msds0144')
    s3_prefix = os.getenv('S3_KEY_PREFIX', 'vectorbt_output/nvda_stock_data')
    s3_path = f's3://{s3_bucket}/{s3_prefix}'

    # Load existing data if any
    try:
        existing_df = wr.s3.read_parquet(
            path=s3_path,
            dataset=True,
            partition_filter=lambda p: p["symbol"] == symbols[0]
        )
    except Exception:
        existing_df = pd.DataFrame()
        

    # Combine and deduplicate (upsert on date)
    combined_df = pd.concat([existing_df, df], ignore_index=True)
    combined_df.drop_duplicates(subset=['date', 'symbol'], keep='last', inplace=True)
    combined_df['date'] = pd.to_datetime(combined_df['date']).dt.date

    # Write back to S3 with partitioning
    wr.s3.to_parquet(
        df=combined_df,
        path=s3_path,
        dataset=True,
        mode='overwrite',
        index=False,
        partition_cols=["symbol", "date"],
        database="project",
        table="nvda_stock_data"
    )
    # Write back to S3 with rds (transactional workload)
    wr.s3.to_parquet(
        df=combined_df,
        path="s3://bucket-final-msds0144/rds-parquet/",
        dataset=True,
        mode='overwrite',
        index=False,
    )
    print(json.dumps({'statusCode': 200, 'message': f'Data for {symbols[0]} upserted to {s3_path}'}))

if __name__ == "__main__":
    main()