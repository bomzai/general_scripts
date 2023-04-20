"""Process tables and zip it to data folder
"""
import pandas as pd
from os.path import join, abspath
import functools as ft
import shutil
import os
import sys

ROOT_PATH = abspath(join(__file__ , "../.."))
MYSQL_TABLES_NAMES=["old_basics_table", "old_ratings_table", "old_titles_dates"]
MONGODB_TABLES_NAMES=["recent_titles_dates", "recent_basics_table", "recent_ratings_table"]
BASICS_COLUMNS=["tconst", "titleType", "primaryTitle", "originalTitle", "isAdult", "startYear", "endYear", "runtimeMinutes", "genres"]
RATINGS_COLUMNS=["tconst", "averageRating", "numVotes"]
DATES_COLUMNS=["tconst", "dataInsertTime"]

def read_data():
    """Read dataframes in data folder
    Returns:
        pd.DataFrame: Return splitted dataset for mongo and mysql.
    """
    title_basics = pd.read_csv(join(os.environ["EXPORT_PATH"], os.environ["BASICS_TABLE_UNPROCESS_FILE"]), sep="\t")
    title_ratings = pd.read_csv(join(os.environ["EXPORT_PATH"], os.environ["RATINGS_TABLE_UNPROCESS_FILE"]), sep="\t")
    title_dates = pd.read_csv(join(os.environ["EXPORT_PATH"], os.environ["DATES_TABLE_UNPROCESS_FILE"]), sep="\t")
    return title_basics, title_ratings, title_dates

def process_data():
    """Chunk dataframes into 6 tables filtered on recent dates
    Returns:
        pd.DataFrame
    """
    title_basics, title_ratings, title_dates = read_data()
    dfs = [title_basics, title_ratings, title_dates]

    # Join all tables to filter on the date
    titles = ft.reduce(lambda left, right: pd.merge(left, right, on='tconst'), dfs)

    # Then rebuild back the tables filtered on the date
    old_basics_table = titles[titles["dataInsertTime"] < os.environ["INSERTION_DATE"]][BASICS_COLUMNS]
    old_ratings_table = titles[titles["dataInsertTime"] < os.environ["INSERTION_DATE"]][RATINGS_COLUMNS]
    old_titles_dates = titles[titles["dataInsertTime"] < os.environ["INSERTION_DATE"]][DATES_COLUMNS]
    recent_basics_table = titles[titles["dataInsertTime"] > os.environ["INSERTION_DATE"]][BASICS_COLUMNS]
    recent_ratings_table = titles[titles["dataInsertTime"] > os.environ["INSERTION_DATE"]][RATINGS_COLUMNS]
    recent_titles_dates = titles[titles["dataInsertTime"] > os.environ["INSERTION_DATE"]][DATES_COLUMNS]

    return old_basics_table, old_ratings_table, old_titles_dates, recent_titles_dates, recent_basics_table, recent_ratings_table

def dataframe_to_tsv():
    """ Create export mysql and export mongodb folder, convert dataframes into tsv files in the export folder
    """
    old_basics_table, old_ratings_table, old_titles_dates, recent_titles_dates, recent_basics_table, recent_ratings_table = process_data()
    mysql_tables = [old_basics_table, old_ratings_table, old_titles_dates]
    mongodb_tables = [recent_titles_dates, recent_basics_table, recent_ratings_table]

    os.makedirs(os.environ["PYTHON_MYSQL_TEMP_FOLDER"])
    os.makedirs(os.environ["PYTHON_MONGODB_TEMP_FOLDER"])
    print("Created folders")

    for table, table_name in zip(mysql_tables, MYSQL_TABLES_NAMES):
        table.to_csv(join(os.environ["PYTHON_MYSQL_TEMP_FOLDER"], table_name + "." + os.environ["FILE_FORMAT"]), sep="\t", index=False)
    
    for table, table_name in zip(mongodb_tables, MONGODB_TABLES_NAMES):
        table.to_csv(join(os.environ["PYTHON_MONGODB_TEMP_FOLDER"], table_name + "." + os.environ["FILE_FORMAT"]), sep="\t", index=False)

def zip_data():
    """ Zip tsv files into export folder
    """
    shutil.make_archive(os.environ["MONGODB_ZIP_DATA_PATH"], 'tar', os.environ["PYTHON_MONGODB_TEMP_FOLDER"])
    shutil.make_archive(os.environ["MYSQL_ZIP_DATA_PATH"], 'tar', os.environ["PYTHON_MYSQL_TEMP_FOLDER"])
    print("Archives done")

    # Create EOF file telling the data prep is done
    open(os.environ["PYTHON_MYSQL_EOF"], 'a').close()
    open(os.environ["PYTHON_MONGODB_EOF"], 'a').close()

if __name__ == '__main__':
    if sys.argv[1] == "docker":
        ROOT_PATH = "data"

    dataframe_to_tsv()
    zip_data()

    # Delete useless folder
    shutil.rmtree(os.environ["PYTHON_MYSQL_TEMP_FOLDER"])
    shutil.rmtree(os.environ["PYTHON_MONGODB_TEMP_FOLDER"])
    print("MongoDB and MySQL temp folders deleted")