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
    glue_symbol="NVDA"
    today = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    s3_base_path = os.getenv('S3_BASE_PATH', f's3://bucket-final-msds0144/vectorbt_output/nvda_stock_data/symbol={glue_symbol}/')
    s3_today_path = f"{s3_base_path}date={today}/"
    db_table = os.getenv('DB_TABLE', 'nvda_stock_data')
    db_connection = os.getenv('DB_CONNECTION', 'rds-postgres-connection')
    db_schema = os.getenv('DB_SCHEMA', 'public')

    print(f"📥 Reading today's partition from S3: {s3_today_path}")
    try:
        df_today = wr.s3.read_parquet(path=s3_today_path, dataset=True)
    except Exception as e:
        print(f"⚠️ No data found for today ({today}). Skipping. Error: {str(e)}")
        job.commit()
        return

    if df_today.empty:
        print(f"⚠️ No data rows found in today's partition.")
        job.commit()
        return

    print(f"✅ Loaded {len(df_today)} rows for {today}")

    conn = wr.catalog.get_connection(db_connection)

    # Get list of symbols to upsert
    symbols = df_today['symbol'].dropna().unique()

    for symbol in symbols:
        print(f"\n🔁 Processing upsert for symbol: {symbol}")

        df_symbol_today = df_today[df_today['symbol'] == symbol]

        query = f"SELECT * FROM {db_schema}.{db_table} WHERE date = '{today}' AND symbol = '{symbol}'"
        try:
            df_existing = wr.db.read_sql_query(query, con=conn)
        except Exception:
            df_existing = pd.DataFrame()

        if not df_existing.empty:
            df_combined = pd.concat([df_existing, df_symbol_today], ignore_index=True)
            df_combined.drop_duplicates(subset=['date', 'symbol'], keep='last', inplace=True)
        else:
            df_combined = df_symbol_today

        print(f"🗑️ Deleting old records for {symbol} on {today}...")
        try:
            wr.db.delete_where(
                table=db_table,
                con=conn,
                schema=db_schema,
                where=f"date = '{today}' AND symbol = '{symbol}'"
            )
        except Exception as e:
            print(f"⚠️ Delete failed for {symbol}. Continuing. Error: {str(e)}")

        print(f"📝 Writing {len(df_combined)} rows to RDS for {symbol}")
        wr.db.to_sql(
            df=df_combined,
            con=conn,
            schema=db_schema,
            table=db_table,
            mode='append',
            index=False
        )

    print(f"\n✅ All symbol upserts complete for {today}")
    job.commit()

if __name__ == "__main__":
    main()
