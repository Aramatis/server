#!/usr/bin/python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from Loaders.LoaderFactory import LoaderFactory
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

"""
 HOW TO USE IT
 run the script giving the parameters by command line
 the first parameter is the gtfs version followed by 
 pairs the name of the model and the paths to the csv files with the data

 EX: python loadData.py 'v0.7' busstop InitialData/v0.7/busstop.csv service InitialData/v0.7/services.csv servicesbybusstop InitialData/v0.7/servicesbybusstop.csv servicestopdistance InitialData/v0.7/servicestopdistance.csv ServiceLocation InitialData/v0.7/servicelocation.csv event InitialData/events.csv
"""
def loadData(args, logFileName = 'loadDataError.log'):
    ''' load csv data to database '''
    factory = LoaderFactory()
    log = open(logFileName, 'w+')
    gtfsVersion = args[0]
    for i in range(1, len(args)-1, 2):
        csv = open(args[i + 1], 'r')  # path to csv file
        # skip header
        csv.next()
        loader = factory.getModelLoader(args[i])(csv, log, gtfsVersion)
        loader.load()
        csv.close()
    log.close()

if __name__ == "__main__":
    ''' load data with data given by args '''
    sys.argv.pop(0)
    loadData(sys.argv)

