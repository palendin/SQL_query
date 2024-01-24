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
    media_key varchar,
    media_type varchar,
    volume_to_make_L float,
    prep_date date,
    operator varchar,
    experiment_for varchar,
    source_link varchar,
    total_material_cost float,
    sample_id varchar,
)


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
    id serial primary key not null,
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
    id serial primary key not null,
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
--table name run_detail, run_parameter, sample_plan, seed_operation, process_values, feed_operation, media_sampling, fresh_media_sampling, biopsy_sampling
--(use serial auto index)
drop table if exists tissue_production.run_detail;
create table tissue_production.run_detail(
    id serial primary key not null,
    experiment_id varchar,
    vessel_type varchar,
    run_description text,
    vessel_number int,
    run_id varchar,
    scaffold_id varchar,
    vial_id varchar,
    culture_duration_days int,
    media_recipe varchar,
    media_key varchar,
    Incubator varchar,
    start_date date,
    end_date date,
    hide_id varchar
)

drop table if exists tissue_production.run_parameter;
create table tissue_production.run_parameter(
    id serial primary key not null,
    run_id varchar,
    target_working_volume_ml float,
    target_seed_area_cm2 int,
    target_seed_density_cells_per_cm2 numeric,
    target_seed_number numeric,
    temperature_SP_C float,
    pCO2_SP float,
    pO2_SP float,
    CO2_SP float,
    O2_SP float,
    pH_SP float,
    rocking_hz_SP float,
    rocking_angle_SP float,
    feed_rate_mlpm_SP float,
    outlet_rate_mlpm_SP float,
    vessel_pressure_psi_SP float,
    actuator_wait_mins float,
    feed_delay float,
    rest_time_hr float,
    stirr_init_rpm int,
    stirr_final_rpm int,
    init_air_flow_mlpm float,
    final_air_flow_mlpm float,
    recirculation_rate_mlpm float,
    process_mode varchar
)

drop table if exists tissue_production.sample_plan;
create table tissue_production.sample_plan(
    id serial primary key not null,
    run_id varchar,
    sampling_ETT_day float,
    media_sample varchar,
    biopsy varchar,
    feed varchar,
    monitor varchar,
    hide_id varchar,
    feed_id varchar,
    sample_id varchar,
    biopsy_id varchar,
)

drop table if exists tissue_production.seed_operation;
create table tissue_production.seed_operation(
    id serial primary key not null,
    run_id varchar,
    seed_volume_ml float,
    concentration_cells_per_ml numeric,
    seed_number numeric,
    seed_date timestamp,
    flood_time_hrs int,
    media_id varchar,
    media_volume_ml float,
    rocking_start_time timestamp,
    operator varchar,
    comment text,
)

drop table if exists tissue_production.process_values;
create table tissue_production.process_values(
    id serial primary key not null,
    run_id varchar,
    monitor_date timestamp,
    volume_ml float,
    temperature_C float,
    pCO2 float,
    pO2 float,
    CO2 float,
    O2 float,
    pH float,
    rocking_hz float,
    rocking_angle float,
    feed_rate_mlpm float,
    outlet_rate_mlpm float,
    vessel_pressure_psi float,
    stirr_rpm int,
    air_flow_mlpm float,
    tank_weight_g float,
    base_weight_g float,
    acid_weight_g float,
    feed_weight_g float,
    feed_change_weight_g float,
    waste_weight_g float,
    waste_change_weight_g float
)

drop table if exists tissue_production.feed_operation;
create table tissue_production.feed_operation(
    id serial primary key not null,
    feed_id varchar,
    feed_date timestamp,
    media_id varchar,
    media_exchange_volume_ml float,
    time_out timestamp,
    time_in timestamp,
    operator varchar,
    comment text
)

drop table if exists tissue_production.media_sampling;
create table tissue_production.media_sampling(
    id serial primary key not null,
    sample_id varchar,
    sample_date timestamp,
    operator varchar,
    comment text
)

drop table if exists tissue_production.fresh_media_sampling;
create table tissue_production.fresh_media_sampling(
    id serial primary key not null,
    experiment_id varchar,
    sample_id varchar,
    sampling_ETT_day float,
    sample_date timestamp,
    operator varchar,
    comment text,
    media_key varchar
)

drop table if exists tissue_production.biopsy_sampling;
create table tissue_production.biopsy_sampling(
    id serial primary key not null,
    biopsy_id varchar,
    biopsy_date timestamp,
    biopsy_purpose text,
    biopsy_diameter_mm float,
    num_biopsy_taken int,
    storage_location varchar,
    operator varchar,
    comment text
)

drop table if exists tissue_production.hide_harvest;
create table tissue_production.hide_harvest(
    id serial primary key not null,
    run_id varchar,
    harvest_date timestamp,
    wet_weight_g float,
    thickness_1_mm float,
    thickness_2_mm float,
    thickness_3_mm float,
    thickness_4_mm float,
    thickness_5_mm float,
    thickness_6_mm float,
    avg_thickness_mm float,
    mechanical_strength float,
    fiber_protrusion varchar,
    surface_smoothness varchar,
    operator varchar,
    comment text
)

drop table if exists tissue_production.run_deviation;
create table tissue_production.run_deviation(
    id serial primary key not null,
    run_id varchar,
    deviation varchar,
    comments text
)

drop table if exists tissue_production.flex2_id_conversion;
create table tissue_production.flex2_id_conversion(
    id serial primary key not null,
    flex2_id varchar,
    sample_id varchar
)

