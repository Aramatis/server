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


THIS_APP_FLDR="$SERVER_FLDR/VisualizationBackupApp"
IMGS_FLDR="$SERVER_FLDR/$IMGS_FLDR"


#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### CHECKS
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

echo " - checking the required stuff works"

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

# imgs backup folder
mkdir -p "$IMGS_FLDR"
if [ ! -d "$IMGS_FLDR" ]; then
	echo "Destination folder for backup images not found: $IMGS_FLDR"
	exit 1
fi

#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### PREPARATION
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

echo " - looking for new $BKP_TYPE backup file"

cd "$BACKUP_FOLDER"

## Look for new files
# e.g: backup_2016-10-03__12_22_02.tar.gz"
pattern="NEW_backup_*.tar.gz"
files=( $pattern )
oldest_not_used="${files[0]}"


if [ -z "$oldest_not_used" ] || [ ! -e "$oldest_not_used" ]; then
	echo " - There are not new backup files to load on $BACKUP_FOLDER. Bye"
	exit 1
fi
echo " - using oldest backup file: $oldest_not_used"


echo " - marking as used: $BACKUP_FILE"
BACKUP_FILE="$BACKUP_FOLDER/${oldest_not_used:4}"
mv "$oldest_not_used" "$BACKUP_FILE"


# create tmp folder for stuff
echo " - creating tmp folder for extraction: $BACKUP_FOLDER/tmp"
cd "$BACKUP_FOLDER"
rm -rf tmp
mkdir tmp
cd tmp


#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### BACKUP LOADING
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

# uncompress
echo " - extracting files to: $BACKUP_FOLDER/tmp" 
tar -zxf "$BACKUP_FILE"
if [ ! -e "$TMP_DB_BACKUP" ]; then
	echo "Backup file not found: $TMP_DB_BACKUP" 
	exit 1
fi

if [ ! -e "$TMP_IMG_BACKUP" ]; then
	echo "Backup file for images not found: $TMP_IMG_BACKUP" 
	exit 1
fi

echo " - extracting database: $BACKUP_FOLDER/tmp/db"
mkdir -p db && cd db
tar -zxf ../"$TMP_DB_BACKUP"
cd ..

echo " - extracting images: $BACKUP_FOLDER/tmp/imgs" 
mkdir -p imgs && cd imgs
tar -zxf ../"$TMP_IMG_BACKUP"
cd ..

# actual work
cd "$THIS_APP_FLDR"
source scripts/"$BKP_TYPE"_loaddata.sh


#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### CLEANING
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 


# delete stuff
echo " - cleaning stuff" 
cd "$BACKUP_FOLDER"
rm -rf tmp

echo "---------------------------------------------------------------"
echo "loaddata.sh end . . $(date)"
echo "---------------------------------------------------------------"

exit 0