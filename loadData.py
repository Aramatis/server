#!/usr/bin/python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from Loaders.LoaderFactory import LoaderFactory
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()


# HOW TO USE IT
# run the script giving the parameters by command line
# the parameters must be the name of the model and the paths to the csv files with the data
# EX: python loadData.py busstop InitialData/busstops.csv service
# InitialData/services.csv servicesbybusstop
# InitialData/servicesbybusstop.csv servicestopdistance
# InitialData/servicestopdistance.csv ServiceLocation
# InitialData/servicelocation.csv event InitialData/events.csv


factory = LoaderFactory()
log = open('loadDataError.log', 'w+')
for i in range(1, len(sys.argv), 2):
    csv = open(sys.argv[i + 1], 'r')  # path to csv file
    # skip header
    csv.next()
    loader = factory.getModelLoader(sys.argv[i])(csv, log)
    loader.load()
    csv.close()
log.close()
