# VisualizationBackupApp
It performs db backups for the visualization server. Complete backups are scheduled on a daily basis and diff backups run every 5 minutes.


```python

INSTALLED_APPS = (
	...
	'django_crontab',
	'VisualizationBackupApp',
	...
)


CRONJOBS = [
	
	# ONLY ON SOURCE SERVER
	# daily and partial backups to remote server
    ('0 */1 * * *', 'VisualizationBackupApp.jobs.complete_dump', '> /tmp/vizbkpapp_complete_dump_log.txt')
    ('0 */1 * * *', 'VisualizationBackupApp.jobs.partial_dump',  '> /tmp/vizbkpapp_partial_dump_log.txt')

    # ONLY ON REMOTE SERVER
    # daily and partial loaddata jobs on remote server
    ('0 */1 * * *', 'VisualizationBackupApp.jobs.complete_loaddata', '> /tmp/vizbkpapp_complete_loaddata_log.txt')
    ('0 */1 * * *', 'VisualizationBackupApp.jobs.partial_loaddata',  '> /tmp/vizbkpapp_partial_loaddata_log.txt')
]

# is this really required??
CRONTAB_LOCK_JOBS = True
```


# "This script must be called by root."

# 1.- VIZ_APP_FLDR
# This script must be called with the parameter VIZ_APP_FLDR
# VIZ_APP_FLDR represents the full path to the VisualizationBackupApp.
# VIZ_APP_FLDR folder does not exists: $VIZ_APP_FLDR

# 2.- REMOTE_USER
# This script must be called with the parameter REMOTE_USER
# REMOTE_USER is the user name of the remote machine. e.g: transapp

# 3.- REMOTE_HOST
# This script must be called with the parameter REMOTE_HOST
# REMOTE_HOST is the name remote machine. e.g: 104.236.183.105

# 4.- REMOTE_BKP_FLDR
# This script must be called with the parameter REMOTE_BKP_FLDR
# REMOTE_BKP_FLDR is the path to the folder where backups are stored
# on the remote machine. e.g: ftp_incoming
# Any file oder than 15 days on this folder will be deleted!!

# 5.- PRIVATE_KEY
# This script must be called with the parameter PRIVATE_KEY
# PRIVATE_KEY is the file with this server private key, used
# to connect to the remote host. e.g: /home/server/.ssh/id_rsa
# The PRIVATE_KEY key file does not exists: $PRIVATE_KEY

# 6.- TMP_BKP_FLDR
# This script must be called with the parameter TMP_BKP_FLDR
# TMP_BKP_FLDR is the path to the folder where backups are built
# on this server. e.g: /tmp/backup_viz
# at some point, this folder will be completely deleted, so ensure
# this is not something important!, like '/home' or '/'.