-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------

--cell_inventory

-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------

--cell_line

-----------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------

--instrument (cell_count, flex2)
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


drop table if exists instrument.flex2;
create table instrument.flex2(
	id serial primary key not null,
    date_time timestamp,
    comment text,
    sample_id varchar,
    sample_type varchar,
    pH float,
    PO2 float,
    PCO2 float,
    Gln float,
    Glu float,
    Gluc float,
    Lac float,
    NH4 float,
    Na float,
    K float,
    Ca float,
    osm float,
    pre_dilution_multiplier int,
    vessel_id varchar,
    batch_id varchar,
    cell_type varchar,
    vessel_temperature_C float,
    vessel_pressure_psi float,
    sparging_O2 float,
    pH_at_temp float,
    PO2_at_temp float,
    PCO2_at_temp float,
    O2_saturation float,
    CO2_saturation float,
    HCO3 float,
    pH_gas_flow_time float,
    chemistry_flow_time float,
    chemistry_dilution_ratio varchar,
    tray_location varchar,
    chemistry_cartridge_lot_number int,
    chemistry_card_lot_number int,
    gas_cartridge_lot_number int,
    gas_card_lot_number int,
    time_in_tray varchar,
    sample_time timestamp,
    operator varchar
)

--INSERT into the same row will change the specified value 
INSERT INTO analytical_db.analytical_tracker (id, start_date) VALUES (1, '11/11/2023');

--do not drop table and create table again if wanting to add new columms
ALTER TABLE analytical_db.analytical_tracker	 
ADD COLUMN new_column varchar

--import csv cotaining the data
copy pizza_schema.hp_assay
from '/Library/PostgreSQL/15/pizza_sales/HP_assay_master_data.csv'
delimiter ',' csv header;



-- create a serial id without having to drop the column or the whole table and retain the column orders
CREATE SEQUENCE t_seq INCREMENT BY 1;
SELECT setval('t_seq', (SELECT max(id) FROM analytical_db.hydroxyproline_raw));

ALTER TABLE analytical_db.hydroxyproline_raw ALTER COLUMN id SET DEFAULT nextval('t_seq');


--replacing value in a specific column with SET by filtering the desired name 
UPDATE analytical_db.biopsy_result
SET experiment_id = 'HP45-20231201'
WHERE experiment_id LIKE '%HP45%'

--update multiple values at once
update users as u set -- postgres FTW
  email = u2.email,
  first_name = u2.first_name,
  last_name = u2.last_name
from (values
  (1, 'hollis@weimann.biz', 'Hollis', 'Connell'),
  (2, 'robert@duncan.info', 'Robert', 'Duncan')
) as u2(id, email, first_name, last_name)
where u2.id = u.id;

--delete specific values
DELETE FROM analytical_db.hydroxyproline_raw
WHERE column_name = 'some_value';

--alter data type to timestamp
ALTER TABLE tissue_production.feed_operation 
ALTER COLUMN feed_date TYPE timestamp without time zone USING feed_date::timestamp without time zone

--join functions:
--https://www.freecodecamp.org/news/sql-join-types-inner-join-vs-outer-join-example/#:~:text=The%20biggest%20difference%20between%20an,table%20in%20the%20resulting%20table.
--LEFT join (can replace LEFT join with INNER/OUTER/RIGHT etc)
SELECT * FROM analytical_db.hydroxyproline_raw as hp

LEFT JOIN biomaterial_scaffold.biomaterial using(biomaterial_id)
LEFT JOIN tracker.analytical_tracker using(experiment_id)

ORDER BY hp.id;




--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------

--flex2 sample data
SELECT 
	cc_tracker.experiment_id,
	cc_tracker.start_date,
	cc_tracker.status,
	rd.run_id,
    rd.run_description
	rd.vessel_type,
	rd.scaffold_id,
	rd.vial_id,
	rd.culture_duration_days,
	rd.media_recipe,
	rd.incubator,
	rd.start_date,
	rd.end_date,
	rd.hide_id,
	sp.sampling_ett_day,
	sp.sample_id,
	ms.sample_date,
	fic.flex2_id,
	f2.*
	
FROM tracker.cell_culture_tracker as cc_tracker

LEFT JOIN tissue_production.run_detail as rd using(experiment_id) 
--INNER JOIN tissue_production.run_parameter as rp using(run_id)
--LEFT JOIN tissue_production.seed_operation as so using(run_id)
LEFT JOIN tissue_production.sample_plan as sp using(run_id)
LEFT JOIN tissue_production.media_sampling as ms using(sample_id)
LEFT JOIN tissue_production.flex2_id_conversion as fic using(sample_id)
LEFT JOIN instrument.flex2 as f2 ON fic.flex2_id = f2.sample_id

--Where rd.run_id = 'CC1-1';



-- flex2 fresh sample data
SELECT 
	cc_tracker.experiment_id,
	cc_tracker.start_date,
	cc_tracker.status,
	rd.media_recipe,
	fms.sample_date,
	fms.sample_id,
	fms.media_key,
	fic.flex2_id,
	f2.*
	
FROM tracker.cell_culture_tracker as cc_tracker
LEFT JOIN tissue_production.run_detail as rd using (experiment_id)
LEFT JOIN tissue_production.fresh_media_sampling as fms using(media_key)
LEFT JOIN tissue_production.flex2_id_conversion as fic using(sample_id)
LEFT JOIN instrument.flex2 as f2 ON fic.flex2_id = f2.sample_id
