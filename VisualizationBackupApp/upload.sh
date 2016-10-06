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
if ! [ $(id -u) = 0 ] ; then
	echo "This script must be called by root."
	exit 1
fi

echo "---------------------------------------------------------------"
echo "upload.sh init" $(date)
echo "---------------------------------------------------------------"


KEY=/home/server/.ssh/id_rsa
HOST=server@172.17.57.188

THIS_FOLDER="$APP_DIR"
TEMPLATE="$THIS_FOLDER"/template.txt
COMMANDS="$THIS_FOLDER"/commands.txt

echo "- preparing environment ..."
TMP_FOLDER=/tmp/backup_viz
mkdir -p "$TMP_FOLDER"
cd "$THIS_FOLDER/.."

echo "creating reports image backups"
cd media
IMAGE_BACKUP=reported_images
sudo rm -f "$IMAGE_BACKUP".zip 
sudo zip -r "$IMAGE_BACKUP"{.zip,}
sudo mv "$IMAGE_BACKUP".zip /tmp/backup_viz/"$IMAGE_BACKUP".zip
cd "$THIS_FOLDER/.."

echo "- creating backup ..."
python manage.py archive

echo "- looking for backup results ..."
FILE=`find $TMP_FOLDER -type f -name 'backup_*.tar.bz2' -printf "%f\n"`
THE_FILE="$TMP_FOLDER/$FILE"
echo "found FILE = $FILE"
echo "found THE_FILE = $THE_FILE"

if [ ! -z "$FILE" ]; then
	
	echo "- found $THE_FILE"

	echo "- generating FTP batch file: $COMMANDS"
	## generate ftp command file
	rm -rf "$COMMANDS"
	cp "$TEMPLATE" "$COMMANDS"
	echo "put $THE_FILE" >> "$COMMANDS"
	echo "put $TMP_FOLDER/$IMAGE_BACKUP.zip" >> "$COMMANDS"

	echo "- sending file"
	## send
	# TODO: check sended file
	sftp -p -i "$KEY" -b "$COMMANDS" "$HOST"

	# ## delete
	echo "- deleting stuff"
	if [ -d "$TMP_FOLDER" ]; then
		if [ -e "$THE_FILE" ]; then
			cd "$TMP_FOLDER"
			rm -rf "$THE_FILE"
		else
			echo "UPS! backup file not found ... delete aborted"
		fi
		if [ -e "$IMAGE_BACKUP".zip ]; then
			cd "$TMP_FOLDER"
			rm -rf "$IMAGE_BACKUP".zip
		else
			echo "UPS! backup images file not found ... delete aborted"
		fi
	else
		echo "UPS! $TMP_FOLDER not found.. delete aborted"
	fi

	#echo "- here load the data  ..."

else
	echo "UPS!.. The backup file was not found. Probably, the 'python manage.py archive' command failed"
fi

echo "-------------------------------------------------------------------"
echo "upload.sh end"
echo "-------------------------------------------------------------------"