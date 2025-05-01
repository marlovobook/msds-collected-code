import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Glue job parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

import os
import awswrangler as wr
import pandas as pd
from datetime import datetime

def main():
    # Init Glue contexts
    sc = SparkContext()
    glueContext = GlueContext(sc)
    job = Job(glueContext)
    job.init(args['JOB_NAME'], args)

    # Config
    glue_symbol = "NVDA"
    s3_base_path = os.getenv(
        'S3_BASE_PATH',
        #f's3://bucket-final-msds0144/vectorbt_output/nvda_stock_data/symbol={glue_symbol}/'
        's3://bucket-final-msds0144/rds-parquet/'
    )
    db_table = os.getenv('DB_TABLE', 'nvda_stock_data')
    db_connection = os.getenv('DB_CONNECTION', 'rds-postgres-connection')
    db_schema = os.getenv('DB_SCHEMA', 'public')

    print(f"📥 Reading full dataset from S3: {s3_base_path}")
    try:
        df_full = wr.s3.read_parquet(path=s3_base_path, dataset=True)
    except Exception as e:
        print(f"❌ Failed to read data from S3. Error: {str(e)}")
        job.commit()
        return

    if df_full.empty:
        print(f"⚠️ No data rows found in dataset.")
        job.commit()
        return

    print(f"✅ Loaded {len(df_full)} total rows from all partitions.")

    # PostgreSQL connection
    try:
        conn = wr.postgresql.connect(connection=db_connection)
    except Exception as e:
        print(f"❌ Could not establish PostgreSQL connection. Error: {str(e)}")
        job.commit()
        return

    # Clean and write per symbol
    symbols = df_full['symbol'].dropna().unique()

    for symbol in symbols:
        print(f"\n🔁 Processing full load for symbol: {symbol}")
        df_symbol = df_full[df_full['symbol'] == symbol].copy()

        # --- 🧹 Data Cleaning ---
        # Fix and filter invalid dates
        df_symbol['date'] = pd.to_datetime(df_symbol['date'], errors='coerce')
        bad_dates = df_symbol[df_symbol['date'].isna()]
        if not bad_dates.empty:
            print(f"⚠️ Found {len(bad_dates)} rows with invalid date values. Dropping them.")
            print(bad_dates[['symbol', 'date']])

        df_symbol = df_symbol.dropna(subset=['date'])
        df_symbol['date'] = df_symbol['date'].dt.date

        # Ensure numeric columns are correct
        float_columns = ['open', 'high', 'low', 'close', 'rsi', 'sma', 'ema', 'atr', 'macd']
        for col in float_columns:
            if col in df_symbol.columns:
                df_symbol[col] = pd.to_numeric(df_symbol[col], errors='coerce')

        # --- 🔄 Full Load: Delete + Insert ---
        print(f"🗑️ Deleting old records for symbol: {symbol}")
        try:
            wr.postgresql.execute(
                sql=f"DELETE FROM {db_schema}.{db_table} WHERE symbol = '{symbol}'",
                con=conn
            )
        except Exception as e:
            print(f"⚠️ Delete failed for symbol={symbol}. Continuing. Error: {str(e)}")

        print(f"📝 Writing {len(df_symbol)} cleaned rows to RDS for symbol: {symbol}")
        try:
            wr.postgresql.to_sql(
                df=df_symbol,
                con=conn,
                schema=db_schema,
                table=db_table,
                mode='append',
                index=False
            )
        except Exception as e:
            print(f"❌ Failed to write data for symbol={symbol}. Error: {str(e)}")

    print(f"\n✅ All symbol full loads complete.")
    job.commit()

if __name__ == "__main__":
    main()
