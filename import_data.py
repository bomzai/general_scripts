"""Process tables and export it to MongoDB and MySQL with localhost and their open ports.
This script should be run after the create_mysql_db.sql script
Run the script with --db argument : 
    --db mongodb 
    --db mysql
"""

from sqlalchemy import create_engine
from os.path import join, abspath
from zip_data import process_data
from pymongo import MongoClient
import argparse
import time
import os
from dotenv import load_dotenv
load_dotenv()


MYSQL_URL = "mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_ADDRESS}/{DATABASE}"\
    .format(MYSQL_USER=os.environ["MYSQL_USER"],
            MYSQL_PASSWORD=os.environ["MYSQL_PASSWORD"],
            MYSQL_ADDRESS=os.environ["MYSQL_ADDRESS"],
            DATABASE=os.environ["DATABASE"])

def parse_database_args():
    """Return the database argument passed when running the script
    
    Returns:
        argparese.ArgumentParser: argument string format
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=str)
    args = parser.parse_args()
    
    return args.db


def mysql_process(old_basics_table, old_ratings_table, old_titles_dates):
    """Export tables to MySQL

    Args:
        old_basics_table (pd.DataFrame): films data table older inserted
        old_ratings_table (pd.DataFrame): films ratings table older inserted
        old_titles_dates (pd.DataFrame): films primary key and old dates insertion associated table
    """

    print("Processing mysql data...")

    engine = create_engine(MYSQL_URL)
    
    with engine.connect() as connection:
        old_basics_table.to_sql(con=engine, name=os.environ["BASICS_TABLE"], schema=os.environ["DATABASE"], index=False, if_exists="replace")
        old_ratings_table.to_sql(con=engine, name=os.environ["RATINGS_TABLE"], schema=os.environ["DATABASE"], index=False, if_exists="replace")
        old_titles_dates.to_sql(con=engine, name=os.environ["DATES_TABLE"], schema=os.environ["DATABASE"], index=False, if_exists="replace")
        print("Tables inserted")

        connection.close()

def mongodb_process(recent_basics_table, recent_ratings_table, recent_titles_dates):
    """Create database, collections and export documents to MongoDB

    Args:
        recent_basics_table (pd.DataFrame): films data table newly inserted
        recent_ratings_table (pd.DataFrame): films ratings table newly inserted
        recent_titles_dates (pd.DataFrame): films primary key and new dates insertion associated table
    """

    print("Processing mongodb data...")

    try:
        client =  MongoClient(host=os.environ["MONGODB_ADDRESS"], port=int(os.environ["MONGODB_PORT"]), username=os.environ["MONGODB_USER"], password=os.environ["MONGODB_PASSWORD"])
    except Exception as ex:
        print("Connection failed, error as follows: \n", ex)

    else:
        # Mannualy create database 
        db = client[os.environ["DATABASE"]]
    
    db.basics.insert_many(recent_basics_table.to_dict("records"))
    db.ratings.insert_many(recent_ratings_table.to_dict("records"))
    db.dates.insert_many(recent_titles_dates.to_dict("records"))   

    print("Documents inserted")
    client.close()



if __name__ == '__main__': 

    start_processing = time.time()

    old_basics_table, old_ratings_table, old_titles_dates, recent_titles_dates, recent_basics_table, recent_ratings_table = process_data()
    # Do not forget to pass argument --db
    DB = parse_database_args()

    if DB == "mysql":
        mysql_process(old_basics_table, old_ratings_table, old_titles_dates)

    if DB == "mongodb":
        mongodb_process(recent_basics_table, recent_ratings_table, recent_titles_dates)
    
    end_processing = time.time()
    print(f"Time consumed by processing with import_data.py {round(end_processing - start_processing, 3)} seconds")