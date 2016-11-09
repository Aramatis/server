#!/bin/bash


function check_json_files()
{
	file="$1"
	if [ ! -e "$file" ]; then
		echo "json file  $file not found.. File extraction failed" 
		exit 1
	fi
}


# extract 
echo " - [ON REMOTE VIZ]: extracting files to: $BACKUP_FOLDER/tmp" 
tar -zxf "$BACKUP_FILE"

if [ ! -e "$BACKUP_DB" ]; then
	echo "Backup file not found: $BACKUP_DB" 
	exit 1
fi

#if [ ! -e "$BACKUP_IMGS" ]; then
#	echo "Backup file for images not found: $BACKUP_IMGS" 
#	exit 1
#fi
tar -zxf "$BACKUP_DB"
#mkdir imgs
#cd imgs
#tar -zxf ../"$BACKUP_IMGS"
#cd ..

# check json files
check_json_files report.json
check_json_files events_for_busstop.json
check_json_files statistic_data_from_registration_busstop.json
check_json_files events_for_busv2.json
check_json_files statistic_data_from_registration_bus.json
check_json_files busassignment.json
check_json_files busv2.json

# load queries
python "$MANAGE_PY" visualization_backup_loaddata #matias pc
#/home/transapp/visualization/venv/bin/python "$MANAGE_PY" visualization_backup_loaddata #transapp viz

# copy images
#echo " - [ON REMOTE VIZ]: copying images from $BACKUP_FOLDER/tmp/imgs to $DEST_IMG_FLDR" 
#cp -arn imgs/* "$DEST_IMG_FLDR"



