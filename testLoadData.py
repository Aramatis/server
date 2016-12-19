# -*- coding: utf-8 -*-
from django.test import TestCase 
import os, subprocess
from loadData import loadData

class LoadInitialDataTest(TestCase):

    def setUp(self):
        ''' this method will automatically call for every single test at the beginning'''
        self.CURRENT_PATH = os.path.dirname(os.path.realpath('__file__'))
        self.FILE_PATH = os.path.join(self.CURRENT_PATH, 'InitialData/')
        self.TEST_FILE_NAME = os.path.join(self.CURRENT_PATH, 'test.csv')

    def tearDown(self):
        ''' this method will automatically call for every single test at the end '''
        os.remove(self.TEST_FILE_NAME)

    def createTestFile(self, fileName, addBadLine = False):
        ''' Create a copy of $filePath with first $MAX_ROWS lines '''
        MAX_ROWS = 2
        newLines = []

        fileRef = open(os.path.join(self.FILE_PATH, fileName))

        index = 0
        for line in fileRef:
            if index == MAX_ROWS:
                break
            newLines.append(line)
            index += 1

        fileRef.close()

        newFile = open(self.TEST_FILE_NAME, 'w')
        for line in newLines:
            if addBadLine:
                newFile.write('TextInID' + line)
            else:
                newFile.write(line)
        newFile.close()

    def compareLogFile(self, logFileName, expectedLog):
        ''' compare log file with the expected error '''
        logFile = open(os.path.join(self.CURRENT_PATH, logFileName)).read()
        self.assertEqual(logFile, expectedLog)
        os.remove(logFileName)

    """
    DON'T UNCOMMENT, THIS COMMAND USE REAL DATABASE, IT'S WRONG
    def test_execLoadDataFromCommandLine(self):
        ''' exec loadData from command line '''
        command = "python " + os.path.join(self.CURRENT_PATH, 'loadData.py')
        subprocess.call(command, shell = True)
    """

    def test_loadBusStopsWithoutProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''

        FILE_NAME = 'busstop.csv'
        self.createTestFile(FILE_NAME)

        loadData(['busstop', self.TEST_FILE_NAME])

    def test_loadBusStopsWithProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''
        
        FILE_NAME = 'busstop.csv'
        self.createTestFile(FILE_NAME, addBadLine = True)

        LOG_FILE_NAME = 'test.log'
        loadData(['busstop', self.TEST_FILE_NAME], logFileName = LOG_FILE_NAME)
        
        EXPECTED_LOG = "=========================================\n"\
        "Exception: el valor es demasiado largo para el tipo character varying(6)\n"\
        "Loader: BusStop\n"\
        "Data columns: code,name,lat,lon\n"\
        "Values: TextInIDAG;Camino Agrícola;-33.49158577;-70.61753772\n"\
        "=========================================\n"

        self.compareLogFile(LOG_FILE_NAME, EXPECTED_LOG)

    def test_loadEventsWithoutProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''

        FILE_NAME = 'events.csv'
        self.createTestFile(FILE_NAME)

        loadData(['event', self.TEST_FILE_NAME])

    def test_loadEventsWithProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''
        
        FILE_NAME = 'events.csv'
        self.createTestFile(FILE_NAME, addBadLine = True)

        LOG_FILE_NAME = 'test.log'
        loadData(['event', self.TEST_FILE_NAME], logFileName = LOG_FILE_NAME)
        
        EXPECTED_LOG = "=========================================\n"\
        "Exception: el valor es demasiado largo para el tipo character varying(8)\n"\
        "Loader: Event\n"\
        "Data columns: id,eventType,category,origin,name,description,lifespam\n"\
        "Values: TextInIDevn00000;busStop;buses Juntos;o;2 juntos;2 buses pasan juntos ;1440\n"\
        "=========================================\n"\

        self.compareLogFile(LOG_FILE_NAME, EXPECTED_LOG)

    def test_loadRoutesWithoutProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''

        FILE_NAME = 'routes.csv'
        self.createTestFile(FILE_NAME)

        loadData(['route', self.TEST_FILE_NAME])

    def test_loadRoutesWithProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''
        
        FILE_NAME = 'routes.csv'
        self.createTestFile(FILE_NAME, addBadLine = True)

        LOG_FILE_NAME = 'test.log'
        loadData(['route', self.TEST_FILE_NAME], logFileName = LOG_FILE_NAME)
        
        EXPECTED_LOG = "=========================================\n"\
        "Exception: el valor es demasiado largo para el tipo character varying(11)\n"\
        "Loader: Route\n"\
        "Data columns: serviceCode,latitude,longitude,sequence\n"\
        "Values: TextInID101I;-33.406175;-70.623244;1\n"\
        "=========================================\n"\

        self.compareLogFile(LOG_FILE_NAME, EXPECTED_LOG)

    def test_loadServiceLocationWithoutProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''

        FILE_NAME = 'servicelocation.csv'
        self.createTestFile(FILE_NAME)

        loadData(['servicelocation', self.TEST_FILE_NAME])

    def test_loadServiceLocationWithProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''
        
        FILE_NAME = 'servicelocation.csv'
        self.createTestFile(FILE_NAME, addBadLine = True)

        LOG_FILE_NAME = 'test.log'
        loadData(['servicelocation', self.TEST_FILE_NAME], logFileName = LOG_FILE_NAME)
        
        EXPECTED_LOG = "=========================================\n"\
        "Exception: el valor es demasiado largo para el tipo character varying(11)\n"\
        "Loader: ServiceLocation\n"\
        "Data columns: serviceName,distance,latitude,longitude\n"\
        "Values: TextInID101I;0;-33.406175;-70.623244\n"\
        "=========================================\n"\

        self.compareLogFile(LOG_FILE_NAME, EXPECTED_LOG)
