#!/bin/bash

echo "---------------------------------------------------------------"
echo "dump.sh init . . $(date)"
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

REMOTE_USER="$2"
if [ -z "$REMOTE_USER" ]; then
	echo "This script must be called with the REMOTE_USER parameter"
	echo "REMOTE_USER is the user name of the remote machine. e.g: transapp"
	exit 1
fi
echo "  > REMOTE_USER: $REMOTE_USER"

REMOTE_HOST="$3"
if [ -z "$REMOTE_HOST" ]; then
	echo "This script must be called with the REMOTE_HOST parameter"
	echo "REMOTE_HOST is the name remote machine. e.g: 104.236.183.105"
	exit 1
fi
echo "  > REMOTE_HOST: $REMOTE_HOST"

REMOTE_BKP_FLDR="$4"
if [ -z "$REMOTE_BKP_FLDR" ]; then
	echo "This script must be called with the REMOTE_BKP_FLDR parameter"
	echo "REMOTE_BKP_FLDR is the FULL path to the folder where backups are stored"
	echo "on the remote machine. e.g: '/home/transapp/bkps', will lead to bkps/complete and bkps/partial"
	echo "Any file older than N days on this folder will be deleted!!"
	exit 1
fi
echo "  > REMOTE_BKP_FLDR: $REMOTE_BKP_FLDR"

PRIVATE_KEY="$5"
if [ -z "$PRIVATE_KEY" ]; then
	echo "This script must be called with the PRIVATE_KEY parameter"
	echo "PRIVATE_KEY is the file with this server private key, used"
	echo "to connect to the remote host. e.g: /home/server/.ssh/id_rsa"
	exit 1
fi
if [ ! -e "$PRIVATE_KEY" ]; then
	echo "The PRIVATE_KEY key file does not exists: $PRIVATE_KEY"
	exit 1
fi
echo "  > PRIVATE_KEY: $PRIVATE_KEY"

TMP_BKP_FLDR="$6"
if [ -z "$TMP_BKP_FLDR" ]; then
	echo "This script must be called with the TMP_BKP_FLDR parameter"
	echo "TMP_BKP_FLDR is the path to the folder where backups are built"
	echo "on this server. e.g: /tmp/backup_viz_complete or /tmp/backup_viz_partial"
	echo "at some point, this folder can be completely deleted, so ensure"
	echo "this is not something important!, like '/home' or '/'."
	exit 1
fi
echo "  > TMP_BKP_FLDR: $TMP_BKP_FLDR"
 
IMGS_FLDR="$7"
if [ -z "$IMGS_FLDR" ]; then
	echo "This script must be called with the IMGS_FLDR parameter"
	echo "IMGS_FLDR represents the full path to the folder where images are stored"
	echo "e.g: /home/server/server/media/reported_images"
	exit 1
fi
echo "  > IMGS_FLDR: $IMGS_FLDR"

DATABASE_NAME="$8"
if [ -z "$DATABASE_NAME" ]; then
	echo "This script must be called with the DATABASE_NAME parameter"
	echo "DATABASE_NAME represents the database name, duh."
	exit 1
fi
echo "  > DATABASE_NAME: $DATABASE_NAME"

BKP_TYPE="$9"
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

PARTIAL_BKP_TIME="${10}"
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


VIZ_APP_FLDR="$SERVER_FLDR/AndroidRequestsBackups"

TMP_BKP_FLDR="$TMP_BKP_FLDR"/"$BKP_TYPE"
REMOTE_BKP_FLDR="$REMOTE_BKP_FLDR"/"$BKP_TYPE"

## backup files
TMP_IMG_BACKUP=images.tar.gz
TMP_DB_BACKUP=database.tar.gz
TMP_BKP_FILE="NEW_backup_$(date +%Y-%m-%d__%H_%M_%S).tar.gz"

# for ssh 
REMOTE_USERHOST="$REMOTE_USER"@"$REMOTE_HOST"

# for sftp
SFTP_COMMANDS="$TMP_BKP_FLDR"/sftp_commands.txt

# tmp
export TMP_BKP_DB_FULL="$TMP_BKP_FLDR"/"$TMP_DB_BACKUP"
export TMP_BKP_IMGS_FULL="$TMP_BKP_FLDR"/"$TMP_IMG_BACKUP"
export TMP_BKP_FILE_FULL="$TMP_BKP_FLDR/$TMP_BKP_FILE"


echo " - computed variables:"
echo "  > TMP_BKP_FLDR: $TMP_BKP_FLDR"
echo "  > REMOTE_BKP_FLDR: $REMOTE_BKP_FLDR"
echo "  > TMP_IMG_BACKUP: $TMP_IMG_BACKUP"
echo "  > TMP_DB_BACKUP: $TMP_DB_BACKUP"
echo "  > TMP_BKP_FILE: $TMP_BKP_FILE"
echo "  > REMOTE_USERHOST: $REMOTE_USERHOST"
echo "  > SFTP_COMMANDS: $SFTP_COMMANDS"
echo "  > VIZ_APP_FLDR: $VIZ_APP_FLDR"
echo "  > TMP_BKP_DB_FULL: $TMP_BKP_DB_FULL"
echo "  > TMP_BKP_IMGS_FULL: $TMP_BKP_IMGS_FULL"
echo "  > TMP_BKP_FILE_FULL: $TMP_BKP_FILE_FULL"



#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### CHECKS
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
if [ ! -d "$SERVER_FLDR" ]; then
	echo " - server folder not found: $SERVER_FLDR"
	exit 1
fi
if [ ! -d "$VIZ_APP_FLDR" ]; then
	echo "VIZ_APP_FLDR folder does not exists: $VIZ_APP_FLDR"
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
if [ -d "$TMP_BKP_FLDR" ]; then
	echo " - you dont have the required permissions to work on this server"
	exit 1
fi
mkdir -p "$TMP_BKP_FLDR"
if [ ! -d "$TMP_BKP_FLDR" ]; then
	echo " - failed to create the tmp folder: $TMP_BKP_FLDR"
	exit 1
fi


#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### BACKUP CREATION
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

cd "$VIZ_APP_FLDR"
source scripts/"$BKP_TYPE"_dump.sh


#### create single backup
#### ----- ----- ----- ----- ----- ----- ----- ----- -----

cd "$TMP_BKP_FLDR"
tar -zcf "$TMP_BKP_FILE" "$TMP_DB_BACKUP" "$TMP_IMG_BACKUP"
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
ssh -i "$PRIVATE_KEY" "$REMOTE_USERHOST" "bash -s" -- < scripts/remote_prepare.sh "$REMOTE_BKP_FLDR"
if [ $? -ne 0 ]; then
	echo "ssh exited with status not 0"
	exit 1
fi


#### upload
#### ----- ----- ----- ----- ----- ----- ----- ----- -----

echo "- generating FTP batch file: $SFTP_COMMANDS"

## generate ftp command file
cd "$TMP_BKP_FLDR"
rm -f "$SFTP_COMMANDS"
echo "cd  $REMOTE_BKP_FLDR" >  "$SFTP_COMMANDS"
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

echo "-------------------------------------------------------------------"
echo "dump.sh end . . $(date)"
echo "-------------------------------------------------------------------"

exit 0
