#!/bin/bash
#
# assumptions:
# - backups are stored on the ftp_incomming folder.
# - backup file is a tar.bz2 compressed file
# - uncompressed files are: data.json and meta.json
# - 
# ARGUMENTS
# - BACKUP_FILE: only the name of the file
# - MANAGE_PY: full path to the manage.py file. 
#   e.g.: /home/transapp/visualization/manage.py

BACKUP_FOLDER="$1"
BACKUP_FILE="$2"
BACKUP_DB="$3"
BACKUP_IMGS="$4"
MANAGE_PY="$5"
DEST_IMG_FLDR="$6"

function exit_usage()
{
	echo "Usage: $ bash script_post.sh <BACKUP_FOLDER> <BACKUP_FILE> <BACKUP_DB> <BACKUP_IMGS> <MANAGE_PY> <DEST_IMG_FLDR"
	echo "e.g:"
	echo " - BACKUP_FOLDER: ftp_incomming"
	echo " - BACKUP_FILE  : backup_2016-10-03__12_22_02.tar.gz"
	echo " - BACKUP_DB    : database.tar.gz"
	echo " - BACKUP_IMGS  : images.tar.gz"
	echo " - MANAGE_PY    : visualization/manage.py"
	echo " - DEST_IMG_FLDR: visualization/media/reported_images"
	exit 1
}

echo " - [ON REMOTE VIZ]: -------- POST LOAD INIT --------"

## CHECKS
# backup folder
if [   -z "$BACKUP_FOLDER" ]; then exit_usage; fi
BACKUP_FOLDER="/home/$USER/$BACKUP_FOLDER"
if [ ! -d "$BACKUP_FOLDER" ]; then
	echo "Backup folder not found: $BACKUP_FOLDER"
	exit_usage
fi

# backup filename
if [   -z "$BACKUP_FILE" ]; then exit_usage; fi
BACKUP_FILE="$BACKUP_FOLDER/$BACKUP_FILE"
if [ ! -e "$BACKUP_FILE" ]; then
	echo "Backup file not found: $BACKUP_FILE"
	exit_usage
fi

# imgs backup DB
if [   -z "$BACKUP_DB" ]; then exit_usage; fi
#BACKUP_DB="$BACKUP_FOLDER/$BACKUP_DB"

# imgs backup images
if [   -z "$BACKUP_IMGS" ]; then exit_usage; fi
#BACKUP_IMGS="$BACKUP_FOLDER/$BACKUP_IMGS"

# manage.py
if [   -z "$MANAGE_PY" ]; then exit_usage; fi
MANAGE_PY="/home/$USER/$MANAGE_PY"
if [ ! -e "$MANAGE_PY" ]; then
	echo "MANAGE.PY file not found: $MANAGE_PY"
	exit_usage
fi

# imgs backup images
if [   -z "$DEST_IMG_FLDR" ]; then exit_usage; fi
DEST_IMG_FLDR="/home/$USER/$DEST_IMG_FLDR"
mkdir -p "$DEST_IMG_FLDR"
if [ ! -d "$DEST_IMG_FLDR" ]; then
	echo "Destination folder for images backup not found: $DEST_IMG_FLDR"
	exit_usage
fi

# check manage works well
#cd "$BACKUP_FOLDER"
#/home/transapp/visualization/venv/bin/python "$MANAGE_PY" 2>/dev/null 1>/dev/null
#if [ $? -ne 0 ]; then
#	echo "manage.py failed run.. maybe some dependencies are missing"
#	exit 1
#fi
#echo "[]" > dummy.json
#/home/transapp/visualization/venv/bin/python "$MANAGE_PY" loaddata dummy.json 2>/dev/null 1>/dev/null
#if [ $? -ne 0 ]; then
#	echo "manage.py loadata failed run.. maybe some dependencies are missing"
#	rm dummy.json
# 	exit 1
#fi

## WORK
cd "$BACKUP_FOLDER"

# create tmp folder for stuff
echo " - [ON REMOTE VIZ]: creating tmp folder for extraction: $BACKUP_FOLDER/tmp"
rm -rf tmp
mkdir tmp
cd tmp

# extract 
echo " - [ON REMOTE VIZ]: extracting files to: $BACKUP_FOLDER/tmp" 
tar -zxf "$BACKUP_FILE"

if [ ! -e "$BACKUP_DB" ]; then
	echo "Backup file not found: $BACKUP_DB" 
	exit 1
fi
if [ ! -e "$BACKUP_IMGS" ]; then
	echo "Backup file for images not found: $BACKUP_IMGS" 
	exit 1
fi
tar -zxf "$BACKUP_DB"
mkdir imgs
cd imgs
tar -zxf ../"$BACKUP_IMGS"
cd ..

# check tar.gz files
if [ ! -e database.sql ]; then
	echo "database.sql not found.. File extraction failed" 
	exit 1
fi

# copy images
echo " - [ON REMOTE VIZ]: copying images from $BACKUP_FOLDER/tmp/imgs to $DEST_IMG_FLDR" 
cp -arn imgs/* "$DEST_IMG_FLDR"

# load data
echo " - [ON REMOTE VIZ]: loading backup to database using $MANAGE_PY"
touch working.lock
sudo -u postgres psql dropdb ghostinspector
sudo -u postgres psql createdb -T template0 ghostinspector
nohup sudo -u postgres psql ghostinspector < database.sql && rm working.lock & 
#nohup /home/transapp/visualization/venv/bin/python "$MANAGE_PY" loaddata data.json && rm working.lock &  

# wait
INIT="$(date +%H:%M:%S)"
while [  -e working.lock ]; do
	echo "waiting ... $INIT / $(date +%H:%M:%S)  P1-P2-P3=$PARAM1-$PARAM2-$PARAM3"
	sleep 5
done


# delete stuff
echo " - [ON REMOTE VIZ]: removing tmp folder" 
cd "$BACKUP_FOLDER"
rm -rf tmp

echo " - [ON REMOTE VIZ]: -------- POST LOAD DONE --------"
exit 0