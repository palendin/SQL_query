--schema name = tracker
--table names cell_culture_tracker, analytical_tracker, media_prep, cell_line
drop table if exists tracker.analytical_tracker;
create table tracker.analytical_tracker(
    id integer primary key not null,
	experiment_id varchar,
    department varchar,
    assay_type varchar,
    hypothesis text,
    start_date date,
    owner varchar,
    experiment_link varchar,
    status varchar
);

drop table if exists tracker.cell_culture_tracker;
create table tracker.cell_culture_tracker(
    id integer primary key not null,
	experiment_id varchar,
    department varchar,
    process_type varchar,
    experiment_description text,
    start_date date,
    owner varchar,
    experiment_link varchar,
    status varchar

)

-- make sure to have reset index when transferring media prep database to get index, and edit column names
drop table if exists tracker.media_prep;
create table tracker.media_prep(
    id integer primary key not null,
	media_id varchar,
    media_recipe varchar,
    media_type varchar,
    volume_to_make_L float,
    prep_date date,
    operator varchar,
    source_link varchar,
    total_material_cost float,
    sample_id varchar,
);


drop table if exists tracker.cell_line_development;
create table tracker.cell_line_development(
    id integer primary key not null,
    cell_line_id varchar,
    cell_line_type varchar,
    released_for_cell_bank_and_seed_train varchar,
    characterization varchar,
    culture_condition text,
    media_condition text,
    experiment_link varchar
)

-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------

--schema name = analytical_db;
--table name = hydroxyproline, biopsy_result
drop table if exists analytical_db.hydroxyproline;  
create table analytical_db.hydroxyproline(
    id integer primary key not null,
    experiment_id varchar,
    sample_id varchar,
    sample_type varchar,
    sample_state varchar,
    sample_lot varchar,
    biopsy_id varchar,
    culture_date date,
    biopsy_replicate integer,
    biopsy_diameter_mm integer,
    digestion_volume_ul integer,
    dilution_factor integer,
    assay_volume_ul integer,
    loaded_weight1_mg float,
    loaded_weight2_mg float,
    tube_weight1_mg float,
    tube_weight2_mg float,
    operator varchar,
    std_conc_ug_per_well float,
    media_type varchar,
    biomaterial_id varchar,
    reaction_date date,
    abs float,
    sheet_name varchar,
    location varchar,
    data_check varchar,  
    normalized_abs float,
    r_squared float,
    net_weight_mg float,
    ug_per_well float,
    mg_per_ml float,
    mg_per_biopsy float,
    mg_per_cm2 float
);

drop table if exists analytical_db.biopsy_result;  
create table analytical_db.biopsy_result(
    id integer primary key not null,
    experiment_id varchar,
    biopsy_id varchar,
    biomaterial_id varchar,
    mg_per_biopsy_mean float,
    mg_per_biopsy_std float,
    mg_per_ml_mean float,
    mg_per_ml_std float,
    mg_per_cm2_mean float,
    mg_per_cm2_std float,
    net_weight_mg float,
    tissue_areal_density_mg_per_cm2 float
);

-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------
--schema name biomaterial_scaffold
--table name biomaterial, scaffold_prep, form_factor, press_parameter, autoclave_specification
drop table if exists biomaterial_scaffold.biomaterial;  
create table biomaterial_scaffold.biomaterial(
    id integer primary key not null,
    biomaterial_id varchar,
    material_type varchar,
    description text,
    vendor varchar,
    received_date date,
    needle_punch integer,
    manufacture_gsm integer,
    manufacture_thickness_mm float,
    areal_density_mg_per_cm2 float,
    total_cost float,
    total_length_m float,
    used_m float,
    remaining_m float,
    biomaterial_id_status varchar
)

drop table if exists biomaterial_scaffold.scaffold;  
create table biomaterial_scaffold.scaffold(
    id integer primary key not null,
    scaffold_id varchar,
    form_factor_id varchar,
    press_id varchar,
    autoclave_id varchar,
    post_press_weight_g float,
    post_press_wetting_ml float,
    thickness_mm float,
    weight_with_frame float,
    coating_type varchar,
    coating_volume_ml float,
    date_prepped date
)

drop table if exists biomaterial_scaffold.form_factor;  
create table biomaterial_scaffold.form_factor(
    id integer primary key not null,
    form_factor_id varchar,
    form_type varchar,
    tissue_geometry varchar,
    tissue_culture_length_in float,
    tissue_culture_width_in float,
    tissue_culture_area_in2 float,
    internal_volume_ml float,
    internal_chamber_height_in float,
    chamber_outer_length_in float,
    chamber_outer_width_in float,
    Note text
)

drop table if exists biomaterial_scaffold.press_parameter;
create table biomaterial_scaffold.press_parameter(
    id integer primary key not null,
    press_id varchar,
    press_instrument varchar,
    target_thickness_mm float,
    press_duration_s float,
    offset_height_mm float,
    spacer_type varchar,
    temperature_F int,
    pressure_psi int,
    num_presses int,
    press_sides varchar,
    spacer_pattern varchar
)

drop table if exists biomaterial_scaffold.autoclave_specification;
create table biomaterial_scaffold.autoclave_specification(
    id integer primary key not null,
    autoclave_id varchar,
    system varchar,
    cycle varchar,
    cycle_phase varchar,
    sterilization_temp_C int,
    dry_temp_C int,
    exhaust_speed varchar,
    sterilization_time_min int,
    dry_time_min int,
    total_time_min int
)


-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------
--schema name seed_train

-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------
--schema name tissue_production

-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------

--cell_inventory

-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------

--cell_line

-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------

--instrument
drop table if exists instrument.cell_count;
create table instrument.cell_count(
    id serial primary key not null,
    sample_id varchar,
    protocol varchar,
	software_version varchar,
	secure_mode_status varchar,
    signed_by varchar,
	sample_media varchar,
	admin_user varchar,
	operator varchar,
	instrument varchar,
	tags varchar,
	comments text,
	total_cells_per_ml numeric,
	live_cells_per_ml numeric,
	dead_cells_per_ml numeric,
	percent_viability float,
	diameter_um float,
	percent_aggregates float,
	debris_index integer,
	dilution_factor float,
	status varchar
)





--INSERT into the same row will change the specified value 
--INSERT INTO analytical_db.analytical_tracker (id, start_date) VALUES (1, '11/11/2023');

--do not drop table and create table again if wanting to add new columms
--ALTER TABLE analytical_db.analytical_tracker	 
--ADD COLUMN new_column varchar

--import csv cotaining the data
--copy pizza_schema.hp_assay
--from '/Library/PostgreSQL/15/pizza_sales/HP_assay_master_data.csv'
--delimiter ',' csv header;
