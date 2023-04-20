"""Create a new csv file with movies ID and a random date it had been add to the database.
"""
from os.path import join, abspath
from datetime import date, timedelta
import pandas as pd
import numpy as np

root_path = abspath(join(__file__ , "../.."))

def random_dates(start : pd.Timestamp, end : pd.Timestamp, n : int, unit='D', seed=None) -> pd.Series:
    """Generate random dates between an interval.

    Args:
        start (pd.Timestamp): Start interval date.
        end (pd.Timestamp): End interval date.
        n (int): Number of dates to generate.
        unit (str, optional): Denotes the unit of the arg for numeric arg. Defaults to 'D'.
        seed (int, optional): Random seed. Defaults to None.

    Returns:
        pd.Series: Series of timestamp at format 'YYYY-MM-DD'.
    """
    if not seed:  # from piR's answer
        np.random.seed(0)

    ndays = (end - start).days + 1
    return (pd.to_timedelta(np.random.rand(n) * ndays, unit=unit) + start).date

if __name__ == "__main__":
    # Load datasets into Dataframes
    basics = pd.read_csv(join(root_path, "data/title_basics_truncated.tsv"), sep="\t")
    ratings = pd.read_csv(join(root_path, "data/title_ratings_truncated.tsv"), sep="\t")

    # Retrive unique tconst
    unique_id = pd.DataFrame(columns=["tconst", "dataInsertTime"])
    unique_id["tconst"] = pd.concat([basics["tconst"], ratings["tconst"]], ignore_index=True).drop_duplicates()

    # Generate timestamps
    start_date = pd.to_datetime(date.today() - timedelta(days=365))
    end_date = pd.to_datetime(date.today())
    unique_id["dataInsertTime"] = random_dates(start_date, end_date, len(unique_id.index))

    # Save new dataframe
    unique_id.to_csv(join(root_path, "data/dataInsertTime.tsv"), sep='\t', index=False)
    print("Done.")