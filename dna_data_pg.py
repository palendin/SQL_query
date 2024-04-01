import pandas as pd
import os
import os, sys
import warnings
from psycopg2 import Error
import json
import shutil
import gspread as gs
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed
from tools_and_functions.insert_hp_data_to_pgdb import insert_hp_csv_data_to_pgdb
from tools_and_functions.read_gsheet import read_gsheet
import numpy as np
from time import sleep

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


# insert csv file from g-drive file by file into postgres
def process_dna_data_and_insert_to_pg(root_directory):
 
    # file names to look for
    file_names = ['combined_raw_data.csv','averaged_data.csv']

    # table names in postgres
    table_list = ['dna_raw','dna_avg']

    # rename some of the columns

    #define columns orders
    dna_raw_order = ['dna_sid', 'experiment_id',
                                'sample_id', 'sample_type', 'description', 'sample_replicate',
                                'sample_diameter_mm', 'digestion_volume_ul',
                                'digested_sample_volume_ul', 'buffer_volume_ul', 'dilution_factor',
                                'assay_volume_ul', 'std_conc_ng_per_well', 'biopsy_region',
                                'culture_duration_days', 'master_well_plate_location', 'abs',
                                'sheet_name', 'location', 'ng_per_well', 'ug_per_ml', 'ug_per_biopsy',
                                'ug_per_cm2', 'r_squared','data_check','avg_ug_per_cm2', 'avg_ug_per_cm2_std']
    
    avg_dna_order = ['dna_sid', 'experiment_id',
                            'sample_id', 'sample_type', 'description', 'sample_diameter_mm',
                            'digestion_volume_ul', 'digested_sample_volume_ul', 'buffer_volume_ul',
                            'dilution_factor', 'assay_volume_ul','biopsy_region', 'culture_duration_days', 'master_well_plate_location','avg_ug_per_cm2', 'avg_ug_per_cm2_std']
    
    # put rename and order in a list for forloop
    column_order = [dna_raw_order,avg_dna_order]

    # read saved experiment upload data
    gc = gs.service_account(filename='/Users/wayne/Documents/Programming/vscode/API/Google_API/service_account.json')
    sh = gc.open_by_key('1TtqClIkvNCqJMoRZ6wkq-PPwwl0trO3SqGbIdAD9d6k')
    worksheet = sh.worksheet('dna_exp_tracker')

    # get experiment id and status from experiment tracker
    tracker_id, tracker_sheet = ['1MOuCpubEbwf7QE_tU5IfL_pqFwtDukOqH5o_9Z0WnHM','Tracker']
    tracker_df = read_gsheet(tracker_id, tracker_sheet).replace('',np.nan, regex=True)
    tracker_df = tracker_df.where(pd.notna(tracker_df), None) # replace NaN value with None
    tracker_df = tracker_df[['experiment_id','status']]
    
    # get processed experiment id from gsheet that contains uploaded experiment names
    saved_exp, saved_tracker_sheet = ['1TtqClIkvNCqJMoRZ6wkq-PPwwl0trO3SqGbIdAD9d6k','dna_exp_tracker']
    saved_exp_df = read_gsheet(saved_exp, saved_tracker_sheet).replace('',np.nan, regex=True)
    saved_exp_df = saved_exp_df.where(pd.notna(saved_exp_df), None) # replace NaN value with None
    saved_exp_list = saved_exp_df.iloc[:,0].to_list()
    
    # upload_list = pd.DataFrame() # gspread API has user request limit of 60/min, but can upload row by row still with sleep function

    for experiment in tracker_df.values:
        if "DNA" in experiment[0]:
            # compare each experiment in the tracker to saved list
            if experiment[0] not in saved_exp_list and (experiment[1] == 'complete' or experiment[1] == 'deprecated'):
                
                # append experiment info to dataframe
                #upload_list = upload_list.append(pd.Series(list(experiment)), ignore_index = True)

                # get an experiment folder path that hasnt been uploaded. Root directory is where experiment folders lie
                experiment_folder_path = os.path.join(root_directory,experiment[0])
                
                for i,file in enumerate(file_names):
                    file_path = os.path.join(experiment_folder_path, file)
                    
                    # check if file exist, if it does, append the content to list
                    if os.path.exists(file_path):
                        data = pd.read_csv(file_path)
                    
                        df = pd.DataFrame(data)

                        # reorder columns
                        df = df[column_order[i]]

                        # replace NaN with None
                        data = df.where(pd.notna(df), None)

                        # insert to postgres (can use the same upload script)
                        print(f'uploading {experiment} to postgres')
                        insert_hp_csv_data_to_pgdb(data,table_list[i])

                    else:
                        print('exp is complete but file is missing, check folder!') 

                # add experiment to spreadsheet to keep track
                worksheet.append_row(list(experiment))
                print(f'appended {experiment} to google sheet')
                sleep(2)

        else:
            continue
        
    print('hydroxyproline upload complete')


                
if __name__ == "__main__":
    # path = resource_path('HP_assay') #where the experiment folders are
    # archive_path = resource_path('HP_assay/archive')
    # process_hp_data_and_insert_to_pg(path,archive_path)

    dna_folder_path  = '/Users/wayne/Library/CloudStorage/GoogleDrive-wayne@vitrolabsinc.com/Shared drives/R&PD Team/Vitrolab Experimental Data (Trained User Only)/Analytical/DNA'
    process_dna_data_and_insert_to_pg(dna_folder_path)

