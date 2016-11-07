#!/bin/bash

#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### BACKUP CREATION
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

function check_json_files()
{
	FILE="$1"
	if [ ! -e "$FILE" ]; then
		echo "json file $FILE not found.. File compression failed" 
		exit 1
	fi
}


#### create image backup
#### ----- ----- ----- ----- ----- ----- ----- ----- -----

cd "$TMP_BKP_FLDR"
mkdir -p imgs

while IFS='' read -r line || [[ -n "$line" ]]; do
	IMAGE="$IMGS_FLDR"/"$line"
	echo "Copying image $IMAGE to $TMP_BKP_FLDR/imgs/"
	cp "$IMAGE" imgs/
done < "dump_report_images.txt"

## compress image folder
echo "- creating reports images backup"
cd imgs
tar -zcf "$TMP_BKP_IMGS_FULL" ./*
if [ ! -e "$TMP_BKP_IMGS_FULL" ]; then
	echo " - image backup file not found, but it should exists!: $TMP_BKP_IMGS_FULL"
	exit 1
fi

#### create database backup
#### ----- ----- ----- ----- ----- ----- ----- ----- -----
echo "- creating reports backup ..."
cd "$TMP_BKP_FLDR"
mkdir -p "bkp" && cd "bkp"
python "$SERVER_FLDR"/manage.py visualization_backup_dump
check_json_files 'dump_Report.json'
check_json_files 'dump_EventForBusStop.json'
check_json_files 'dump_StadisticDataFromRegistrationBusStop.json'
check_json_files 'dump_EventForBusv2.json'
check_json_files 'dump_StadisticDataFromRegistrationBus.json'
check_json_files 'dump_Busassignment.json'
check_json_files 'dump_Busv2.json'
tar -zcf "$TMP_DB_BACKUP" ./*.json

# check db backup
echo "- looking for db backup results ..."
if [ ! -e "$TMP_BKP_DB_FULL" ]; then
	echo "UPS!.. The db backup file was not found. Probably, the 'python manage.py reports_archive' command failed"
	echo "Required file: $TMP_BKP_DB_FULL"
	exit 1
fi

