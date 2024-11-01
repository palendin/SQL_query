# for manual upload new rows from data_from_instrument to postgres

import pandas as pd
import os, sys
import psycopg2
from psycopg2 import Error
import shutil
import gspread as gs
import json
import numpy as np
from tools_and_functions.read_gsheet import read_gsheet
from tools_and_functions.insert_instrument_to_pgdb import insert_flex_csv_to_pg

# define the path to be base path of the PC + the folder containing the data source
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)

    return path

# temporary solution: read gsheet -> upload to postgresql
def flex2_processing(start_rows, file, archive_directory):
    
    df = read_gsheet(file_id='1CFYh78GX4T_xjn-nOZT0ysmWQdJCYz7yh3cy97OOe1g', sheet_name='flex2')

    # convert empty cells to None
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df = df.where(pd.notna(df),None)

    # replace cells with "-" with None
    df = df.replace("-",np.nan)
    df = df.where(pd.notna(df),None)

    # append the data starting from a specific row
    df = df.loc[start_rows:]
    df = df.rename(columns={'Vessel Temperature (¬∞C)':'temperature'})
    print(df.head(10))
    insert_flex_csv_to_pg(df,'flex2')

if __name__ == "__main__":
    flex2_processing(start_rows = 0, file=None, archive_directory=None)