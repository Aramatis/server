#!/usr/bin/python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()
from AndroidRequests.models import *

exacta509 = open(os.path.join(os.getcwd(), 'InitialData', '509I-parada-loc-exacta.csv'), 'w')
estima509 = open(os.path.join(os.getcwd(), 'InitialData', '509I-parada-loc-estima.csv'), 'w')
exacta314 = open(os.path.join(os.getcwd(), 'InitialData', '314I-parada-loc-exacta.csv'), 'w')
estima314 = open(os.path.join(os.getcwd(), 'InitialData', '314I-parada-loc-estima.csv'), 'w')
exacta509.write("latitude; longitude;name\n")
estima509.write("latitude; longitude;name\n")
exacta314.write("latitude; longitude;name\n")
estima314.write("latitude; longitude;name\n")
data = open(sys.argv[1], 'r')
data509 = []
data314 = []
for line in data:
	line.replace("\n", "")
	datos = line.split(";")
	datos[2] = datos[2].replace("\n", "").replace("\r", "")
	busStop = BusStop.objects.get(code=datos[0])
	if(datos[1]=="509I"):
		data509.append([datos[0], datos[1], datos[2]])
		exacta509.write(str(busStop.latitud) + ";"+ str(busStop.longitud) + ";" + datos[0] + "\n")
	else:
		data314.append([datos[0], datos[1], datos[2]])
		exacta314.write(str(busStop.latitud) + ";"+ str(busStop.longitud) + ";" + datos[0] + "\n")
exacta314.close()
exacta509.close()

for data in data509:
	serviceCode = "509I"
	ssd = round(int(data[2]), -1)
	try:
		location = ServiceLocation.objects.filter(service = serviceCode, distance = ssd)[0]
		estima509.write(str(location.latitud) + ";"+ str(location.longitud) + ";" + data[0] + "\n")
	except:
		print data
estima509.close()
for data in data314:
	serviceCode = "314I"
	ssd = round(int(data[2]), -1)
	try:
		location = ServiceLocation.objects.filter(service = serviceCode, distance = ssd)[0]
		estima314.write(str(location.latitud) + ";"+ str(location.longitud) + ";" + data[0] + "\n")
	
	except:
		print data
estima314.close()
