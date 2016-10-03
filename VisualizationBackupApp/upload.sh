#!/bin/bash

APP_DIR="$1"
if [ -z "$APP_DIR" ]; then
	echo "This script must be called with the parameter APP_DIR"
	exit 1
fi
if [ ! -d "$APP_DIR" ]; then
	echo "APP_DIR folder does not exists: $APP_DIR"
	exit 1
fi
if [ "$USER" != "root" ]; then
	echo "This script must be called by root. Current user: $USER"
	exit 1
fi


KEY=/home/server/.ssh/id_rsa
HOST=server@172.17.57.188

THIS_FOLDER="$APP_DIR"
TEMPLATE="$THIS_FOLDER"/template.txt
COMMANDS="$THIS_FOLDER"/commands.txt

TMP_FOLDER=/tmp/backup_viz
mkdir -p "$TMP_FOLDER"

cd "$THIS_FOLDER/.."
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