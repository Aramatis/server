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