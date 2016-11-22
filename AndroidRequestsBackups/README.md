# AndroidRequestsBackups

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
	'AndroidRequestsBackups',
)
```

The `django-crontab` python package can be installed using: `pip install django-crontab`

To install the `AndroidRequestsBackups` app, simple clone this repository into each server root folder.


## Settings:

Also, you each server requires the following configurations on the `settings.py` file.

### On both servers

```python
## (TranSappViz) related parameters
# Folder (full path) where to put backups on remote (TranSappViz) server.
# Any file older than ANDROID_REQUESTS_BACKUPS_BKPS_LIFETIME days
# will be deleted!
# This value MUST match the one on the other server!, otherwise
# really bad stuff might happen
ANDROID_REQUESTS_BACKUPS_REMOTE_BKP_FLDR = "/home/transapp/bkps"

# Amount of minutes to send to the remote (TranSappViz) server.
# This value MUST match the one on the other server!, otherwise
# some data can be lost
ANDROID_REQUESTS_BACKUPS_TIME            = "5"
```

- The database name used to fetch and load data is taken from the `settings.DATABASES['default']['NAME']` variable.
- Images to send are retrieved from the `settings.MEDIA_IMAGE` folder.

### On (TranSapp) server

```python
## (TranSapp) related parameters
# Folder to use for tmp processing (full path).
# At some point, this folder can be completely deleted, so ensure
# this is not something important!, like '/home' or '/'."
ANDROID_REQUESTS_BACKUPS_TMP_BKP_FLDR    = "/tmp/backup_viz"


# remote (TranSappViz) server credentials.
# - private key: used to access the remote
# - remote host: IP of the remote host
# - remote user: username on the remote
ANDROID_REQUESTS_BACKUPS_PRIVATE_KEY     = "/home/server/.ssh/id_rsa"
ANDROID_REQUESTS_BACKUPS_REMOTE_HOST     = "104.236.183.105"
ANDROID_REQUESTS_BACKUPS_REMOTE_USER     = "transapp"
```


### On (TranSappViz) server

```python
# Amount of days to keep "complete backup" files. Older files are deleted.
# This value is only valid for complete backups. Partial backups are only
# kept for 2 days
ANDROID_REQUESTS_BACKUPS_BKPS_LIFETIME   = "10"
```



## Scheduling

Backups needs to be scheduled on each `settings.py` file. The configuration depends on the working mode of each server. 

### The sender (TranSapp)

The recommended setting is to schedule complete backups once a day and partial backups every 5 minutes.

```python
# ONLY ON (TranSapp)
CRONJOBS = [	
    # daily complete backup at 3:30am
    ('30  3 * * *', 'AndroidRequestsBackups.jobs.complete_dump', '> /tmp/android_request_bkps_complete_dump_log.txt')
    
    # partial backups every 5 minutes
    ('*/5 * * * *', 'AndroidRequestsBackups.jobs.partial_dump',  '> /tmp/android_request_bkps_partial_dump_log.txt')
]
```  

### The receiver (TranSappViz)

The recommended setting is to schedule a lot of update checkings, this way new updates are applied as soon as possible (it's super duper free to fail if there aren't updates, assuming you are not scheduling a check every second). 

It is very important to keep the partial backup time interval AT MOST at a half of the `ANDROID_REQUESTS_BACKUPS_TIME` parameter, otherwise bkps will be stacked, which will result on a fixed update delay of `ANDROID_REQUESTS_BACKUPS_BKPS_LIFETIME` days (for complete bkps) or 2 days (for partial bkps).

```python
# ONLY ON (TranSappViz)
CRONJOBS = [	
    # check for complete updates every one hour
    ('0 */1 * * *', 'AndroidRequestsBackups.jobs.complete_loaddata', '> /tmp/android_request_bkps_complete_loaddata_log.txt')
    
    # check for partial updates every 2 minutes
    ('*/1 * * * *', 'AndroidRequestsBackups.jobs.partial_loaddata',  '> /tmp/android_request_bkps_partial_loaddata_log.txt')
]
```

### On both

On each server, you can see the process logs on the `/tmp/android_request_bkps_*_log.txt` files.


This app also requires to set the following `django-crontab` related parameters:

```python
CRONTAB_LOCK_JOBS = True        # this way, partial jobs will stack.
CRONTAB_COMMAND_SUFFIX = '2>&1' # this way, we can see error on log files.
```

See also [this wiki](https://en.wikipedia.org/wiki/Cron#Format) on how to write a schedule using the cron format. 


### Considerations:

Disk Space is a limited resource on Web Servers, so make sure not to fill them with garbage (i.e, backups). This can only happen on (TranSappViz), specially for complete backups, when they are scheduled to be run too often (like hours, minutes.) and when the `ANDROID_REQUESTS_BACKUPS_BKPS_LIFETIME` variable is too large.

At the moment, (TranSappViz) has a 20GB disk, and each complete backup ... ...


## Finally, setting up the jobs

This must be done with root privileges on both servers. On both (TranSapp) and (TranSappViz), we need to access the database as the postgres user to perform dumps and loads. Also, some (TranSapp) server files can only be modified by root.

So, we need to remove outdated jobs, and add the new ones. Open a terminal and type:
```(bash)
cd <path to the server folder>

# remove and update this app jobs for root user
sudo -u root python manage.py crontab remove
sudo -u root python manage.py crontab add
```

You can check the all the jobs an user owns this way. Only make sure only the `root` owns the `AndroidRequestsBackups` jobs. Open a terminal and type:
```(bash)
sudo -u <username> python manage.py crontab show

sudo -u root python manage.py crontab show
```

## Future Work

- Decouple the postprocessing script call from the (TranSappViz) code (do not use a direct call to `transform.py`)
- Consider migrating to a queue based architecture. See also: "ETL Queues" on google.

