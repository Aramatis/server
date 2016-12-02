#!/usr/bin/python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib

# HOW TO USE IT
# run the script when you want to update base data
# Each time when you use this script, you have to check FILE_VERSION variable,
# this string has to match with the last version of files generated by
# GTFSProcessing

# latest updated version
FILE_VERSION = 'v0.6'

DATA_PATH = './InitialData'
URL_PREFIX = 'https://raw.githubusercontent.com/InspectorIncognito/GTFSProcessing/master/procesaGTFS/x64/Release'
FILE_EXTENSION = '.csv'
FILE_NAMES = [
    'busstop',
    'services',
    'servicesbybusstop',
    'servicestopdistance',
    'servicelocation']

downloader = urllib.URLopener()

for fileName in FILE_NAMES:
    savedFileName = DATA_PATH + '/' + fileName + FILE_EXTENSION
    url = '{}/{}'.format(URL_PREFIX, fileName + FILE_VERSION + FILE_EXTENSION)
    print "Downloading ... " + url
    downloader.retrieve(url, savedFileName)
    print 'updated ' + fileName + ' file'
