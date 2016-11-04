import subprocess
import os



def _run_script(filename):
	app_path = os.path.dirname(os.path.realpath(__file__))
	command = "bash " + app_path  + "/scripts/" + filename
	command = command + " " + app_path
	subprocess.call(command, shell=True)

def complete_dump():
	_run_script("dump.sh")

def partial_dump():
	_run_script("partial_dump.sh")

def complete_loaddata():
	_run_script("loaddata.sh")

def partial_loaddata():
	_run_script("partial_loaddata.sh")
