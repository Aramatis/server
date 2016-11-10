#!/bin/bash
#
# this script
# > it creates the ftp incomming folder if not exists
#
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


echo " - [ON REMOTE VIZ]: -------- PRE LOAD INIT --------"
exit 0