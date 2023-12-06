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

# loop through each subfolder and upload specified csv file to postgresql database table
def insert_csv_data_to_pgdb(root_directory, file_name, table_name):

    # json file maps csv column names to postgresql column names
    with open('hp_assay_map.json', 'r') as file:
        hp_assay_column_mapping = json.load(file)

    # connect to db
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="sample_database",
            user="postgres",
            password="Vitrolabs2023",
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
                remembered_folders_file = 'processed_files.txt'
                file_path = os.path.join(os.path.dirname(__file__), 'processed_files.txt')
                if not os.path.exists(file_path):
                    with open(file_path, 'w'):
                        pass
                else:
                    pass

                # with open(remembered_folders_file, 'r+') as f:
                #     if folder_name not in f.read():
                #         f.write(folder_name + ',')     
                #         pass
                #     else:
                #         continue
              
                #file_name = 'combined_raw_data.csv'
                data = pd.read_csv(folder_path + '/' + file_name, na_values=['NaN'])

                # Replace NaN values with None
                df = data.where(pd.notna(data), None)
                #df = df.iloc[0:,2:]

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
                    postgresql_column_name = hp_assay_column_mapping.get(col, col)
                    postgresql_columns.append(postgresql_column_name)
             
                # Generate the column names dynamically
                columns = ', '.join(postgresql_columns)
            
                # Generate the placeholders for the VALUES clause based on the number of columns
                placeholders = ', '.join(['%s'] * len(df.columns))

                # Create the INSERT query (will insert even if duplicate)
                query = f'''INSERT INTO pizza_schema.{table_name}({columns}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING'''

                # Insert data from the DataFrame
                for _, row in df.iterrows():
                    #print(row)
                    cur.execute(query, tuple(row))
                    
                connection.commit()
            
                # cur.execute(query, df)
                # connection.commit()
                print('success')
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cur.close()
            connection.close()
            print("PostgreSQL connection is closed")


# combine HP combined raw and biopsy results csv files, each into one big csv 
# when the experiment folder listed in order, the insertion to csv is not in order, but its always the same order. Can take advantage of this and use unique index for insertion purposes
def combine_to_csv_from_folders(root_directory):
    #print(root_directory)

    data_list = [[],[]] #empty list for two sets of data since there are two different csv files
    file_names = ['combined_raw_data.csv','biopsy_result.csv']

    # columns to rename if the column names are different
    raw_data_columns_rename = {'experiment_ID':'experiment_id','sample_ID':'sample_id','hide_ID':'biopsy_id','biomaterial_ID':'biomaterial_id','digest volume ul':'digestion_volume_ul','digest sample volume ul':'assay_volume_ul'}
    biopsy_columns_rename = {'experiment_ID':'experiment_id','hide_ID':'biopsy_id','biomaterial_ID':'biomaterial_id'}

    # Loop through each subfolder in folder directory 
    for folder_name in os.listdir(root_directory):
        folder_path = os.path.join(root_directory, folder_name)

        # if subfolder path exist
        if os.path.isdir(folder_path):
            print(f"Folder: {folder_path}")

            # loop through the file names in the subfolder
            for i,file in enumerate(file_names):
                if file == file_names[0]:
                    rename_column = raw_data_columns_rename
                if file == file_names[1]:
                    rename_column = biopsy_columns_rename

                file_path = os.path.join(folder_path, file)

                # check if file exist, if it does, append the content to list
                if os.path.exists(file_path):
                    data = pd.read_csv(folder_path + '/' + file)
                    df = pd.DataFrame(data)
        
                    #rename somecolumns for consistency
                    df = df.rename(columns=rename_column)

                    if df is not None:               
                        data_list[i].append(df)

                    else:
                        continue
                else:
                    continue
    
     #rename columns in desired order
    raw_data_column_order = ['experiment_id','sample_id','sample_type','sample_state','sample_lot','biopsy_id','culture_date','biopsy_replicate','biopsy_diameter_mm',
                    'digestion_volume_ul','dilution_factor','assay_volume_ul','loaded_weight1_mg','loaded_weight2_mg','tube_weight1_mg','tube_weight2_mg','operator',
                    'std_conc_ug_per_well','media_type','biomaterial_id','reaction_date','abs','sheet_name','location','data check','normalized_abs','r_squared',
                    'net weight mg','ug/well','mg/ml','mg/biopsy','mg/cm2']
    
    biopsy_column_order = ['experiment_id',	'biopsy_id','biomaterial_id','mg/biopsy mean','mg/biopsy std','mg/ml mean','mg/ml std',	
                           'mg/cm2 mean','mg/cm2 std','net weight mg','tissue areal density mg/cm2']

    column_order = [raw_data_column_order,biopsy_column_order]
  
    # order the data and save to csv
    for j, data in enumerate(data_list):
        combined_data = pd.concat(data, axis= 0, ignore_index=True) #[data.columns]. this will create default index
        combined_data = combined_data[column_order[j]].rename_axis('id') # rename default index to "id"
        combined_data.to_csv(f'test{j}.csv')

    # combined_data = data[column_order].rename_axis('id')
    # combined_data.to_csv(f'test{i}.csv')


def excel_to_csv_from_folders(root_directory):
    data_list = []
    for folder_name in os.listdir(root_directory):
        folder_path = os.path.join(root_directory, folder_name)
        # check if subfolder
        if os.path.isdir(folder_path):
            print(f"Folder: {folder_path}")
            file_path = os.path.join(folder_path, 'combined_raw_data.csv')
            if os.path.exists(file_path):
                continue
                
if __name__ == "__main__":
    path = resource_path('HP_assay')
    combine_to_csv_from_folders(path)
    #insert_csv_data_to_pgdb(path,file_name='combined_raw_data.csv',table_name='hp_assay')

