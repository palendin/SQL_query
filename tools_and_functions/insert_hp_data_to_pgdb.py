import pandas as pd
import os
import os, sys
import warnings
import psycopg2
from psycopg2 import Error
import json
import shutil
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed
warnings.filterwarnings("ignore")
import traceback

# for executable purposes, defining a dynamic base path is needed for executing at different locations
# for relative path, this is a folder created in the same directory as the executable for storing HP_assay experiments
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)

    return path

# loop through each subfolder and upload specified csv file to postgresql database table
@retry(stop=stop_after_attempt(10), wait=wait_fixed(5))
def insert_hp_csv_data_to_pgdb(df, table):
    
    # connect to db
    try:
        connection = psycopg2.connect(
        host="34.134.210.165",
        database="vitrolabs",
        user="postgres",
        password="Vitrolabs2023!",
        port=5432)
        
        cur = connection.cursor()

        # Check if the table exists
        query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)"
        cur.execute(query, (table,))
        table_exists = cur.fetchone()[0]

        if table_exists:
            print(f"The table '{table}' exists.")
        else:
            print(f"The table '{table}' does not exist.")
            raise Exception('create table in postgresql first with desired names. Make sure json names match them')

        # if using this script solely to upload file
        #df['culture_date'] = pd.to_datetime(df['culture_date'], format='%m/%d/%y')
        # df.where(pd.notna(df),None) # df.where replaces NaN with None
        # df.replace({pd.NaT: None}, inplace=True) #replace NaT with None)

        # Use the mapping to determine the corresponding PostgreSQL column name
        postgresql_columns = []
        
        column_map = os.path.join(os.getcwd(),f'column_map/{table}.json')
        #column_map = '/Users/wayne/Documents/Programming/vscode/API/SQL_query/column_map/hydroxyproline_raw.json' 
        with open(column_map, 'r') as file:
            map = json.load(file)
        for col in df.columns:
            postgresql_column_name = map.get(col, col)
            postgresql_columns.append(postgresql_column_name)
    
        # Generate the column names dynamically
        columns = ', '.join(postgresql_columns)
    
        # Generate the placeholders for the VALUES clause based on the number of columns
        placeholders = ', '.join(['%s'] * len(df.columns))

        # Create the INSERT query (will insert even if duplicate)
        query = f'''INSERT INTO analytical_db.{table}({columns}) VALUES ({placeholders})''' # ON CONFLICT (id) DO UPDATE SET {update_columns}'''

        # insert multiple row into dataframe
        # creates a list of tuples (data_values) where each tuple represents a row in your DataFrame. Then, the executemany method is used to insert all the rows with a single query. This can significantly improve the performance compared to inserting rows one by one.
        data_values = [tuple(row) for _, row in df.iterrows()]
        cur.executemany(query, data_values)
            
        connection.commit()
        print(f'data from {table} upload successfully')
                 
    except (Exception) as error:
        print(traceback.format_exc())
    finally:
        if (connection):
            cur.close()
            connection.close()
            print("PostgreSQL connection is closed")

                
if __name__ == "__main__":
    # df = pd.read_csv('/Users/wayne/Documents/Programming/vscode/template-processing/postgres_manip/final_hp_raw_combined.csv')
    # print(len(df))
    # df = df.iloc[16000:18847]
    # insert_hp_csv_data_to_pgdb(df,table='hydroxyproline_raw')

    #maybe i can implmeent this through looping the commit
    rows_to_upload = 50
    chunk_size = 10
    start=0
    end=0
    while end <= rows_to_upload:
        
        start, end = (start, start+chunk_size)
        print(start,end)
        start = end