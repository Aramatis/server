# VisualizationBackupApp

This app performs database backups from the (TranSapp) server and loads them to the (TranSappViz) server. So, this app is designed to be used on two servers, the Sender (TranSapp) and the Receiver (TranSappViz) of backups, both using the AndroidRequests models.

It provides two backup types, complete and partial, which are designed to be scheduled on a daily basis (long period of time) and diff backups run some minutes (short period of time), respectively.

The processing pipeline is as follows:

- (TranSapp): Dump database tables to one `.sql` file (complete) or multiple `.json` files (one for each table)
- (TranSapp): Copy the related media files
- (TranSapp): Compress all and send it through sftp.
- (TranSappViz): Check for new data, otherwise, finish.
- (TranSappViz): Decompress files.
- (TranSappViz): Load to database and media folders.
- (TranSappViz): Performs database postprocessing stuff. 

Complete and partial backups only differ on the amount of data that is sent. Complete backups performs a complete database dump, but partial only take into account the latest M minutes of data and only from AndroidRequests models which might have changed.


## Project Setup

For each server, you must add the following apps to the project `settings.py` file.

```python
INSTALLED_APPS = (
	# ...
	'django_crontab',
	'VisualizationBackupApp',
)
```

## Scheduling

Backups needs to be scheduled on the `settings.py` file, using the cron app. 

On (TranSapp), the recommended setting is to schedule complete backups once a day and partial backups every 5 minutes.
```python
# ONLY ON (TranSapp)
CRONJOBS = [	
    # daily complete backup at 3:30am
    ('30  3 * * *', 'VisualizationBackupApp.jobs.complete_dump', '> /tmp/vizbkpapp_complete_dump_log.txt')
    
    # partial backups every 5 minutes
    ('*/5 * * * *', 'VisualizationBackupApp.jobs.partial_dump',  '> /tmp/vizbkpapp_partial_dump_log.txt')
]
```

On (TranSappViz), the recommended setting is to schedule a lot of update checkings, this way new updates are applied as soon as possible (it's super duper free to fail if there aren't updates, assuming you are not scheduling a check every second).
```python
# ONLY ON (TranSappViz)
CRONJOBS = [	
    # check for complete updates every one hour
    ('0 */1 * * *', 'VisualizationBackupApp.jobs.complete_loaddata', '> /tmp/vizbkpapp_complete_loaddata_log.txt')
    
    # check for partial updates every 2 minutes
    ('*/2 * * * *', 'VisualizationBackupApp.jobs.partial_loaddata',  '> /tmp/vizbkpapp_partial_loaddata_log.txt')
]
```
You can see the process log on the `/tmp/vizbkpapp_*_log.txt` files.

Note that is highly recommended to set the parameter `CRONTAB_LOCK_JOBS = True` on `settings.py`. This is not mandatory, but unexpected stuff might happen otherwise!.

See also [this wiki](https://en.wikipedia.org/wiki/Cron#Format) on how to write a schedule using the cron format. 


## Settings TODO:
 
```
1.- VIZ_APP_FLDR
This script must be called with the parameter VIZ_APP_FLDR
VIZ_APP_FLDR represents the full path to the VisualizationBackupApp.
VIZ_APP_FLDR folder does not exists: $VIZ_APP_FLDR

2.- REMOTE_USER
This script must be called with the parameter REMOTE_USER
REMOTE_USER is the user name of the remote machine. e.g: transapp

3.- REMOTE_HOST
This script must be called with the parameter REMOTE_HOST
REMOTE_HOST is the name remote machine. e.g: 104.236.183.105

4.- REMOTE_BKP_FLDR
This script must be called with the parameter REMOTE_BKP_FLDR
REMOTE_BKP_FLDR is the path to the folder where backups are stored
on the remote machine. e.g: ftp_incoming
Any file oder than 15 days on this folder will be deleted!!

5.- PRIVATE_KEY
This script must be called with the parameter PRIVATE_KEY
PRIVATE_KEY is the file with this server private key, used
to connect to the remote host. e.g: /home/server/.ssh/id_rsa
The PRIVATE_KEY key file does not exists: $PRIVATE_KEY

6.- TMP_BKP_FLDR
This script must be called with the parameter TMP_BKP_FLDR
TMP_BKP_FLDR is the path to the folder where backups are built
on this server. e.g: /tmp/backup_viz
at some point, this folder will be completely deleted, so ensure
this is not something important!, like '/home' or '/'.
```

## Finally, setting up the jobs

This must be done with root privileges, because we want to access the databases, drop them and create new ones on (TranSappViz), and finally, because all files on (TranSapp) can be only modified by root.

So, we need remove outdated jobs, and add the new ones. Open a terminal and type:
```(bash)
cd <path to the server folder>

# remove and update this app jobs for root user
sudo -u root python manage.py crontab remove
sudo -u root python manage.py crontab add
```

You can check the all the jobs an user owns this way. Only make sure `root` owns our jobs. Open a terminal and type:
```(bash)
sudo -u <username> python manage.py crontab add 

sudo -u root python manage.py crontab add 
```



