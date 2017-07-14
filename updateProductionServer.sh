#!/bin/bash

#####################################################################
# COMMAND LINE INPUT
#####################################################################
if [ -z "$1" ]; then
    echo "FYI: You have to specify a tag server version"
    exit 
fi

serverVersion=$1
fileVersion=${2:-0}

#####################################################################
# Check if we need to add key files in server project
#####################################################################
KEY_PATH=./server/keys
KEY_FILES=(
    admins.json
    DTPMConnectionParams.json
    google_key.json
    email_config.json
    secret_key.txt
    database_config.json
    android_requests_backups.py
    )

for FILE_NAME in "${KEY_FILES[@]}"
do
    if [ ! -f $KEY_PATH/$FILE_NAME ]; then
        echo "REMEBER TO ADD ALL KEY FILES IN THIS SERVER"
        echo "THE NEXT FILE COULD NOT FIND: $FILE_NAME"
        exit
    fi
done

#####################################################################
# Database backup
#####################################################################
DB_NAME="ghostinspector"
DATE=`date +%Y-%m-%d`
DUMP_NAME="dump$DATE\.sql"
sudo -u postgres pg_dump "$DB_NAME" > "$DUMP_NAME"
tar -zcvf ../"$DUMP_NAME\.tar.gz" "$DUMP_NAME"
rm "$DUMP_NAME"

#####################################################################
# Update repository
#####################################################################

git fetch 

# if tag exists -> update code
if git tag --list | egrep "^$serverVersion$"
then
	# stop server
	service apache2 stop
    # stash changes
    git stash 

    git checkout tags/"$serverVersion"
    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic --noinput

    # load data from fixture
    python manage.py loaddata levels scoreEvents

    # run test
    coverage run --source='.' manage.py test
    coverage report --omit=DataDictionary,server,AndroidRequestsBackups,AndroidRequests/migrations/* -m
    
    # apply changes not committed
    git stash apply

	# start server
    service apache2 start
else
    echo "FYI: Tag $serverVersion does not exists."
fi

#####################################################################
# Update data
#####################################################################

if [ "$fileVersion" -ne "0" ]
then
    python updateData.py "$fileVersion"
    echo "loading stop data ..."
    python loadData.py "$fileVersion" busstop InitialData/"$fileVersion"/busstop.csv 
    echo "loading trip data ..."
    python loadData.py "$fileVersion" service InitialData/"$fileVersion"/services.csv 
    echo "loading services by stop data ..."
    python loadData.py "$fileVersion" servicesbybusstop InitialData/"$fileVersion"/servicesbybusstop.csv 
    echo "loading service stop distance data ..."
    python loadData.py "$fileVersion" servicestopdistance InitialData/"$fileVersion"/servicestopdistance.csv
    echo "loading service location data ..."
    python loadData.py "$fileVersion" ServiceLocation InitialData/"$fileVersion"/servicelocation.csv
    echo "loading events data ..."
    python loadData.py "$fileVersion" event InitialData/events.csv
    #python loadData.py "$fileVersion" route InitialData/"$fileVersion"/routes.csv
else 
    echo "FYI: It was not updated data because file version was not given."
fi

