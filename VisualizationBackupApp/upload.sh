#!/bin/bash

KEY=/home/server/.ssh/id_rsa
HOST=server@172.17.57.188

THIS_FOLDER=/home/server/Documents/server/VisualizationBackupApp
TEMPLATE="$THIS_FOLDER"/template.txt
COMMANDS="$THIS_FOLDER"/commands.txt

TMP_FOLDER=/tmp/backup_viz
mkdir -p "$TMP_FOLDER"

cd /home/server/Documents/server
python manage.py archive

FILE=`find $TMP_FOLDER -type f -name 'backup_*.tar.bz2' -printf "%f\n"`
THE_FILE="$TMP_FOLDER/$FILE"
echo "THE_FILE = $THE_FILE"
echo "FILE = $FILE"

if [ ! -z "$FILE" ]; then
	
	echo "Found $THE_FILE"

	echo "Generating FTP batch file: $COMMANDS"
	## generate ftp command file
	rm -rf "$COMMANDS"
	cp "$TEMPLATE" "$COMMANDS"
	echo "put $THE_FILE" >> "$COMMANDS"

	echo "Sending file"
	## send
	# TODO: check sended file
	sftp -p -i "$KEY" -b "$COMMANDS" "$HOST"

	# ## delete
	echo "Deleting stuffffffff"
	if [ -d "$TMP_FOLDER" ]; then
		if [ -e "$THE_FILE" ]; then
			cd "$TMP_FOLDER"
			rm -rf "$THE_FILE"
		fi
	fi
else
	echo "The backup file was not found. Probably, the 'python manage.py archive' command failed"
fi