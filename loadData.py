#!/usr/bin/python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from Loaders.LoaderFactory import LoaderFactory
from Loaders.ModelLoaders import LoadEvents
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()


## HOW TO USE IT
## run the script giving the parameters by command line
## the parameters must be the name of the model and the paths to the csv files with the data
## EX: python loadData.py busstop InitialData/busstops.csv service InitialData/services.csv servicesbybusstop InitialData/servicesbybusstop.csv servicestopdistance InitialData/servicestopdistance.csv ServiceLocation InitialData/servicelocation.csv


log = open('loadDataError.log', 'w')
loadAllEvents = LoadEvents()
loadAllEvents.loadEvents()
ticks = [1000, 100, 1000, 5000, 50000]
for i in range(1, len(sys.argv), 2):
	csv = open(sys.argv[i+1], 'r') #path to Bus Stop csv file
	csv.next()
	factory = LoaderFactory()
	loader = factory.getModelLoader(sys.argv[i])(csv, log)
	loader.load(ticks[((i+1)/2-1)%len(ticks)])
	csv.close()