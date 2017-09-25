#!/usr/bin/python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import os
import sys

def updateGTFSData(gtfsVersion):
    """ generate a folder with the gtfs version data """
    DATA_PATH = './InitialData'
    FILE_NAMES = [
        # (localName, webName)
        ('busstop.csv', 'busstop{}.csv'.format(gtfsVersion)),
        ('services.csv', 'services{}.csv'.format(gtfsVersion)),
        ('servicesbybusstop.csv', 'servicesbybusstop{}.csv'.format(gtfsVersion)),
        ('servicestopdistance.csv', 'servicestopdistance{}.csv'.format(gtfsVersion)),
        ('servicelocation.csv', 'servicelocation{}.csv'.format(gtfsVersion))]

    directory = "{}/{}".format(DATA_PATH, gtfsVersion)
    try: 
        print "creating directory '{}'".format(directory)
        os.mkdir(directory)
    except OSError:
        print "directory '{}' already exists...".format(directory)

    for fileName, webFileName in FILE_NAMES:
        filePath = "{}/{}/{}".format(DATA_PATH, gtfsVersion, fileName)

        if os.path.isfile(filePath):
            message = "file '{}' exists. Do you want to replace it?(yes/no)".format(fileName)
            answer = raw_input(message)
            if answer.lower() in ['yes', 'y']:
                downloadFile(fileName, webFileName, filePath)
            else:
                print "file '{}' skipped".format(fileName)
        else:
            downloadFile(fileName, webFileName, filePath)
     
def downloadFile(fileName, webFileName, filePath):
    """ download file from GTFSProcessing repository """
    URL_PREFIX = 'https://raw.githubusercontent.com/InspectorIncognito/GTFSProcessing/master/procesaGTFS/x64/Release'
    downloader = urllib.URLopener()

    url = '{}/{}'.format(URL_PREFIX, webFileName)
    print "downloading ... " + url
    downloader.retrieve(url, filePath)
    print "file '{}' updated".format(fileName)

if __name__ == "__main__":
    """ download new csv files by command line """
    if len(sys.argv) < 2:
        print "ERROR: You have to provided a GTFS version. For instance: v0.9"
    else:
        updateGTFSData(sys.argv[1])

