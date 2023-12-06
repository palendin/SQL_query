from bm_sf_pg import insert_bm_sf_to_pgdb
from tracker_pg import insert_tracker_data_to_pgdb
from hydroxyproline_pg import insert_hp_csv_data_to_pgdb
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

# seed train

# tissue production

# cell count

# metabolite


# biomaterials
bm_sf_path = resource_path('biomaterial_scaffold_postgresql')
insert_bm_sf_to_pgdb(bm_sf_path,file_name='biomaterial_and_scaffold_prep.xlsx',table_name=['biomaterial','scaffold','form_factor','press_parameter','autoclave_specification'])

# trackers
analytical_tracker_path = resource_path('tracker_postgresql')
insert_tracker_data_to_pgdb(analytical_tracker_path,file_name='Analytical Experiment Tracker.csv',table_name='analytical_tracker')

# hydroxyproline raw data
raw_hp_data_path = resource_path('hp_raw_postgresql')
insert_hp_csv_data_to_pgdb(raw_hp_data_path,file_name='hp_combined_raw.csv',table_name='hydroxyproline_raw')

# hydroxyproline biopsy data
biopsy_data_path = resource_path('hp_biopsy_postgresql')
insert_hp_csv_data_to_pgdb(biopsy_data_path,file_name='biopsy_combined_raw.csv',table_name='biopsy_result')

