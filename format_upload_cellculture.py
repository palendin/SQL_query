import pandas as pd
import os, sys
import numpy as np
import psycopg2
from psycopg2 import Error
import shutil
import gspread as gs
import json
import traceback
from tools_and_functions.insert_tissue_data_to_pgdb import insert_tissue_data_to_pgdb
from tools_and_functions.insert_scalex_data_to_pgdb import insert_scalex_csv_data_to_pgdb

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

    # upload trend data
    scalex_trend_processing(root_directory, archive_directory)

    # upload excel data
    for folder_name in os.listdir(root_directory):
        if "CC" in folder_name: 
            folder_path = os.path.join(root_directory, folder_name)

            # name for each tab in the excel file. This is also the table name in postgresql
            sheet_names = ['run_detail', 'run_parameter','sample_plan','seed_operation','process_values','feed_operation',
                           'media_sampling','fresh_media_sampling','biopsy_sampling','hide_harvest','run_deviation', 'flex2_id_conversion','metabolite_calc']

            # used for re-arranging cols, assuming they match cols in file
            column_order_list = {
                'run_detail_column_order' : ['experiment_id','vessel_type','run_description','vessel_number','run_id','scaffold_id',
                                             'vial_id','culture_duration_days','media_recipe','media_key','Incubator','start_date','end_date','hide_id'],
                'run_parameter_column_order' : ['run_id','target_working_volume_ml','target_seed_area_cm2','target_seed_density_cells_per_cm2',
                                                'target_seed_number','temperature_SP_C','dO2_SP','CO2_SP','O2_SP','pH_SP',
                                                'rocking_hz_SP','rocking_angle_SP','feed_rate_mlpm_SP','outlet_rate_mlpm_SP',
                                                'vessel_pressure_psi_SP','actuator_wait_mins','feed_delay','rest_time_hr',
                                                'stirr_init_rpm','stirr_final_rpm','init_air_flow_mlpm','final_air_flow_mlpm','recirculation_rate_mlpm','process_mode'],
                'sample_plan_column_order' : ['run_id','sampling_ETT_day','media_sample','biopsy','feed','monitor','hide_id','feed_id','sample_id','biopsy_id','sampling_ETT_hr'],
                'seed_operation_column_order' : ['run_id','seed_volume_ml','seed_concentration_cells_per_ml','seed_number','seed_date','flood_time_hrs',
                                                 'media_id','media_volume_ml','rocking_start_time','operator','comment'],
                'process_values_column_order' : ['run_id','monitor_date','working_volume_ml','temperature_C','dO2','CO2','O2','pH','rocking_hz',
                                                 'rocking_angle','feed_rate_mlpm','outlet_rate_mlpm','vessel_pressure_psi','stirr_rpm','air_flow_mlpm','tank_weight_g',
                                                 'base_weight_g','acid_weight_g','feed_weight_g','feed_change_weight_g','waste_weight_g','waste_change_weight_g','offline_pH','ett_day'],
                'feed_operation_column_order' : ['feed_id','feed_date','media_id','media_exchange_volume_ml','time_out','time_in','operator','comment','ett_day'],
                'media_sampling_column_order' : ['sample_id','sample_date','operator','comment'],
                'fresh_media_sampling_column_order' : ['experiment_id','sample_id','sampling_ETT_day','sample_date','operator','comment','media_key'],
                'biopsy_sampling_column_order' : ['biopsy_id','biopsy_date','biopsy_purpose','biopsy_diameter_mm','num_biopsy_taken','storage_location','operator','comment'],
                'hide_harvest_column_order' : ['run_id','harvest_date','wet_weight_g','thickness_1_mm','thickness_2_mm','thickness_3_mm','thickness_4_mm',
                                               'thickness_5_mm','thickness_6_mm','avg_thickness_mm','mechanical_strength','fiber_protrusion',
                                               'surface_smoothness','operator','comment'],
                'run_deviation_column_order' : ['run_id','deviation','comments'],
                'flex2_id_conversion_column_order' : ['flex2_id','sample_id'],
                'metabolite_calc_column_order' : ['experiment_id',	'run_id',	'sampling_ett_day',	'sample_id',	'sample_date',	'pH',	'gln_mmol_per_l',	'gluc_g_per_l',	
                                                  'glu_mmol_per_l',	'nh4_mmol_per_l',	'lac_g_per_l',	'tank_volume_l',	'exchange_volume_l',	'fresh_gln_mmol_per_l',	
                                                  'fresh_gluc_g_per_l',	'fresh_glu_mmol_per_l',	'fresh_nh4_mmol_per_l',	'fresh_lac_g_per_l',	'res_gln_mmol_per_l',	'res_gluc_g_per_l',	
                                                  'res_glu_mmol_per_l',	'res_nh4_mmol_per_l',	'res_lac_g_per_l',	'exchange_vol_l',	'interval_gln_mmol_per_l',	'interval_gluc_g_per_l',	
                                                  'interval_glu_mmol_per_l',	'interval_nh4_mmol_per_l',	'interval_lac_g_per_l',	'res_interval_gln_mmol_per_l',	'res_interval_gluc_g_per_l',
                                                    'res_interval_glu_mmol_per_l',	'res_interval_nh4_mmol_per_l',	'res_interval_lac_g_per_l',	'cum_gln_mmol_per_l',	
                                                    'cum_gluc_g_per_l',	'cum_glu_mmol_per_l',	'cum_nh4_mmol_per_l',	'cum_lac_g_per_l',	'res_cum_gln_mmol_per_l',	
                                                    'res_cum_gluc_g_per_l',	'res_cum_glu_mmol_per_l',	'res_cum_nh4_mmol_per_l',	'res_cum_lac_g_per_l',	'total_gln_mmol_per_l',	
                                                    'total_gluc_g_per_l',	'total_glu_mmol_per_l',	'total_nh4_mmol_per_l',	'total_lac_g_per_l',	'total_gln_mmol',	
                                                    'total_gluc_g',	'total_glu_mmol',	'total_nh4_mmol',	'total_lac_g']
                }
            
            arranged_columns_list = list(column_order_list.values())
            
            # for uploading individually selected tables
            # sheet_names = ['process_values']
            # arranged_columns_list = [column_order_list['metabolite_calc_column_order']]
            # print(arranged_columns_list)
            
            # read all relevant sheets, assuming the excel file name is same as folder name
            try:
                df = pd.read_excel(folder_path+'/' + f'{folder_name}.xlsx',engine='openpyxl', sheet_name=sheet_names)

                for i, sheet in enumerate(sheet_names):
                    # read each sheet, remove empty rows
                    if i == 7: #fresh_media_sampling has additional rows that we dont need
                        data = df[sheet].iloc[:,0:7]
                    else:
                        #continue
                        data = df[sheet]
                    
                    data = data.replace("-",np.nan)
                    
                    data.replace({pd.NaT: None}, inplace=True) #replace NaT with None
                    #data = data.where(pd.notna(data),None) # df.where replaces NaN with None
                    data.replace({np.nan: None}, inplace=True)
                    data = data.dropna(axis=0,subset=[data.columns[0]])
                    
                    # remove rows that is nan in either 1st or 2nd column
                    nan_rows = data.iloc[:, [0, 1]].isna().any(axis=1)
                    data = data[~nan_rows]

                    # re-order columns (edit column order if needed)
                    data = data[arranged_columns_list[i]] # this should also only show the column that I need
        
                    # upload
                    print(f'uploading sheet {sheet}')
                    insert_tissue_data_to_pgdb(data=data,table=sheet)

                # move CC folder to archive after uploading
                shutil.move(folder_path, archive_directory)
            except:
                print(traceback.format_exc())
                exit()
        else:
            print('continuing')
            continue # continue to loop through folder
    
    
