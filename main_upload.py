from bm_sf_pg import insert_bm_sf_to_pgdb
from tracker_pg import insert_tracker_data_to_pgdb
from hp_data_pg import process_hp_data_and_insert_to_pg
from format_upload_cellcount_pg import cell_count_processing
from format_upload_cellculture import tissue_production_processing
from format_upload_flex_pg import flex2_processing
from dna_data_pg import process_dna_data_and_insert_to_pg
import os, sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(".")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
    path = os.path.join(base_path, relative_path)

    return path

# cell line

# cell bank

# upload biomaterials from g-drive
# file_id = '1-n2zwPWklDmYvsyYcuaSqdirkg1vnwAaMFXQvvDCyLc'
# sheet_list = ['biomaterial', 'scaffold', 'form factor', 'press parameter', 'autoclave specification'] # sheet_list variable is read by the function read_gsheet
# table_name=['biomaterial','scaffold','form_factor','press_parameter','autoclave_specification']
# column_positions = [14,13,11,11,11]
# insert_bm_sf_to_pgdb(file_id, sheet_list, table_name,column_positions)

# # upload analytcal trackers from g-drive
# file_id = '1MOuCpubEbwf7QE_tU5IfL_pqFwtDukOqH5o_9Z0WnHM'
# sheet_name = "Tracker" # sheet_name variable is read by the function read_gsheet
# table_name = 'analytical_tracker'
# insert_tracker_data_to_pgdb(file_id, sheet_name, table_name)

# upload cell culture tracker from g-drive
# file_id = '1PxgbZfxgc2cVEJooCtSvNgFlVabnHUUcy9Q_R8_xP4g' # cell culture tracker
# sheet_name = 'tracker'
# table_name = 'cell_culture_tracker'
# insert_tracker_data_to_pgdb(file_id, sheet_name, table_name)

# upload media prep from g-drive
file_id = '1-2LQo-Xj4bdmy0EeyYNbvLnoXHKTN-QoGupEgimmT2c'
sheet_name = 'Media Prep'
table_name = 'media_prep'
insert_tracker_data_to_pgdb(file_id, sheet_name, table_name)

# # # upload seed train from g-drive


# upload cell count from g-drive
process_folder_path = '/Users/wayne/Library/CloudStorage/GoogleDrive-wayne@vitrolabsinc.com/Shared drives/R&PD Team/Vitrolab Experimental Data (Trained User Only)/Instrument/nucleocounter raw files'
archive_folder_path = '/Users/wayne/Library/CloudStorage/GoogleDrive-wayne@vitrolabsinc.com/Shared drives/R&PD Team/Vitrolab Experimental Data (Trained User Only)/Instrument/nucleocounter raw files/Archive (Data Uploaded)'
cell_count_processing(process_folder_path, archive_folder_path)

# upload tissue production from g-drive
path = resource_path('Tissue')
archive = resource_path('Tissue/archive')
tissue_production_processing(root_directory=path, archive_directory=archive)

# upload hp data from g-drive. postgresql table is serial id
hp_folder_path  = '/Users/wayne/Library/CloudStorage/GoogleDrive-wayne@vitrolabsinc.com/Shared drives/R&PD Team/Vitrolab Experimental Data (Trained User Only)/Analytical/hydroxyproline'
process_hp_data_and_insert_to_pg(hp_folder_path)

# upload dna data from g-drive, postgresql table is serial id
dna_folder_path  = '/Users/wayne/Library/CloudStorage/GoogleDrive-wayne@vitrolabsinc.com/Shared drives/R&PD Team/Vitrolab Experimental Data (Trained User Only)/Analytical/DNA'
process_dna_data_and_insert_to_pg(dna_folder_path)


# # upload flex2 data from g-drive (automated completely now, run as needed)
# run_flex2_upload = input('do you need to upload flex2 data from google sheet? (y/n)')
# if run_flex2_upload == 'y':
#     row = int(input('enter index to start appending from y')) #for recent data, its total row in gsheet minus 2
#     start_row = int(row)
#     flex2_processing(start_row,file=None, archive_directory=None) # reads the g-sheet. Note: use if there are additional data needed to upload to postgres
# else:
#     print('skipping flex upload')