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
echo " - checking parameters:"
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
echo "  > SERVER_FLDR: $SERVER_FLDR"

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
echo "  > BACKUP_FOLDER: $BACKUP_FOLDER"

IMGS_FLDR="$3"
if [ -z "$IMGS_FLDR" ]; then
	echo "This script must be called with the IMGS_FLDR parameter"
	echo "IMGS_FLDR represents the full path to the folder where images are stored"
	echo "e.g: /home/transapp/visualization/media/reported_images"
	exit 1
fi
echo "  > IMGS_FLDR: $IMGS_FLDR"

DATABASE_NAME="$4"
if [ -z "$DATABASE_NAME" ]; then
	echo "This script must be called with the DATABASE_NAME parameter"
	echo "DATABASE_NAME represents the database name, duh."
	exit 1
fi
echo "  > DATABASE_NAME: $DATABASE_NAME"

BKPS_LIFETIME="$5"
if [ -z "$BKPS_LIFETIME" ]; then
	echo "This script must be called with the BKPS_LIFETIME parameter"
	echo "BKPS_LIFETIME represents the number of days to keep backup files alive."
	echo "This time is fixed for partial backups to 2 days."
	echo "e.g.: 15"
	exit 1
fi
echo "  > BKPS_LIFETIME: $BKPS_LIFETIME"

BKP_TYPE="$6"
if [ -z "$BKP_TYPE" ]; then
	echo "This script must be called with the BKP_TYPE parameter"
	echo "BKP_TYPE represents the backup type: 'complete' or 'partial'"
	exit 1
fi
if [ "$BKP_TYPE" != "complete" ] && [ "$BKP_TYPE" != "partial" ] ; then
	echo "INVALID TYPE: BKP_TYPE should be 'complete' or 'partial'"
	exit 1
fi
echo "  > BKP_TYPE: $BKP_TYPE"

PARTIAL_BKP_TIME="$7"
if [ "$BKP_TYPE" = "partial" ] && [ -z "$PARTIAL_BKP_TIME" ] ; then
	echo "This script must be called with the PARTIAL_BKP_TIME parameter"
	echo "PARTIAL_BKP_TIME represents the amount of time used to lookup for"
	echo "database updates. Format is 'minutes hours days'"
	echo "e.g: '5' for a 5 minutes lookup"
	exit 1
fi
echo "  > PARTIAL_BKP_TIME: $PARTIAL_BKP_TIME"


#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### GENERATED PARAMETERS
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

MUTEX_FOLDER="$BACKUP_FOLDER"/lockFolder.lock
BACKUP_FOLDER="$BACKUP_FOLDER"/"$BKP_TYPE"

# bkp files
TMP_DB_DUMP=database.sql
TMP_IMG_BACKUP=images.tar.gz
TMP_DB_BACKUP=database.tar.gz


THIS_APP_FLDR="$SERVER_FLDR/AndroidRequestsBackups"

MANAGE_PY="$SERVER_FLDR/manage.py"

echo " - computed variables:"
echo "  > MUTEX_FOLDER: $MUTEX_FOLDER"
echo "  > BACKUP_FOLDER: $BACKUP_FOLDER"
echo "  > TMP_DB_DUMP: $TMP_DB_DUMP"
echo "  > TMP_IMG_BACKUP: $TMP_IMG_BACKUP"
echo "  > TMP_DB_BACKUP: $TMP_DB_BACKUP"
echo "  > THIS_APP_FLDR: $THIS_APP_FLDR"
echo "  > IMGS_FLDR: $IMGS_FLDR"
echo "  > MANAGE_PY: $MANAGE_PY"


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
if [ ! -e "$MANAGE_PY" ]; then
	echo "MANAGE.PY file not found: $MANAGE_PY"
	exit 1
fi

## manage.py works well
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
#### MUTEX
#### #### #### #### #### #### #### #### #### #### #### #### #### ####
function free_mutex()
{
	rm -rf "$MUTEX_FOLDER"
}
function exit_and_free()
{
	free_mutex
	exit 1
}

while true ; do
	if mkdir "$MUTEX_FOLDER" 2>/dev/null
		then    # directory did not exist, but was created successfully
		trap exit_and_free 1 2 9 15 17 19 23
    	echo " - successfully acquired lock: $MUTEX_FOLDER"
    	break
	else    # failed to create the directory, presumably because it already exists
		echo " - cannot acquire lock, giving up on $MUTEX_FOLDER"

		# force free on too old mutex
		if test "`find $MUTEX_FOLDER -mmin +10`" ; then
			free_mutex
			continue
		fi

		# wait for complete and exit for partial bkps
		if [ "$BKP_TYPE" = "complete" ]; then
			sleep 2
		else
			echo "//////////// Ending work! ////////////"
			exit 1
		fi
	fi
done


#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### PREPARATION
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

# delete old stuff older than N days
echo " - deleting files older than N days on $BACKUP_FOLDER"
if [ -d "$BACKUP_FOLDER" ]; then
	find "$BACKUP_FOLDER" -ctime +"$BKPS_LIFETIME" -type f -delete	
fi

echo " - looking for new $BKP_TYPE backup file"
## Look for new files
# e.g: backup_2016-10-03__12_22_02.tar.gz"
cd "$BACKUP_FOLDER"
pattern="NEW_backup_*.tar.gz"
files=( $pattern )
oldest_not_used="${files[0]}"


if [ -z "$oldest_not_used" ] || [ ! -e "$oldest_not_used" ]; then
	echo " - There are not new backup files to load on $BACKUP_FOLDER. Bye"
	exit_and_free
fi
echo " - using oldest backup file: $oldest_not_used"


echo " - marking as used: $BACKUP_FILE"
BACKUP_FILE_NOT_FULL="${oldest_not_used:4}"
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
	exit_and_free
fi

if [ ! -e "$TMP_IMG_BACKUP" ]; then
	echo "Backup file for images not found: $TMP_IMG_BACKUP" 
	exit_and_free
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
free_mutex

echo "---------------------------------------------------------------"
echo "loaddata.sh end . . $(date)"
echo "---------------------------------------------------------------"

exit 0