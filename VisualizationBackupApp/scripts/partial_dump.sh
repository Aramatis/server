#!/bin/bash


function check_json_files()
{
	FILE="$1"
	if [ ! -e "$FILE" ]; then
		echo "json file $FILE not found.. File compression failed" 
		exit 1
	fi
}


#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### CHECK MANAGE.PY WORKS OK
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

## manage.py existence
MANAGE_PY="$SERVER_FLDR/manage.py"
if [ ! -e "$MANAGE_PY" ]; then
	echo "MANAGE.PY file not found: $MANAGE_PY"
	exit 1
fi

## manage.py works well
cd "$BACKUP_FOLDER"
python "$MANAGE_PY" 2>/dev/null 1>/dev/null
if [ $? -ne 0 ]; then
	echo "manage.py failed run.. maybe some dependencies are missing"
	exit 1
fi

#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### BACKUP CREATION
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

#### create database backup
#### ----- ----- ----- ----- ----- ----- ----- ----- -----
echo "- creating reports backup ..."
cd "$TMP_BKP_FLDR"
mkdir -p "bkp" && cd "bkp"
python "$MANAGE_PY" visualization_backup_dump "$PARTIAL_BKP_TIME"
check_json_files 'dump_Report.json'
check_json_files 'dump_EventForBusStop.json'
check_json_files 'dump_StadisticDataFromRegistrationBusStop.json'
check_json_files 'dump_EventForBusv2.json'
check_json_files 'dump_StadisticDataFromRegistrationBus.json'
check_json_files 'dump_Busassignment.json'
check_json_files 'dump_Busv2.json'
tar -zcf "$TMP_BKP_DB_FULL" *.json

# check db backup
echo "- looking for db backup results ..."
if [ ! -e "$TMP_BKP_DB_FULL" ]; then
	echo "UPS!.. The db backup file was not found."
	echo "Required file: $TMP_BKP_DB_FULL"
	exit 1
fi

#### create image backup
#### ----- ----- ----- ----- ----- ----- ----- ----- -----

cd "$TMP_BKP_FLDR"
mkdir -p imgs

while IFS='' read -r line || [[ -n "$line" ]]; do
	IMAGE="$IMGS_FLDR"/"$line"
	if [ -e "$IMAGE" ] ; then
		echo "Copying image $IMAGE to $TMP_BKP_FLDR/imgs/"
		cp "$IMAGE" imgs/
	fi
done < "bkp/dump_report_images.txt"

## compress image folder
echo "- creating reports images backup"
cd imgs
tar -zcf "$TMP_BKP_IMGS_FULL" *
if [ ! -e "$TMP_BKP_IMGS_FULL" ]; then
	echo " - image backup file not found, but it should exists!: $TMP_BKP_IMGS_FULL"
	exit 1
fi


