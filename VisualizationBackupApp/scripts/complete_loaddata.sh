#!/bin/bash


cd "$BACKUP_FOLDER"
cd tmp/db

# check dump
echo " - checking for JSON dump"
if [ ! -e database.sql ]; then
	echo "database.sql not found.. File extraction failed" 
	exit 1
fi

# load queries
echo " - loading records"
#sudo -u postgres dropdb ghostinspector
#sudo -u postgres psql createdb -T template0 ghostinspector
sudo -u postgres psql ghostinspector < database.sql


# copy images
echo " - copying images from $BACKUP_FOLDER/tmp/imgs to $IMGS_FLDR" 
cd "$BACKUP_FOLDER"
cd tmp
cp -arn imgs/* "$IMGS_FLDR"
