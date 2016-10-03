import subprocess

def my_scheduled_job():
	subprocess.call("bash /home/server/Documents/server/VisualizationBackupApp/upload.sh", shell=True)