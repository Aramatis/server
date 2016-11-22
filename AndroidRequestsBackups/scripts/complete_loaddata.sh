#!/bin/bash


cd "$BACKUP_FOLDER"
cd tmp/db

# check dump
echo " - checking for JSON dump"
if [ ! -e database.sql ]; then
	echo "database.sql not found.. File extraction failed" 
	exit_and_free
fi

# load queries
echo " - loading records"
#sudo -u postgres dropdb "$DATABASE_NAME"
#sudo -u postgres psql createdb -T template0 "$DATABASE_NAME"
sudo -u postgres psql "$DATABASE_NAME" < database.sql


# copy images
echo " - copying images from $BACKUP_FOLDER/tmp/imgs to $IMGS_FLDR" 
cd "$BACKUP_FOLDER"
cd tmp
if [ "$(ls -A imgs/)" ]; then
    cp -arn imgs/* "$IMGS_FLDR"
else
    echo " - no images found"
fi
