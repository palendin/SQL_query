from bm_sf_pg import insert_bm_sf_to_pgdb
from tracker_pg import insert_tracker_data_to_pgdb
from hp_data_pg import process_hp_data_and_insert_to_pg
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
file_id = '1-n2zwPWklDmYvsyYcuaSqdirkg1vnwAaMFXQvvDCyLc'
sheet_list = ['biomaterial', 'scaffold', 'form factor', 'press parameter', 'autoclave specification'] # sheet_list variable is read by the function read_gsheet
table_name=['biomaterial','scaffold','form_factor','press_parameter','autoclave_specification']
insert_bm_sf_to_pgdb(file_id, sheet_list, table_name)

# upload analytcal trackers from g-drive
file_id = '1MOuCpubEbwf7QE_tU5IfL_pqFwtDukOqH5o_9Z0WnHM'
sheet_name = "Tracker" # sheet_name variable is read by the function read_gsheet
table_name = 'analytical_tracker'
insert_tracker_data_to_pgdb(file_id, sheet_name, table_name)

# upload cell culture tracker from g-drive
file_id = '1PxgbZfxgc2cVEJooCtSvNgFlVabnHUUcy9Q_R8_xP4g' # cell culture tracker
sheet_name = 'tracker'
table_name = 'cell_culture_tracker'
insert_tracker_data_to_pgdb(file_id, sheet_name, table_name)

# upload media prep from g-drive
file_id = '1-2LQo-Xj4bdmy0EeyYNbvLnoXHKTN-QoGupEgimmT2c'
sheet_name = 'Media Prep'
table_name = 'media_prep'
insert_tracker_data_to_pgdb(file_id, sheet_name, table_name)

# upload seed train from g-drive

# upload tissue production from g-drive

# hydroxyproline data (raw + biopsy). postgresql table is serial id. MAKE SURE ONLY NEW FILES ARE IN THE FOLDER FIRST
path = resource_path('HP_assay') #where the experiment folders are
archive_path = resource_path('HP_assay/archive')
process_hp_data_and_insert_to_pg(path,archive_path)

