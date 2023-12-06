import pandas as pd
import os
import os, sys
import warnings
import psycopg2
from psycopg2 import Error
import json
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

# root directory points to tracker folder. function good for single file insert to pg
def insert_tracker_data_to_pgdb(root_directory, file_name, table_name):

    # json file maps csv column names to postgresql column names
    column_map = '/Users/wayne/Documents/Programming/vscode/API/SQL_query/column_map/analytical_tracker.json'
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
        for files in os.listdir(root_directory):
            file_path = os.path.join(root_directory,files)

            files = os.listdir(root_directory)
            if file_name in files:
                try:
                    data = pd.read_csv(root_directory + '/' + file_name, na_values=['NaN'])
                    df = data.where(pd.notna(data), None) # replace NaN value with None
                except:
                    print('file might be corrupted')

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

                # Create the INSERT query (will insert even if duplicate)
                query = f'''INSERT INTO tracker.{table_name}({columns}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING'''


                data_values = [tuple(row) for _, row in df.iterrows()]
                cur.executemany(query, data_values)
                # Insert data from the DataFrame
                # for _, row in df.iterrows():
                #     #print(row)
                #     cur.execute(query, tuple(row))
                    
                connection.commit()
            
                print('trackers upload success')

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cur.close()
            connection.close()
            print("PostgreSQL connection is closed")

                
if __name__ == "__main__":
    path = resource_path('tracker_postgresql')
    insert_tracker_data_to_pgdb(path,file_name='Analytical Experiment Tracker.csv',table_name='analytical_tracker')

