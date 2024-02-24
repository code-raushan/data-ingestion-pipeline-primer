import os
import pandas as pd
from time import time
from sqlalchemy import create_engine
import argparse

def main(params):

    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url

    csv_name = 'output.csv'

    if url.endswith('.csv.gz'):
        csv_name = 'output.csv.gz'
    else:
        csv_name = 'output.csv'

    os.system(f"wget {url} -O {csv_name}")

    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)
    
    df = next(df_iter)

    df.head(n=0).to_sql(name=table_name, con=engine, if_exists="replace")

    df.to_sql(name=table_name, con=engine, if_exists="append")

    while True:
        try:
            time_start = time()
            df = next(df_iter)
            
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            
            df.to_sql(name="yellow_taxi_data", con=engine, if_exists="append")
            
            time_end = time()
            
            print(f"inserted chunk in {time_end-time_start} seconds")

        except StopIteration: 
            print("Finished ingesting data into database")
            break



if __name__=='__main__':

    parser = argparse.ArgumentParser(description='Arguments for data ingestion')

    parser.add_argument("--user", required=True, help="username for postgresdb")
    parser.add_argument("--password", required=True, help="password for postgresdb")
    parser.add_argument("--host", required=True, help="host address of postgresdb")
    parser.add_argument("--port", required=True, help="port of running postgresdb")
    parser.add_argument("--db", required=True, help="database name")
    parser.add_argument("--table_name", required=True, help="table_name of postgresdb")
    parser.add_argument("--url", required=True, help="url to download csv")

    args = parser.parse_args()

    main(args)



