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
	
	# ONLY ON BACKUP SOURCE
    ('0 */1 * * *', 'VisualizationBackupApp.jobs.complete_backup', '>> /tmp/log_backup_cron.txt')
    ('0 */1 * * *', 'VisualizationBackupApp.jobs.partial_backup',  '>> /tmp/log_backup_cron.txt')

    # ONLY ON REMOTE SERVER
    # TODO
]

# is this really required??
CRONTAB_LOCK_JOBS = True
```