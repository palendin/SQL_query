import pandas as pd
import numpy as np
import os, sys
import warnings
import psycopg2
from psycopg2 import Error
import json
from tenacity import retry, stop_after_attempt, wait_fixed
from tools_and_functions.read_gsheet import *

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)

    return path

# def insert_bm_sf_to_pgdb(root_directory, file_name, table_name):
    
#     try:
#         connection = psycopg2.connect(
#         host="34.134.210.165",
#         database="vitrolabs",
#         user="postgres",
#         password="Vitrolabs2023!",
#         port=5432)
        
#         cur = connection.cursor()
    
#         file_path = os.path.join(root_directory, file_name)
#         print(file_path)

#         bm_sf_sheet = pd.read_excel(file_path,engine='openpyxl',sheet_name=None) #skip the first row which is the indexes of the well

#         for i, sheet_name in enumerate(bm_sf_sheet):
#             #print(sheet_name)
#             df = bm_sf_sheet[sheet_name]
#             df = df.fillna(0).replace([0],[None])
#             df = df[df['id'].notna()] # get all rows that does not have null id
#              # Check if the table exists
#             query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)"
#             cur.execute(query, (table_name[i],))
#             table_exists = cur.fetchone()[0]

#             if table_exists:
#                 print(f"The table '{table_name[i]}' exists.")
#             else:
#                 print(f"The table '{table_name[i]}' does not exist.")
#                 raise Exception('create table in postgresql first with desired names. Make sure json names match them')


#             # column does not need mod, no mapping needed.
#             postgresql_columns = df.columns
#             # for col in df.columns:
#             #     postgresql_column_name = map.get(col, col)
#             #     postgresql_columns.append(postgresql_column_name)
        
#             # Generate the column names dynamically for postgresql query format
#             columns = ', '.join(postgresql_columns)
        
#             # Generate the placeholders for the VALUES clause based on the number of columns
#             placeholders = ', '.join(['%s'] * len(df.columns))

#             # Create the INSERT query (will insert even if duplicate, but conflict will dictates what it will do
#             query = f'''INSERT INTO biomaterial_scaffold.{table_name[i]}({columns}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING'''


#             data_values = [tuple(row) for _, row in df.iterrows()]
#             cur.executemany(query, data_values)
#             # data_values = [tuple(row) for _, row in df.iterrows()]
#             # cur.executemany(query, data_values)
#             # Insert data from the DataFrame
#             # for _, row in df.iterrows():
#             #     if(row['id']):
#             #         print(_,'inserted successfully')
#             #         cur.execute(query, tuple(row))
                
#             connection.commit()
#             print('biomaterial upload success')

#         # rows_to_upload = 50
#         # chunk_size = 10
#         # start=0
#         # end=0
#         # while end <= rows_to_upload:
            
#         #     start, end = (start, start+chunk_size)
#         #     print(start,end)
#         #     start = end
            

#     except (Exception, Error) as error:
#         print("Error while connecting to PostgreSQL", error)
#     finally:
#         if (connection):
#             cur.close()
#             connection.close()
#             print("PostgreSQL connection is closed")
    
def insert_bm_sf_to_pgdb(file_id, sheet_list, table_name, column_positions):
    
    try:
        connection = psycopg2.connect(
        host="34.134.210.165",
        database="vitrolabs",
        user="postgres",
        password="Vitrolabs2023!",
        port=5432)
        
        cur = connection.cursor()
        
        for i, sheet in enumerate(sheet_list):
            data = read_gsheet(file_id, sheet).replace('', np.nan, regex=True)
            df = data.where(pd.notna(data), None) # replace NaN value with None    

            df = df[df['id'].notna()].iloc[:,0:column_positions[i]] # get all rows that does not have null id
            #print(df.head())
            query = f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)"
            cur.execute(query, (table_name[i],))
            table_exists = cur.fetchone()[0]
        
            if table_exists:
                print(f"The table '{table_name[i]}' exists.")
            else:
                print(f"The table '{table_name[i]}' does not exist.")
                raise Exception('create table in postgresql first with desired names. Make sure json names match them')
            
            # column does not need mod, no mapping needed.
            postgresql_columns = df.columns
            # for col in df.columns:
            #     postgresql_column_name = map.get(col, col)
            #     postgresql_columns.append(postgresql_column_name)
        
            # Generate the column names dynamically for postgresql query format
            columns = ', '.join(postgresql_columns)
        
            # Generate the placeholders for the VALUES clause based on the number of columns
            placeholders = ', '.join(['%s'] * len(df.columns))

            # Create the INSERT query (will insert even if duplicate, but conflict will dictates what it will do
            query = f'''INSERT INTO biomaterial_scaffold.{table_name[i]}({columns}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING'''


            data_values = [tuple(row) for _, row in df.iterrows()]
            cur.executemany(query, data_values)
            # data_values = [tuple(row) for _, row in df.iterrows()]
            # cur.executemany(query, data_values)
            # Insert data from the DataFrame
            # for _, row in df.iterrows():
            #     if(row['id']):
            #         print(_,'inserted successfully')
            #         cur.execute(query, tuple(row))
                
            connection.commit()
            print('{} upload success'.format(sheet))

        # # rows_to_upload = 50
        # # chunk_size = 10
        # # start=0
        # # end=0
        # # while end <= rows_to_upload:
            
        # #     start, end = (start, start+chunk_size)
        # #     print(start,end)
        # #     start = end
            

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cur.close()
            connection.close()
            print("PostgreSQL connection is closed")

if __name__ == "__main__":
    #path = resource_path('biomaterial_scaffold_postgresql')
    #insert_bm_sf_to_pgdb(path,file_name='biomaterial_and_scaffold_prep.xlsx',table_name=['biomaterial','scaffold','form_factor','press_parameter','autoclave_specification'])

    file_id = '1-n2zwPWklDmYvsyYcuaSqdirkg1vnwAaMFXQvvDCyLc'
    sheet_list = ['biomaterial', 'scaffold', 'form factor', 'press parameter', 'autoclave specification'] #sheet list variable is read by the function read_gsheet
    table_name=['biomaterial','scaffold','form_factor','press_parameter','autoclave_specification']

    insert_bm_sf_to_pgdb(file_id, sheet_list, table_name)