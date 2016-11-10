#!/bin/bash










# check tar.gz files
if [ ! -e database.sql ]; then
	echo "database.sql not found.. File extraction failed" 
	exit 1
fi

# copy images
echo " - [ON REMOTE VIZ]: copying images from $BACKUP_FOLDER/tmp/imgs to $DEST_IMG_FLDR" 
cp -arn imgs/* "$DEST_IMG_FLDR"

# load data
echo " - [ON REMOTE VIZ]: loading backup to database using $MANAGE_PY"
touch working.lock
sudo -u postgres psql dropdb ghostinspector
sudo -u postgres psql createdb -T template0 ghostinspector
nohup sudo -u postgres psql ghostinspector < database.sql && rm working.lock & 
#nohup /home/transapp/visualization/venv/bin/python "$MANAGE_PY" loaddata data.json && rm working.lock &  


