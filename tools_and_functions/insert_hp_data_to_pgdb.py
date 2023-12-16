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
def insert_hp_csv_data_to_pgdb(data, table):
    
    if table == "biopsy_result":
        column_map = "/Users/wayne/Documents/Programming/vscode/API/SQL_query/column_map/biopsy_map.json"
    if table == "hydroxyproline_raw":
        column_map = "/Users/wayne/Documents/Programming/vscode/API/SQL_query/column_map/hp_assay_map.json"
    # json file maps csv column names to postgresql column names
    with open(column_map, 'r') as file:
        map = json.load(file)

    # connect to db
    try:
        connection = psycopg2.connect(
        host="34.134.210.165",
        database="vitrolabs",
        user="postgres",
        password="Vitrolabs2023!",
        port=5432)
        
        cur = connection.cursor()

        try:
            # Replace NaN values with None
            df = data.where(pd.notna(data), None)
                    # replace empty date with None
            try:
                df['reaction_date'] = df['reaction_date'].replace('01-00-1900',0).replace([0],[None])
            except:
                pass

        except:
            print('unable to read the dataframe')

        # Check if the table exists
        query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)"
        cur.execute(query, (table,))
        table_exists = cur.fetchone()[0]

        if table_exists:
            print(f"The table '{table}' exists.")
        else:
            print(f"The table '{table}' does not exist.")
            raise Exception('create table in postgresql first with desired names. Make sure json names match them')

        # Use the mapping to determine the corresponding PostgreSQL column name
        postgresql_columns = []
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

        # # rename file and move to archive
        # current_time = datetime.now().strftime("%Y%m%d%H%M%S") # Get the current timestamp

        # # Create the new file name with the current timestamp
        # new_file_name = f'{current_time}{file_name}'
        # os.rename(root_directory + '/' + file_name, root_directory + '/' + new_file_name)

        # # move file to archive folder
        # shutil.move(root_directory + '/' + new_file_name, archive_folder)
        
                 
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cur.close()
            connection.close()
            print("PostgreSQL connection is closed")

                
if __name__ == "__main__":
    path = resource_path('hp_biopsy_postgresql')
    archive_folder = '/Users/wayne/Documents/Programming/vscode/API/SQL_query/hp_biopsy_postgresql/archive'
    insert_hp_csv_data_to_pgdb(path,file_name='biopsy_result.csv',table_name='biopsy_result', archive_folder=archive_folder)

    # maybe i can implmeent this through looping the commit
     # rows_to_upload = 50
        # chunk_size = 10
        # start=0
        # end=0
        # while end <= rows_to_upload:
            
        #     start, end = (start, start+chunk_size)
        #     print(start,end)
        #     start = end