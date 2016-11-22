import subprocess
import os
from django.conf import settings

def _print_param_exception():
    print("MISSING SOME PARAMETERS FROM settings.py. MAKE SURE ALL " +
          "REQUIRED ANDROID_REQUESTS_BACKUPS_ STUFF EXISTS.")

def _run_script(filename, args=[]):

    # build command
    app_path = settings.BASE_DIR + "/AndroidRequestsBackups/"
    command = "bash " + app_path + "scripts/" + filename
    for arg in args:
        command += " " + arg

    # call
    subprocess.call(command, shell=True)


def _retrieve_dump_params():
    try:
        element = (
            "dump.sh",
            [
                settings.BASE_DIR,
                settings.ANDROID_REQUESTS_BACKUPS_REMOTE_USER,
                settings.ANDROID_REQUESTS_BACKUPS_REMOTE_HOST,
                settings.ANDROID_REQUESTS_BACKUPS_REMOTE_BKP_FLDR,
                settings.ANDROID_REQUESTS_BACKUPS_PRIVATE_KEY,
                settings.ANDROID_REQUESTS_BACKUPS_TMP_BKP_FLDR,
                settings.MEDIA_IMAGE,
                settings.DATABASES['default']['NAME']
            ]
        )
        return element
    except Exception as e:
        _print_param_exception()
        raise e


def _retrieve_load_params():
    try:
        element = (
            "loaddata.sh",
            [
                settings.BASE_DIR,
                settings.ANDROID_REQUESTS_BACKUPS_REMOTE_BKP_FLDR,
                settings.MEDIA_IMAGE,
                settings.DATABASES['default']['NAME']
            ]
        )
        return element
    except Exception as e:
        _print_param_exception()
        raise e

def complete_dump():
    filename, params = _retrieve_dump_params()
    params.append("complete")
    _run_script(filename, params)


def partial_dump():
    try:
        filename, params = _retrieve_dump_params()
        params.append("partial")
        params.append(settings.ANDROID_REQUESTS_BACKUPS_TIME)
        _run_script(filename, params)

    except Exception as e:
        _print_param_exception()
        raise e


def complete_loaddata():
    try:
        filename, params = _retrieve_load_params()
        params.append(settings.ANDROID_REQUESTS_BACKUPS_BKPS_LIFETIME)
        params.append("complete")
        _run_script(filename, params)

    except Exception as e:
        _print_param_exception()
        raise e


def partial_loaddata():
    try:
        filename, params = _retrieve_load_params()
        params.append("2")       # keep backups at most two days
        params.append("partial")
        params.append(settings.ANDROID_REQUESTS_BACKUPS_TIME)
        _run_script(filename, params)

    except Exception as e:
        _print_param_exception()
        raise e
