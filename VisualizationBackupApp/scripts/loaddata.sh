#!/bin/bash

echo "---------------------------------------------------------------"
echo "loaddata.sh init . . $(date)"
echo "---------------------------------------------------------------"

# root usage check
if ! [ "$(id -u)" = "0" ] ; then
	echo "This script must be called by root."
	exit 1
fi

#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### USER PARAMETERS
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
SERVER_FLDR="$1"
if [ -z "$SERVER_FLDR" ]; then
	echo "This script must be called with the SERVER_FLDR parameter"
	echo "SERVER_FLDR represents the full path to this server."
	echo "e.g: /home/transapp/visualization"
	exit 1
fi
if [ ! -d "$SERVER_FLDR" ]; then
	echo "SERVER_FLDR folder does not exists: $SERVER_FLDR"
	exit 1
fi

BACKUP_FOLDER="$2"
if [ -z "$BACKUP_FOLDER" ]; then
	echo "This script must be called with the BACKUP_FOLDER parameter"
	echo "BACKUP_FOLDER is the FULL PATH to the folder where backups are stored"
	echo "e.g: '/home/transapp/bkps'"
	exit 1
fi
if [ ! -d "$BACKUP_FOLDER" ]; then
	echo "Backup folder not found: $BACKUP_FOLDER"
	exit 1
fi

IMGS_FLDR="$3"
if [ -z "$IMGS_FLDR" ]; then
	echo "This script must be called with the IMGS_FLDR parameter"
	echo "IMGS_FLDR represents the path the folder where images are stored, relative to SERVER_FLDR"
	echo "e.g: media/reported_images"
	exit 1
fi

DATABASE_NAME="$4"
if [ -z "$DATABASE_NAME" ]; then
	echo "This script must be called with the DATABASE_NAME parameter"
	echo "DATABASE_NAME represents the database name, duh."
	exit 1
fi

BKP_TYPE="$5"
if [ -z "$BKP_TYPE" ]; then
	echo "This script must be called with the BKP_TYPE parameter"
	echo "BKP_TYPE represents the backup type: 'complete' or 'partial'"
	exit 1
fi
if [ "$BKP_TYPE" != "complete" ] && [ "$BKP_TYPE" != "partial" ] ; then
	echo "INVALID TYPE: BKP_TYPE should be 'complete' or 'partial'"
	exit 1
fi



#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### GENERATED PARAMETERS
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

BACKUP_FOLDER="$BACKUP_FOLDER"/"$BKP_TYPE"

# bkp files
TMP_DB_DUMP=database.sql
TMP_IMG_BACKUP=images.tar.gz
TMP_DB_BACKUP=database.tar.gz


#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### CHECKS
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

# backup folder with type
if [ ! -d "$BACKUP_FOLDER" ]; then
	echo "Backup folder not found for $BKP_TYPE backups: $BACKUP_FOLDER"
	exit 1
fi

## manage.py existence
MANAGE_PY="$SERVER_FLDR/manage.py"
if [ ! -e "$MANAGE_PY" ]; then
	echo "MANAGE.PY file not found: $MANAGE_PY"
	exit 1
fi

## manage.py works well
# /home/transapp/visualization/venv/bin/python
python "$MANAGE_PY" 2>/dev/null 1>/dev/null
if [ $? -ne 0 ]; then
	echo "manage.py failed run.. maybe some dependencies are missing"
	exit 1
fi


#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### PREPARATION
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

cd "$BACKUP_FOLDER"

## Look for new files
# e.g: backup_2016-10-03__12_22_02.tar.gz"
pattern="NEW_backup_*.tar.gz"
files=( $pattern )
oldest_not_used="${files[0]}"


if [ -z "$oldest_not_used" ] || [ ! -e "$oldest_not_used" ]; then
	echo "New backup file not found on $BACKUP_FOLDER. Bye"
	exit 1
fi
echo "- using oldest backup file: $oldest_not_used"


echo "- Marking as used: $BACKUP_FILE"
BACKUP_FILE="$BACKUP_FOLDER/${oldest_not_used:4}"
mv "$oldest_not_used" "$BACKUP_FILE"



# # imgs backup folder
# DEST_IMG_FLDR="/home/$USER/$DEST_IMG_FLDR"
# mkdir -p "$DEST_IMG_FLDR"
# if [ ! -d "$DEST_IMG_FLDR" ]; then
# 	echo "Destination folder for images backup not found: $DEST_IMG_FLDR"
# 	exit 1
# fi

# # wait
# INIT="$(date +%H:%M:%S)"
# while [  -e working.lock ]; do
# 	echo "waiting ... $INIT / $(date +%H:%M:%S)  P1-P2-P3=$PARAM1-$PARAM2-$PARAM3"
# 	sleep 5
# done


# cd "$BACKUP_FOLDER"

# # create tmp folder for stuff
# echo " - [ON REMOTE VIZ]: creating tmp folder for extraction: $BACKUP_FOLDER/tmp"
# rm -rf tmp
# mkdir tmp
# cd tmp

# check manage.py works well
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



#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### BACKUP LOADING
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 



#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### CLEANING
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 


# # delete stuff
# echo " - [ON REMOTE VIZ]: removing tmp folder" 
# cd "$BACKUP_FOLDER"
# rm -rf tmp

# echo " - [ON REMOTE VIZ]: -------- POST LOAD DONE --------"
# exit 0


echo "---------------------------------------------------------------"
echo "loaddata.sh end . . $(date)"
echo "---------------------------------------------------------------"