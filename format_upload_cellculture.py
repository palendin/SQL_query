import pandas as pd
import os, sys
import psycopg2
from psycopg2 import Error
import shutil
import gspread as gs
import json
import traceback
from tools_and_functions.insert_tissue_data_to_pgdb import insert_tissue_data_to_pgdb

# define the path to be base path of the PC + the folder containing the data source
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)

    return path

# process -> append to g-sheet -> upload to postgresql
def tissue_production_processing(root_directory, archive_directory):
    for folder_name in os.listdir(root_directory):
        if "CC" in folder_name: 
            folder_path = os.path.join(root_directory, folder_name)

            # name for each tab in the excel file. This is also the table name in postgresql
            sheet_names = ['run_detail', 'run_parameter','sample_plan','seed_operation','process_values','feed_operation',
                           'media_sampling','fresh_media_sampling','biopsy_sampling','hide_harvest','run_deviation', 'flex2_id_conversion']
        
            # used for re-arranging cols, assuming they match cols in file
            run_detail_column_order = ['experiment_id','vessel_type','run_description','vessel_number','run_id','scaffold_id','vial_id','culture_duration_days','media_recipe','media_key','Incubator','start_date','end_date','hide_id']
            run_parameter_column_order = ['run_id','target_working_volume_ml','target_seed_area_cm2','target_seed_density_cells_per_cm2','target_seed_number','temperature_SP_C','CO2_SP','O2_SP','pCO2_SP','pO2_SP','pH_SP','rocking_hz_SP','rocking_angle_SP','feed_rate_mlpm_SP','outlet_rate_mlpm_SP','vessel_pressure_psi_SP','actuator_wait_mins','feed_delay','rest_time_hr','stirr_init_rpm','stirr_final_rpm','init_air_flow_mlpm','final_air_flow_mlpm','recirculation_rate_mlpm','process_mode']
            sample_plan_column_order = ['run_id','sampling_ETT_day','media_sample','biopsy','feed','monitor','hide_id','feed_id','sample_id','biopsy_id']
            seed_operation_column_order = ['run_id','seed_volume_ml','concentration_cells_per_ml','seed_number','seed_date','flood_time_hrs','media_id','media_volume_ml','rocking_start_time','operator','comment']
            process_values_column_order = ['run_id','monitor_date','volume_ml','temperature_C','CO2','O2','pCO2','pO2','pH','rocking_hz','rocking_angle','feed_rate_mlpm','outlet_rate_mlpm','vessel_pressure_psi','stirr_rpm','air_flow_mlpm']
            feed_operation_column_order = ['feed_id','feed_date','media_id','media_exchange_volume_ml','time_out','time_in','operator','comment']
            media_sampling_column_order = ['sample_id','sample_date','operator','comment']
            fresh_media_sampling_column_order = ['experiment_id','sample_id','sampling_ETT_day','sample_date','operator','comment','media_key']
            biopsy_sampling_column_order = ['biopsy_id','biopsy_date','biopsy_purpose','biopsy_diameter_mm','num_biopsy_taken','storage_location','operator','comment']
            hide_harvest_column_order = ['run_id','harvest_date','wet_weight_g','thickness_1_mm','thickness_2_mm','thickness_3_mm','thickness_4_mm','thickness_5_mm','thickness_6_mm','avg_thickness_mm','mechanical_strength','fiber_protrusion','surface_smoothness','operator','comment']
            run_deviation_column_order = ['run_id','deviation','comments']
            flex2_id_conversion_column_order = ['flex2_id','sample_id']

            arranged_columns_list = [run_detail_column_order,run_parameter_column_order,sample_plan_column_order,seed_operation_column_order,
                                     process_values_column_order,feed_operation_column_order, media_sampling_column_order,
                                     fresh_media_sampling_column_order,biopsy_sampling_column_order,hide_harvest_column_order,run_deviation_column_order, flex2_id_conversion_column_order]
            
            # sheet_names = ['run_parameter','process_values']
            # arranged_columns_list = [run_parameter_column_order, process_values_column_order]
            
            # read all relevant sheets, assuming the excel file name is same as folder name
            df = pd.read_excel(folder_path+'/' + f'{folder_name}.xlsx',engine='openpyxl', sheet_name=sheet_names)

            for i, sheet in enumerate(sheet_names):
                # read each sheet, remove empty rows
                if i == 7: #fresh_media_sampling has additional rows that we dont need
                    data = df[sheet].iloc[:,0:7]
                else:
                    #continue
                    data = df[sheet]
                
                data = data.where(pd.notna(data),None) # df.where replaces NaN with None
                data = data.dropna(axis=0,subset=[data.columns[0]])
                print(data)
                # re-order columns (edit column order if needed)
                data = data[arranged_columns_list[i]]
                
                # upload
                insert_tissue_data_to_pgdb(data=data,table=sheet)

            # move CC folder to archive after uploading
            shutil.move(folder_path, archive_directory)
        

        else:
            print('continuing')
            continue # continue to loop through folder
            
# def insert_column_name(df, **columns_and_positions):
#     column_list = df.columns
#     for column, position in columns_and_positions.items():
#         print(column,position)
#         new_column = column_list.insert(position, column)
       
#     return new_column

if __name__ == "__main__":
    path = resource_path('Tissue')
    archive = resource_path('Tissue/archive')
    tissue_production_processing(root_directory=path, archive_directory=archive)