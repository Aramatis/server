#!/bin/bash

#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### BACKUP CREATION
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

#### create image backup
#### ----- ----- ----- ----- ----- ----- ----- ----- -----





#### create database backup
#### ----- ----- ----- ----- ----- ----- ----- ----- -----
echo "- creating reports backup ..."
cd "$TMP_BKP_FLDR"
mkdir -p "bkp" && cd "bkp"
python "$SERVER_FLDR"/manage.py visualization_backup_dump
cp /tmp/reports.json "$TMP_BKP_FLDR"/reports.json

# check_json_files report.json
# check_json_files events_for_busstop.json
# check_json_files statistic_data_from_registration_busstop.json
# check_json_files events_for_busv2.json
# check_json_files statistic_data_from_registration_bus.json
# check_json_files busassignment.json
# check_json_files busv2.json

tar -zcvf "$TMP_DB_BACKUP" *.json

# check db backup
echo "- looking for db backup results ..."
if [ ! -e "$TMP_BKP_DB_FULL" ]; then
	echo "UPS!.. The db backup file was not found. Probably, the 'python manage.py reports_archive' command failed"
	echo "Required file: $TMP_BKP_DB_FULL"
	exit 1
fi