# def insert_column_name(df, **columns_and_positions):
#     column_list = df.columns
#     for column, position in columns_and_positions.items():
#         print(column,position)
#         new_column = column_list.insert(position, column)
       
#     return new_column

def scalex_trend_processing(root_directory, archive_directory):

    column_names = ['experiment_id','run_id','Time','time_hr','pH Acid(0) - Setpoint', 'pH Alkali(1) - Setpoint',	'dO2(2) - Setpoint','Temperature(3) - Setpoint','Temperature Jacket(4) - Setpoint',	'Heater(54) - State','Heater(54) - Value',
                    'PT-100 Bio(8) - State','PT-100 Bio(8) - Value','PT-100 Jacket(9) - State',	'PT-100 Jacket(9) - Value','4-20mA pH Temperature(12) - State','4-20mA pH Temperature(12) - Value',	
                    '4-20mA pH(13) - State','4-20mA pH(13) - Value','4-20mA dO2 Temperature(14) - State','4-20mA dO2 Temperature(14) - Value','Gas Air(45) - State','Gas Air(45) - Value','Gas O2(46) - State',	
                    'Gas O2(46) - Value','Gas CO2(47) - State',	'Gas CO2(47) - Value','MFC Air Value(0) - State','MFC Air Value(0) - Value','Base In (LS14)(66) - State','Base In (LS14)(66) - Value',
                    'Recirculation IN (LS16)(67) - State','Recirculation IN (LS16)(67) - Value','Recirculation OUT (LS16)(68) - State','Recirculation OUT (LS16)(68) - Value','4-20mA dO2 (15) - State',
                    '4-20mA dO2 (15) - Value','MFC Air Cmd(18) - State','MFC Air Cmd(18) - Value','Media In / Sampling (LS25)(69) - State','Media In / Sampling (LS25)(69) - Value']
  
    for folder_name in os.listdir(root_directory):

        if "CC" in folder_name:
            folder_path = os.path.join(root_directory, folder_name)
            file_list = os.listdir(folder_path)

            #DCU_file = f'{folder_name} DCU Data.csv'
            for f in file_list:
                if "DCU" in f and f.endswith('.csv'):
                    df = pd.read_csv(folder_path + '/' + f).iloc[1:,:]
                    df.insert(0, 'experiment_id', folder_name)
    
                    # extract runid from file name
                    file_name = f.split(' ')

                    run_id = [runid for runid in file_name if 'CC' in runid]
                    print(f'run id is {run_id}')
                    
                    df.insert(1,'run_id',run_id[0])

                    # convert datetime with timezone to pandas datetime
                    datetime = pd.to_datetime(df['Time']) 
                    time_hr = (datetime - datetime.iloc[0]).dt.total_seconds()/3600 #converts time difference to hours. ".dt is accessor to get components such as year, month out of the datetime value"
                    df.insert(3,'time_hr',time_hr)

                    df = df[column_names]
                    # for i, column in enumerate(df.columns):
                    #     df.rename(columns={column:column_names[i]}, inplace=True)
                    
                    rows_to_upload = len(df)

                    chunk_size = 1000
                    start = 0
                    end = len(df)
                    upload = input(f'total of {rows_to_upload} rows, uploading from {start} to {end}, (y/n)')
                    if upload == 'y':

                        print('starting to upload')

                        while end <= rows_to_upload:
                            
                            start, end = (start, start+chunk_size)
                            
                            # dataframe to upload
                            df_subset = df.iloc[start:end,:]
                    
                            print(f'uploading row {start} to {end}')
                            
                            #upload dataframe
                            insert_scalex_csv_data_to_pgdb(df_subset,table='scalex_hydro')

                            start = end
                    else:
                        exit()
    

