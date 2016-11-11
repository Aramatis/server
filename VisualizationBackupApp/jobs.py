import subprocess
import os
from django.conf import settings

def _print_param_exception():
    print("MISSING SOME PARAMETERS FROM settings.py. MAKE SURE ALL " +
          "REQUIRED VIZ_BKP_APP_ STUFF EXISTS.")

def _run_script(filename, args=[]):

    # build command
    app_path = os.path.dirname(os.path.realpath(__file__))
    command = "bash " + app_path + "/scripts/" + filename
    for arg in args:
        command += " " + arg

    # call
    subprocess.call(command, shell=True)


def _retrieve_dump_params():
    try:
        element = (
            "dump.sh",
            [
                os.path.dirname(os.path.realpath(__file__)),
                settings.VIZ_BKP_APP_REMOTE_USER,
                settings.VIZ_BKP_APP_REMOTE_HOST,
                settings.VIZ_BKP_APP_REMOTE_BKP_FLDR,
                settings.VIZ_BKP_APP_PRIVATE_KEY,
                settings.VIZ_BKP_APP_TMP_BKP_FLDR,
                settings.VIZ_BKP_APP_IMGS_FLDR,
                settings.VIZ_BKP_APP_HOST_DATABASE
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
                settings.VIZ_BKP_APP_REMOTE_BKP_FLDR,
                settings.VIZ_BKP_APP_IMGS_FLDR,
                settings.VIZ_BKP_APP_REMOTE_DATABASE,
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
        params.append(settings.VIZ_BKP_APP_TIME)
        _run_script(filename, params)

    except Exception as e:
        _print_param_exception()
        raise e


def complete_loaddata():
    try:
        filename, params = _retrieve_load_params()
        params.append(settings.VIZ_BKP_APP_BKPS_LIFETIME)
        params.append("complete")
        _run_script(filename, params)

    except Exception as e:
        _print_param_exception()
        raise e


def partial_loaddata():
    filename, params = _retrieve_load_params()
    params.append("2")       # keep backups at most two days
    params.append("partial")
    _run_script(filename, params)
