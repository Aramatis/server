#!/bin/bash

#### #### #### #### #### #### #### #### #### #### #### #### #### #### 
#### BACKUP CREATION
#### #### #### #### #### #### #### #### #### #### #### #### #### #### 

#### create image backup
#### ----- ----- ----- ----- ----- ----- ----- ----- -----
echo "- creating reports images backup"
cd "$IMGS_FLDR"
tar -zcvf "$TMP_BKP_IMGS_FULL" ./*
if [ ! -e "$TMP_BKP_IMGS_FULL" ]; then
	echo " - image backup file not found, but it should exists!: $TMP_BKP_IMGS_FULL"
	exit 1
fi


#### create database backup
#### ----- ----- ----- ----- ----- ----- ----- ----- -----

## dump
echo "- creating complete backup ..."
cd "$TMP_BKP_FLDR"
sudo -u postgres pg_dump "$DATABASE_NAME" > "$TMP_DB_DUMP_FULL"
if [ ! -e "$TMP_DB_DUMP_FULL" ]; then
	echo "UPS!.. The db dump file was not found. Maybe, the pg_dump command failed!."
	echo "Required file: $TMP_DB_DUMP_FULL"
	exit 1
fi

## compress
tar -zcvf "$TMP_DB_BACKUP" "$TMP_DB_DUMP"
echo "- looking for db backup results ..."
if [ ! -e "$TMP_BKP_DB_FULL" ]; then
	echo "UPS!.. The db backup file was not found."
	echo "Required file: $TMP_BKP_DB_FULL"
	exit 1
fi