if __name__ == "__main__":
    path = resource_path('Tissue')
    archive = resource_path('Tissue/archive')
    tissue_production_processing(root_directory=path, archive_directory=archive)
    #scalex_trend_processing(path,archive)



    # maybe i can implmeent this through looping the commit. 
    # since df = df.iloc[16000:18847] ignores the last column, loop below might work
    # rows_to_upload = 54
    # chunk_size = 10
    # start = 0
    # end = 0
    # while end <= rows_to_upload:
        
    #     start, end = (start, start+chunk_size)
    #     print(start,end)
    #     start = end






      # run_detail_column_order = ['experiment_id','vessel_type','run_description','vessel_number','run_id','scaffold_id','vial_id','culture_duration_days','media_recipe','media_key','Incubator','start_date','end_date','hide_id']
            # run_parameter_column_order = ['run_id','target_working_volume_ml','target_seed_area_cm2','target_seed_density_cells_per_cm2','target_seed_number','temperature_SP_C','CO2_SP','O2_SP','pCO2_SP','pO2_SP','pH_SP','rocking_hz_SP','rocking_angle_SP','feed_rate_mlpm_SP','outlet_rate_mlpm_SP','vessel_pressure_psi_SP','actuator_wait_mins','feed_delay','rest_time_hr','stirr_init_rpm','stirr_final_rpm','init_air_flow_mlpm','final_air_flow_mlpm','recirculation_rate_mlpm','process_mode']
            # sample_plan_column_order = ['run_id','sampling_ETT_day','media_sample','biopsy','feed','monitor','hide_id','feed_id','sample_id','biopsy_id']
            # seed_operation_column_order = ['run_id','seed_volume_ml','concentration_cells_per_ml','seed_number','seed_date','flood_time_hrs','media_id','media_volume_ml','rocking_start_time','operator','comment']
            # process_values_column_order = ['run_id','monitor_date','volume_ml','temperature_C','CO2','O2','pCO2','pO2','pH','rocking_hz','rocking_angle','feed_rate_mlpm','outlet_rate_mlpm','vessel_pressure_psi','stirr_rpm','air_flow_mlpm']
            # feed_operation_column_order = ['feed_id','feed_date','media_id','media_exchange_volume_ml','time_out','time_in','operator','comment']
            # media_sampling_column_order = ['sample_id','sample_date','operator','comment']
            # fresh_media_sampling_column_order = ['experiment_id','sample_id','sampling_ETT_day','sample_date','operator','comment','media_key']
            # biopsy_sampling_column_order = ['biopsy_id','biopsy_date','biopsy_purpose','biopsy_diameter_mm','num_biopsy_taken','storage_location','operator','comment']
            # hide_harvest_column_order = ['run_id','harvest_date','wet_weight_g','thickness_1_mm','thickness_2_mm','thickness_3_mm','thickness_4_mm','thickness_5_mm','thickness_6_mm','avg_thickness_mm','mechanical_strength','fiber_protrusion','surface_smoothness','operator','comment']
            # run_deviation_column_order = ['run_id','deviation','comments']
            # flex2_id_conversion_column_order = ['flex2_id','sample_id']

            # arranged_columns_list = [run_detail_column_order,run_parameter_column_order,sample_plan_column_order,seed_operation_column_order,
            #                          process_values_column_order,feed_operation_column_order, media_sampling_column_order,
            #                          fresh_media_sampling_column_order,biopsy_sampling_column_order,hide_harvest_column_order,run_deviation_column_order, flex2_id_conversion_column_order]
            