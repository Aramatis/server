#!/bin/bash

#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### USER CONFIGURATION
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

## visualization server data
REMOTE_USER="mpavez"
REMOTE_HOST="172.17.57.241"
# REMOTE_USER="transapp"
# REMOTE_HOST="104.236.183.105"
REMOTE_VIZ_MANAGE_PY="workspaces/visualization/manage.py"
REMOTE_IMG_FLDR="workspaces/visualization/media/reported_images"

# where to put backup data on the visualization server
# e.g: ftp_incoming --> /home/$USER/ftp_incoming
REMOTE_VIZ_INCOMING_FLDR=ftp_incoming


## this machine private key, used to enter the remote host
PRIVATE_KEY=/home/server/.ssh/id_rsa


## bakcup files

# at some point, this folder will be completely deleted, so ensure
# this is not something important!, like '/home' or '/'.
TMP_BKP_FLDR=/tmp/backup_viz
TMP_IMG_BACKUP=images.tar.gz
TMP_DB_BACKUP=database.tar.gz
TMP_BKP_FILE="backup_$(date +%Y-%m-%d__%H_%M_%S).tar.gz"

echo "---------------------------------------------------------------"
echo "upload.sh init $(date)"
echo "---------------------------------------------------------------"
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### PARAMETERS
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
VIZ_APP_FLDR="$1"
if [ -z "$VIZ_APP_FLDR" ]; then
	echo "This script must be called with the parameter VIZ_APP_FLDR"
	echo "VIZ_APP_FLDR represents the full path to the VisualizationBackupApp."
	exit 1
fi
if [ ! -d "$VIZ_APP_FLDR" ]; then
	echo "VIZ_APP_FLDR folder does not exists: $VIZ_APP_FLDR"
	exit 1
fi
if ! [ "$(id -u)" = "0" ] ; then
	echo "This script must be called by root."
	exit 1
fi


#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### BUILD VARIABLES
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
# for ssh 
REMOTE_USERHOST="$REMOTE_USER"@"$REMOTE_HOST"

# for sftp
SFTP_COMMANDS="$TMP_BKP_FLDR"/sftp_commands.txt

# django
SERVER_FLDR=$(dirname "$VIZ_APP_FLDR")
IMGS_FLDR="$SERVER_FLDR"/media/reported_images

# tmp
TMP_BKP_DB_FULL="$TMP_BKP_FLDR"/"$TMP_DB_BACKUP"
TMP_BKP_IMGS_FULL="$TMP_BKP_FLDR"/"$TMP_IMG_BACKUP"
TMP_BKP_FILE_FULL="$TMP_BKP_FLDR/$TMP_BKP_FILE"

#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### CHECKS
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
if [ ! -d "$SERVER_FLDR" ]; then
	echo " - server folder not found: $SERVER_FLDR"
	exit 1
fi
if [ ! -d "$IMGS_FLDR" ]; then
	echo " - server images not found at: $IMGS_FLDR"
	exit 1
fi


#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### PREPARATION
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

#### clean tmp folder in server
#### ----- ----- ----- ----- ----- ----- ----- ----- -----
echo "- preparing environment ..."
rm -rf "$TMP_BKP_FLDR"
mkdir -p "$TMP_BKP_FLDR"
if [ ! -d "$TMP_BKP_FLDR" ]; then
	echo " - failed to create the tmp folder: $TMP_BKP_FLDR"
	exit 1
fi


#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### BACKUP CREATION
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

#### create image backup
#### ----- ----- ----- ----- ----- ----- ----- ----- -----
echo "- creating reports image backups"
cd "$IMGS_FLDR"
tar -zcvf "$TMP_BKP_IMGS_FULL" *
if [ ! -e "$TMP_BKP_IMGS_FULL" ]; then
	echo " - image backup file not found, but it should exists!: $TMP_BKP_IMGS_FULL"
	exit 1
fi


#### create database backup
#### ----- ----- ----- ----- ----- ----- ----- ----- -----
echo "- creating backup ..."
cd "$TMP_BKP_FLDR"
python "$SERVER_FLDR"/manage.py archive                #   comment for testing
#cp /home/sebastian/database.tar.gz "$TMP_BKP_DB_FULL" # uncomment for testing

# check db backup
echo "- looking for db backup results ..."
if [ ! -e "$TMP_BKP_DB_FULL" ]; then
	echo "UPS!.. The db backup file was not found. Probably, the 'python manage.py archive' command failed"
	echo "Required file: $TMP_BKP_DB_FULL"
	exit 1
fi

#### create single backup
#### ----- ----- ----- ----- ----- ----- ----- ----- -----

cd "$TMP_BKP_FLDR"
tar -zcvf "$TMP_BKP_FILE" "$TMP_DB_BACKUP" "$TMP_IMG_BACKUP"
if [ ! -e "$TMP_BKP_FILE" ]; then
	echo "UPS!.. The backup file was not found. Something went wrong while compressing the files"
	exit 1
fi


#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### Upload backups
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
	
#### prepare visualization server
#### ----- ----- ----- ----- ----- ----- ----- ----- -----

cd "$VIZ_APP_FLDR"
ssh -i "$PRIVATE_KEY" "$REMOTE_USERHOST" "bash -s" -- < script_pre.sh "$REMOTE_VIZ_INCOMING_FLDR"

#### upload
#### ----- ----- ----- ----- ----- ----- ----- ----- -----

echo "- generating FTP batch file: $SFTP_COMMANDS"

## generate ftp command file
cd "$TMP_BKP_FLDR"
rm -f "$SFTP_COMMANDS"
echo "cd  $REMOTE_VIZ_INCOMING_FLDR" >  "$SFTP_COMMANDS"
echo "put $TMP_BKP_FILE_FULL" >> "$SFTP_COMMANDS"


## send
echo "- sending file"
sftp -p -i "$PRIVATE_KEY" -b "$SFTP_COMMANDS" "$REMOTE_USERHOST"


#### delete backups on this server
#### ----- ----- ----- ----- ----- ----- ----- ----- -----

echo "- deleting stuff"
if [ -d "$TMP_BKP_FLDR" ]; then
	cd "$TMP_BKP_FLDR"

	# delete db_backup
	if [ -e "$TMP_BKP_DB_FULL" ]; then	
		rm -f "$TMP_BKP_DB_FULL"
	fi

	# delete img backup
	if [ -e "$TMP_BKP_IMGS_FULL" ]; then
		rm -f "$TMP_BKP_IMGS_FULL"
	fi

	# delete full backup
	if [ -e "$TMP_BKP_FILE_FULL" ]; then
		rm -f "$TMP_BKP_FILE_FULL"
	fi
fi


#### post upload work
#### ----- ----- ----- ----- ----- ----- ----- ----- -----

cd "$VIZ_APP_FLDR"
ssh -i "$PRIVATE_KEY" "$REMOTE_USERHOST" "bash -s" -- < script_post.sh "$REMOTE_VIZ_INCOMING_FLDR" "$TMP_BKP_FILE" "$TMP_DB_BACKUP" "$TMP_IMG_BACKUP" "$REMOTE_VIZ_MANAGE_PY" "$REMOTE_IMG_FLDR"


echo "-------------------------------------------------------------------"
echo "upload.sh end"
echo "-------------------------------------------------------------------"
