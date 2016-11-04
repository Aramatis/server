import subprocess
import os

def complete_backup():
	app_path = os.path.dirname(os.path.realpath(__file__))
	command = "bash " + app_path  + "/upload.sh"
	command = command + " " + app_path
	subprocess.call(command, shell=True)

def partial_backup():
	app_path = os.path.dirname(os.path.realpath(__file__))
	command = "bash " + app_path  + "/partial_upload.sh"
	command = command + " " + app_path
	subprocess.call(command, shell=True)
