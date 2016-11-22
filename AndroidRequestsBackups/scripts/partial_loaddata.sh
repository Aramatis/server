#!/bin/bash


function check_json_files()
{
	file="$1"
	if [ ! -e "$file" ]; then
		echo "json file  $file not found.. File extraction failed" 
		exit_and_free
	fi
	echo " - (OK) found json $file"
}

cd "$BACKUP_FOLDER"
cd tmp/db

# check json files
echo " - checking for JSON files to load"
check_json_files "dump_Report.json"
check_json_files "dump_EventForBusStop.json"
check_json_files "dump_StadisticDataFromRegistrationBusStop.json"
check_json_files "dump_EventForBusv2.json"
check_json_files "dump_StadisticDataFromRegistrationBus.json"
check_json_files "dump_Busassignment.json"
check_json_files "dump_Busv2.json"

# load queries
echo " - loading records"
python "$MANAGE_PY" visualization_backup_loaddata

# copy images
echo " - copying images from $BACKUP_FOLDER/tmp/imgs to $IMGS_FLDR" 
cd "$BACKUP_FOLDER"
cd tmp
if [ "$(ls -A imgs/)" ]; then
    cp -arn imgs/* "$IMGS_FLDR"
else
    echo " - no images found"
fi

python "$SERVER_FLDR/transform.py" "$BACKUP_FILE_NOT_FULL" "$PARTIAL_BKP_TIME"
