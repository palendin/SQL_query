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
import traceback
import logging


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
def process_dw_data_and_insert_to_pg(root_directory):
    
   # Set up logging
    log_print_file_path = 'logs/dw_print.log'
    logger_print = print_logging(log_print_file_path)

    # file names to look for
    file_names = ['sample_layout.gsheet']

    # table names in postgres
    table_list = ['dry_weight']

    # # rename some of the columns (note rename/column order is now for exp starting at HP86+)
    # raw_data_columns_rename = {'experiment_ID':'experiment_id','sample_ID':'sample_id','hide_ID':'biopsy_id','biomaterial_ID':'biomaterial_id','digest volume ul':'digestion_volume_ul','digest sample volume ul':'assay_volume_ul'}
    # biopsy_columns_rename = {'experiment_ID':'experiment_id','hide_ID':'biopsy_id','biomaterial_ID':'biomaterial_id','sample_ID':'sample_id'}

    # #define columns orders
    # raw_data_column_order = ['experiment_id','sample_id','sample_type','sample_state','sample_lot','biopsy_id','culture_date','biopsy_replicate','biopsy_diameter_mm',
    #                 'digestion_volume_ul','dilution_factor','assay_volume_ul','loaded_weight1_mg','loaded_weight2_mg','tube_weight1_mg','tube_weight2_mg','operator',
    #                 'std_conc_ug_per_well','media_type','biomaterial_id','reaction_date','abs','sheet_name','location','data check','normalized_abs','r_squared',
    #                 'net weight mg','ug/well','mg/ml','mg/biopsy','mg/cm2','avg mg/biopsy', 'mg/biopsy std', 'avg mg/cm2','mg/cm2 std', 'avg mg/ml', 'mg/ml std','HP_sid']
    
    # biopsy_column_order = ['experiment_id',	'biopsy_id','biomaterial_id','mg/biopsy mean','mg/biopsy std','mg/ml mean','mg/ml std',	
    #                        'mg/cm2 mean','mg/cm2 std','net weight mg','tissue areal density mg/cm2','sample_id', 'HP_sid']
    
    # # put rename and order in a list for forloop
    # column_rename = [raw_data_columns_rename, biopsy_columns_rename]
    # column_order = [raw_data_column_order,biopsy_column_order]

    # read saved experiment upload data
    gc = gs.service_account(filename='/Users/wayne/Documents/Programming/vscode/API/Google_API/service_account.json')
    sh = gc.open_by_key('1TtqClIkvNCqJMoRZ6wkq-PPwwl0trO3SqGbIdAD9d6k')
    worksheet = sh.worksheet('hp_exp_tracker')

    # get experiment id and status from experiment tracker
    tracker_id, tracker_sheet = ['1MOuCpubEbwf7QE_tU5IfL_pqFwtDukOqH5o_9Z0WnHM','Tracker']
    tracker_df = read_gsheet(tracker_id, tracker_sheet).replace('',np.nan, regex=True)
    tracker_df = tracker_df.where(pd.notna(tracker_df), None) # replace NaN value with None
    tracker_df = tracker_df[['experiment_id','status']]
    
    # get processed experiment id from gsheet that contains uploaded experiment names
    saved_exp, saved_tracker_sheet = ['1TtqClIkvNCqJMoRZ6wkq-PPwwl0trO3SqGbIdAD9d6k','dryweight_tracker']
    saved_exp_df = read_gsheet(saved_exp, saved_tracker_sheet).replace('',np.nan, regex=True)
    saved_exp_df = saved_exp_df.where(pd.notna(saved_exp_df), None) # replace NaN value with None
    saved_exp_list = saved_exp_df.iloc[:,0].to_list()

    for experiment in tracker_df.values:
        if "DW" in experiment[0]:
            # compare each experiment in the tracker to saved list
            if experiment[0] not in saved_exp_list and (experiment[1] == 'complete' or experiment[1] == 'deprecated'):

                # get an experiment folder path that hasnt been uploaded. Root directory is where experiment folders lie
                experiment_folder_path = os.path.join(root_directory,experiment[0])
                
                for i,file in enumerate(file_names):
                    file_path = os.path.join(experiment_folder_path, file)
                    print(file_path)
                    
                    # check if file exist, if it does, append the content to list
                    # if os.path.exists(file_path):
                          
    #                     data = pd.read_csv(file_path)
                    
    #                     df = pd.DataFrame(data)
            
    #                     # rename some columns for consistency
    #                     df = df.rename(columns=column_rename[i])

    #                     # reorder columns
    #                     df = df[column_order[i]]

    #                     # replace NaN with None
    #                     #data = df.where(pd.notna(df), None) # this no longer works in later version of pandas
    #                     data = df.replace(np.nan,None)
            
    #                     # replace empty date or weird date with None
    #                     try:
    #                         data['culture_date'] = data['culture_date'].replace('01-00-1900',0).replace([0],[None])
    #                         data['reaction_date'] = data['reaction_date'].replace('01-00-1900',0).replace([0],[None])
    #                     except:
    #                         pass
                        
    #                     # insert to postgres
    #                     try:
    #                         logger_print.info(f'uploading experiment {experiment}, table {table_list[i]} to postgres')
    #                         insert_hp_csv_data_to_pgdb(data,table_list[i])
    #                     except:
    #                         traceback_msg = traceback.format_exc()
    #                         raise ValueError(traceback_msg)

    #                 else:
    #                     logger_print.info(f'{experiment} has file is missing, check folder {file_path}!')
    #                     continue

    #             # add experiment to spreadsheet to keep track
    #             worksheet.append_row(list(experiment))
    #             logger_print.info(f'appended {experiment} to google sheet')
    #             sleep(2)
    #     else:
    #         continue
        
    # print('hydroxyproline upload complete')

def setup_logging(log_file_path):
    # Create the logs directory if it does not exist
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    # Set up logging for errors
    logging.basicConfig(
        level=logging.ERROR,  # Log only errors and above
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler(sys.stdout)  # optional arg. Log to console (stdout)
        ]
    )
    logger_error = logging.getLogger('error_logger')
    logger_error.propagate = False  # Disable propagation to root logger

    return logger_error


def print_logging(log_print_path):
     # Create the logs directory if it does not exist
    os.makedirs(os.path.dirname(log_print_path), exist_ok=True)
    
    # Create a FileHandler to log to the specified file
    handler_print = logging.FileHandler(log_print_path)

    # Configure the format of log messages
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler_print.setFormatter(formatter)

    # Create a logger and add the FileHandler to it
    logger = logging.getLogger('print_logger')
    logger.setLevel(logging.INFO)  # Set the logging level to INFO
    logger.addHandler(handler_print)


    return logger

                
if __name__ == "__main__":
    # path = resource_path('HP_assay') #where the experiment folders are
    # archive_path = resource_path('HP_assay/archive')
    # process_hp_data_and_insert_to_pg(path,archive_path)
    
    # Set up logging
    log_error_file_path = 'logs/hp_error.log'

    # Set up logging
    logger_error = setup_logging(log_error_file_path)

    hp_folder_path  = '/Users/wayne/Library/CloudStorage/GoogleDrive-wayne@vitrolabsinc.com/Shared drives/R&PD Team/Vitrolab Experimental Data (Trained User Only)/Analytical/hydroxyproline'
    try:
        process_dw_data_and_insert_to_pg(hp_folder_path)
    except Exception as e:
        # this will log the msg as well as any exception error within the functions
        logger_error.exception(f"An error occurred while processing and inserting data")
        sys.exit(1)
