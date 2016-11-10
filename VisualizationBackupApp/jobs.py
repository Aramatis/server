import subprocess
import os
from django.conf import settings


def _run_script(filename, args = []):

    # build command
    app_path = os.path.dirname(os.path.realpath(__file__))
    command = "bash " + app_path + "/scripts/" + filename
    for arg in args:
        command += " " + arg

    # call
    subprocess.call(command, shell=True)


def _retrieve_dump_params():
    try:
        element =("dump.sh",[os.path.dirname(os.path.realpath(__file__)),
            settings.VIZ_BKP_APP_REMOTE_USER,
            settings.VIZ_BKP_APP_REMOTE_HOST,
            settings.VIZ_BKP_APP_REMOTE_BKP_FLDR,
            settings.VIZ_BKP_APP_PRIVATE_KEY,
            settings.VIZ_BKP_APP_TMP_BKP_FLDR,
            settings.VIZ_BKP_APP_IMGS_FLDR,
            settings.VIZ_BKP_APP_DATABASE]
        )
        print element
        return element
    except Exception as e:
        print("MISSING SOME PARAMETERS FROM settings.py. MAKE SURE ALL " +
                "REQUIRED VIZ_BKP_APP_ STUFF EXISTS.")
        raise e


def complete_dump():
    filename, params = _retrieve_dump_params()
    params.append("complete")
    _run_script(filename, params)


def partial_dump():
    print "vivo"
    try:
        filename, params = _retrieve_dump_params()
        params.append("partial")
        print settings.VIZ_BKP_APP_TIME
        params.append(settings.VIZ_BKP_APP_TIME)
        print "dead"
        _run_script(filename,params)
    except Exception as e:
        print("MISSING SOME PARAMETERS FROM settings.py. MAKE SURE ALL " +
                "REQUIRED VIZ_BKP_APP_ STUFF EXISTS.")
        raise e
    


def partial_loaddata():
    _run_script("partial_loaddata.sh")

print 1