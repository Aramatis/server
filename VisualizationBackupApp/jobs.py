import subprocess
import os
from django.conf import settings


def _run_script(filename, *args):
	app_path = os.path.dirname(os.path.realpath(__file__))
	command = "bash " + app_path  + "/scripts/" + filename
	command = command + " " + app_path
	for arg in list(args):
		command = command +" "+ arg
	subprocess.call(command, shell=True)
	

def complete_dump():
	try:
		VIZ_APP_FLDR = os.path.dirname(os.path.realpath(__file__))
		DATABASE_NAME   = settings.VIZ_BKP_APP_DATABASE
        REMOTE_USER     = settings.VIZ_BKP_APP_REMOTE_USER
        REMOTE_HOST     = settings.VIZ_BKP_APP_REMOTE_HOST
        REMOTE_BKP_FLDR = settings.VIZ_BKP_APP_REMOTE_BKP_FLDR
        PRIVATE_KEY     = settings.VIZ_BKP_APP_PRIVATE_KEY
        TMP_BKP_FLDR    = settings.VIZ_BKP_APP_TMP_BKP_FLDR
        IMGS_FLDR       = settings.VIZ_BKP_APP_IMGS_FLDR

        _run_script("dump.sh", VIZ_APP_FLDR, REMOTE_USER, REMOTE_HOST, REMOTE_BKP_FLDR, PRIVATE_KEY, TMP_BKP_FLDR, IMGS_FLDR, DATABASE_NAME)
        
    except Exception as e:
    	print "MISSING SOME PARAMETERS FROM settings.py. MAKE SURE ALL REQUIRED 'VIZ_BKP_APP_*' STUFF EXISTS"
        raise e

def partial_dump():
	_run_script("partial_dump.sh")

def complete_loaddata():
	_run_script("loaddata.sh")

def partial_loaddata():
	_run_script("partial_loaddata.sh")
