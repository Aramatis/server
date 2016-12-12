# ----------------------------------------------------------------------------
# VIZ_BACKUP_APP
# see also: AndroidRequestsBackups/REAME.md
ANDROID_REQUESTS_BACKUPS = {
		
	# (TranSapp) related parameters
	# Folder to use for tmp processing (full path).
	# At some point, this folder can be completely deleted, so ensure
	# this is not something important!, like '/home' or '/'."
	'TMP_BKP_FLDR' : '/tmp/backup_viz',


	# (TranSappViz) related parameters
	# Folder (full path) where to put backups on remote (TranSappViz) server.
	# Any file older than ANDROID_REQUESTS_BACKUPS['BKPS_LIFETIME'] days
	# will be deleted!
	# This value MUST match the one on the other server!, otherwise
	# really bad stuff might happen
	'REMOTE_BKP_FLDR' : '<REPLACE_HOME>/bkps',

	# Amount of minutes to send to the remote (TranSappViz) server.
	# This value MUST match the one on the other server!, otherwise
	# some data can be lost
	'TIME' : 5,

	# remote (TranSappViz) server credentials.
	# - private key: used to access the remote
	# - remote host: IP of the remote host
	# - remote user: username on the remote
	'PRIVATE_KEY' : '<REPLACE_HOME>/.ssh/id_rsa',
	'REMOTE_HOST' : 'myhost',
	'REMOTE_USER' : 'myuser',

	# testing
	'TEST_USER'      : '<REPLACE_USER>',
	'TEST_USER_HOME' : '<REPLACE_HOME>',
}
# ----------------------------------------------------------------------------

def android_requests_backups_update_jobs(cronjobs):

	# schedule daily complete backup at 3:30am
	cronjobs.append(
		('30  3 * * *', 'AndroidRequestsBackups.jobs.complete_dump',
		'> /tmp/android_request_bkps_complete_dump_log.txt')
	)

	# partial backups every 5 minutes
	cronjobs.append(
		('*/5 * * * *', 'AndroidRequestsBackups.jobs.partial_dump',
		'> /tmp/android_request_bkps_partial_dump_log.txt'),
	)

	# remote connection checker
	cronjobs.append(
		('0 */1 * * *', 'AndroidRequestsBackups.jobs.ssh_sftp_checker',
		 '> /tmp/android_request_bkps_ssh_sftp_checker_log.txt'),
	)

	return cronjobs