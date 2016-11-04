#!/bin/bash
#
# this script
# > it creates the ftp incomming folder if not exists
# > it deletes all files older than 15 days
#
# assumptions:
# - ftp_incoming folder is only used for backup purposes
# - all data with more than 15 days will be deleted
BACKUP_FOLDER="$1"

echo " - [ON REMOTE VIZ]: -------- PRE LOAD INIT --------"

## CHECKS
# backup folder
if [   -z "$BACKUP_FOLDER" ]; then
	echo "Usage: $ bash script_pre.sh <BACKUP_FOLDER>"
	exit 1
fi


## WORK
FTP_FLDR=/home/"$USER"/"$BACKUP_FOLDER"

# create backup folder
echo " - [ON REMOTE VIZ]: creating folder for ftp files: $FTP_FLDR"
mkdir -p "$FTP_FLDR"

# delete old stuff older than 15 days
echo " - [ON REMOTE VIZ]: deleting files older than 15 days on: $FTP_FLDR"
if [ -d "$FTP_FLDR" ]; then
	find "$FTP_FLDR" -ctime +15 -type f -delete	
fi

echo " - [ON REMOTE VIZ]: -------- PRE LOAD INIT --------"
exit 0