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
from tools_and_functions.insert_hp_data_to_pgdb import insert_hp_csv_data_to_pgdb

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

# insert csv file by file into postgres
def process_hp_data_and_insert_to_pg(root_directory, archive_path):
    #print(root_directory)

    # file names to look for
    file_names = ['combined_raw_data.csv','biopsy_result.csv']

    # table names in postgres
    table_list = ['hydroxyproline_raw','biopsy_result']

    # define some to rename columns
    raw_data_columns_rename = {'experiment_ID':'experiment_id','sample_ID':'sample_id','hide_ID':'biopsy_id','biomaterial_ID':'biomaterial_id','digest volume ul':'digestion_volume_ul','digest sample volume ul':'assay_volume_ul'}
    biopsy_columns_rename = {'experiment_ID':'experiment_id','hide_ID':'biopsy_id','biomaterial_ID':'biomaterial_id'}

    #define columns orders
    raw_data_column_order = ['experiment_id','sample_id','sample_type','sample_state','sample_lot','biopsy_id','culture_date','biopsy_replicate','biopsy_diameter_mm',
                    'digestion_volume_ul','dilution_factor','assay_volume_ul','loaded_weight1_mg','loaded_weight2_mg','tube_weight1_mg','tube_weight2_mg','operator',
                    'std_conc_ug_per_well','media_type','biomaterial_id','reaction_date','abs','sheet_name','location','data check','normalized_abs','r_squared',
                    'net weight mg','ug/well','mg/ml','mg/biopsy','mg/cm2']
    
    biopsy_column_order = ['experiment_id',	'biopsy_id','biomaterial_id','mg/biopsy mean','mg/biopsy std','mg/ml mean','mg/ml std',	
                           'mg/cm2 mean','mg/cm2 std','net weight mg','tissue areal density mg/cm2']
    
    # put rename and order in a list for forloop
    column_rename = [raw_data_columns_rename, biopsy_columns_rename]
    column_order = [raw_data_column_order,biopsy_column_order]

    # Loop through each subfolder in folder directory 
    for folder_name in os.listdir(root_directory):

        # if folder name is an experiment folder:
        if "HP" in folder_name:
            folder_path = os.path.join(root_directory, folder_name)
            # loop through the file names in the experiment folder
            for i,file in enumerate(file_names):
                file_path = os.path.join(folder_path, file)
                
                # check if file exist, if it does, append the content to list
                if os.path.exists(file_path):
                    data = pd.read_csv(folder_path + '/' + file)
                    df = pd.DataFrame(data)
        
                    # rename some columns for consistency
                    df = df.rename(columns=column_rename[i])

                    # reorder columns
                    df = df[column_order[i]]

                    # replace NaN with None
                    data = df.where(pd.notna(df), None)

                    # replace empty date with None
                    try:
                        data['reaction_date'] = data['reaction_date'].replace('01-00-1900',0).replace([0],[None])
                    except:
                        pass
                    
                    # insert to postgres
                    #insert_hp_csv_data_to_pgdb(data,table_list[i])

                else:
                    continue    
            
            # move folder to archive
            shutil.move(folder_path, archive_path)

        else:
            continue

# # combine HP combined raw and biopsy results csv files, each into one big csv. Then upload to postgresql
# def process_hp_data_and_insert_to_pg(root_directory, archive_path):
#     #print(root_directory)

#     data_list = [[],[]] #empty list for two sets of data since there are two different csv files
#     file_names = ['combined_raw_data.csv','biopsy_result.csv']
#     table_list = ['hydroxyproline_raw','biopsy_result']

#     # columns to rename if the column names are different
#     raw_data_columns_rename = {'experiment_ID':'experiment_id','sample_ID':'sample_id','hide_ID':'biopsy_id','biomaterial_ID':'biomaterial_id','digest volume ul':'digestion_volume_ul','digest sample volume ul':'assay_volume_ul'}
#     biopsy_columns_rename = {'experiment_ID':'experiment_id','hide_ID':'biopsy_id','biomaterial_ID':'biomaterial_id'}

#     # Loop through each subfolder in folder directory 
#     for folder_name in os.listdir(root_directory):
#         folder_path = os.path.join(root_directory, folder_name)

#         # if subfolder path exist
#         if os.path.isdir(folder_path):
#             print(f"Folder: {folder_path}")

#             # loop through the file names in the subfolder
#             for i,file in enumerate(file_names):
#                 if file == file_names[0]:
#                     rename_column = raw_data_columns_rename
#                 if file == file_names[1]:
#                     rename_column = biopsy_columns_rename

#                 file_path = os.path.join(folder_path, file)

#                 # check if file exist, if it does, append the content to list
#                 if os.path.exists(file_path):
#                     data = pd.read_csv(folder_path + '/' + file)
#                     df = pd.DataFrame(data)
        
#                     #rename somecolumns for consistency
#                     df = df.rename(columns=rename_column)

#                     if df is not None:               
#                         data_list[i].append(df)

#                     else:
#                         continue
#                 else:
#                     continue
    
#      #rename columns in desired order
#     raw_data_column_order = ['experiment_id','sample_id','sample_type','sample_state','sample_lot','biopsy_id','culture_date','biopsy_replicate','biopsy_diameter_mm',
#                     'digestion_volume_ul','dilution_factor','assay_volume_ul','loaded_weight1_mg','loaded_weight2_mg','tube_weight1_mg','tube_weight2_mg','operator',
#                     'std_conc_ug_per_well','media_type','biomaterial_id','reaction_date','abs','sheet_name','location','data check','normalized_abs','r_squared',
#                     'net weight mg','ug/well','mg/ml','mg/biopsy','mg/cm2']
    
#     biopsy_column_order = ['experiment_id',	'biopsy_id','biomaterial_id','mg/biopsy mean','mg/biopsy std','mg/ml mean','mg/ml std',	
#                            'mg/cm2 mean','mg/cm2 std','net weight mg','tissue areal density mg/cm2']

#     column_order = [raw_data_column_order,biopsy_column_order]
  
#     # insert the data from data_list into postgresql
#     for j, data in enumerate(data_list):
#         combined_data = pd.concat(data, axis= 0, ignore_index=True) #[data.columns]. this will create default index
#         combined_data = combined_data[column_order[j]] #.rename_axis('id')# rename default index to "id"
        
#         # insert into postgresql
#         insert_hp_csv_data_to_pgdb(combined_data,table_list[j])

#         # save them to respective folder
#         # if j == 0:
#         #     path = resource_path('hp_raw_postgresql')
#         # if j == 1:
#         #     path = resource_path('hp_biopsy_postgresql')
        
#         # combined_data.to_csv(path + '/' + file_names[j])

#     # move all folder that thats with the name "HP" to archive
#     for folder_name in os.listdir(root_directory):
#         if 'HP' in folder_name:
#             folder_path = os.path.join(root_directory, folder_name)
#             shutil.move(folder_path, archive_path)

                
if __name__ == "__main__":
    path = resource_path('HP_assay') #where the experiment folders are
    archive_path = resource_path('HP_assay/archive')
    process_hp_data_and_insert_to_pg(path,archive_path)

