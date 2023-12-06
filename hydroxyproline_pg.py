import pandas as pd
import os
import os, sys
import warnings
import psycopg2
from psycopg2 import Error
import json
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
def insert_hp_csv_data_to_pgdb(root_directory, file_name, table_name):

    if table_name == "biopsy_result":
        column_map = "/Users/wayne/Documents/Programming/vscode/API/SQL_query/column_map/biopsy_map.json"
    if table_name == "hydroxyproline_raw":
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

        # Loop through file in directory 
        for folder_name in os.listdir(root_directory):
            folder_path = os.path.join(root_directory, folder_name)
            # check if subfolder
            if os.path.isdir(folder_path):
                print(f"Folder: {folder_path}")
            
                # # Print the file names in the current subfolder
                # for file_name in os.listdir(folder_path):
                #     print(f" - {file_name}")

                # have a text file to indicate which folder has been processed
                # make a text file if not exist
                remembered_folders_file = 'hydroxyproline_processed_files.txt'
                file_path = os.path.join(os.path.dirname(__file__), 'hydroxyproline_processed_files.txt')
                if not os.path.exists(file_path):
                    with open(file_path, 'w'):
                        pass
                else:
                    pass    
                
                with open(remembered_folders_file, 'r+') as f:
                    if folder_name not in f.read():
                        data = pd.read_csv(folder_path + '/' + file_name, na_values=['NaN'])

                        # Replace NaN values with None
                        df = data.where(pd.notna(data), None)
                        
                        #df = df.iloc[6136:,:]

                        # replace empty date with None
                        try:
                            df['reaction_date'] = df['reaction_date'].replace('01-00-1900',0).replace([0],[None])
                        except:
                            pass

                        # Check if the table exists
                        query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)"
                        cur.execute(query, (table_name,))
                        table_exists = cur.fetchone()[0]

                        if table_exists:
                            print(f"The table '{table_name}' exists.")
                        else:
                            print(f"The table '{table_name}' does not exist.")
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
                        
                        update_columns = ', '.join([f'{col} = EXCLUDED.{col}' for col in postgresql_columns])

                        # Create the INSERT query (will insert even if duplicate)
                        query = f'''INSERT INTO analytical_db.{table_name}({columns}) VALUES ({placeholders}) ON CONFLICT (id) DO UPDATE SET {update_columns}'''

                        # insert multiple row into dataframe
                        # creates a list of tuples (data_values) where each tuple represents a row in your DataFrame. Then, the executemany method is used to insert all the rows with a single query. This can significantly improve the performance compared to inserting rows one by one.
                        data_values = [tuple(row) for _, row in df.iterrows()]
                        cur.executemany(query, data_values)

                        # Insert data from the DataFrame
                        # for _, row in df.iterrows():
                        #     print(_,'inserted successfully')
                        #     cur.execute(query, tuple(row))
                            
                        connection.commit()
                        print('success')

                        f.write(folder_name + ',')     
                    
                    else:
                        continue

               
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cur.close()
            connection.close()
            print("PostgreSQL connection is closed")
                
if __name__ == "__main__":
    path = resource_path('hp_raw_postgresql')
    insert_hp_csv_data_to_pgdb(path,file_name='hp_combined_raw.csv',table_name='hydroxyproline_raw')

    # maybe i can implmeent this through looping the commit
     # rows_to_upload = 50
        # chunk_size = 10
        # start=0
        # end=0
        # while end <= rows_to_upload:
            
        #     start, end = (start, start+chunk_size)
        #     print(start,end)
        #     start = end
