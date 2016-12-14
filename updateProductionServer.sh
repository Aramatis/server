#!/bin/bash

#####################################################################
# COMMAND LINE INPUT
#####################################################################
if [ -z "$1" ]; then
    echo "You have to specify a tag server version"
    exit 
fi

serverVersion=$1
fileVersion=${2:-0}

#####################################################################
# Update repository
#####################################################################

git fetch 

# if tag exists -> update code
if git tag --list | egrep "^$serverVersion$"
then
    git checkout tags/"$serverVersion"
    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic --noinput

    # replace path to the server project
    sed -i -e 's/\/server\//\/ubuntu\//g' server/wsgi.py

    # define DEBUG = FALSE
    sed -i -e 's/DEBUG = True/DEBUG = False/g' server/settings.py

    # run test
    coverage run --source='.' manage.py test
    coverage report --omit=DataDictionary,server,AndroidRequestsBackups -m
    
    service apache2 restart
else
    echo "FYI: Tag $serverVersion does not exists."
fi

#####################################################################
# Update data
#####################################################################

if [ "$fileVersion" -ne "0" ]
then
    python updateData.py "$fileVersion"
    python loadData.py busstop InitialData/busstop.csv 
    python loadData.py service InitialData/services.csv 
    python loadData.py servicesbybusstop InitialData/servicesbybusstop.csv 
    python loadData.py servicestopdistance InitialData/servicestopdistance.csv
    python loadData.py ServiceLocation InitialData/servicelocation.csv
    python loadData.py event InitialData/events.csv
    python loadData.py route InitialData/routes.csv
else 
    echo "FYI: It was not updated data because file version was not given."
fi

