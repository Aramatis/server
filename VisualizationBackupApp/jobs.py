import subprocess
import os



def _run_script(filename, *args):
	app_path = os.path.dirname(os.path.realpath(__file__))
	command = "bash " + app_path  + "/scripts/" + filename
	command = command + " " + app_path
	for arg in list(args):
		command = command +" "+ arg
	subprocess.call(command, shell=True)
	

def complete_dump():
	VIZ_APP_FLDR = os.path.dirname(os.path.realpath(__file__))
	REMOTE_USER = "transapp"
	REMOTE_HOST = "104.236.183.105"
	REMOTE_BKP_FLDR = "ftp_incoming"
	PRIVATE_KEY = "/home/server/.ssh/id_rsa"
	TMP_BKP_FLDR = "/tmp/backup_viz"
	_run_script("dump.sh", VIZ_APP_FLDR, REMOTE_USER, REMOTE_HOST, REMOTE_BKP_FLDR, PRIVATE_KEY, TMP_BKP_FLDR)


def partial_dump():
	_run_script("partial_dump.sh")

def complete_loaddata():
	_run_script("loaddata.sh")

def partial_loaddata():
	_run_script("partial_loaddata.sh")
