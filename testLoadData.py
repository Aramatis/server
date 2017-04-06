# -*- coding: utf-8 -*-
from django.test import TestCase 
import os, subprocess
from loadData import loadData
from django.utils import timezone
from django.conf import settings

class LoadInitialDataTest(TestCase):

    def setUp(self):
        ''' this method will automatically call for every single test at the beginning'''
        self.CURRENT_PATH = os.path.dirname(os.path.realpath('__file__'))
        self.FILE_PATH = os.path.join(self.CURRENT_PATH, 'InitialData/test/')
        self.TEST_FILE_NAME = os.path.join(self.CURRENT_PATH, 'test.csv')

    def tearDown(self):
        ''' this method will automatically call for every single test at the end '''
        os.remove(self.TEST_FILE_NAME)

    def createTestFile(self, fileName, addBadLine = False):
        ''' Create a copy of $filePath with first $MAX_ROWS lines '''
        MAX_ROWS = 2
        newLines = []

        if fileName == 'events.csv':
            fileName = '../{}'.format(fileName)
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
                newFile.write('HI!IAmAnError' + line)
            else:
                newFile.write(line)
        newFile.close()

    def compareLogFile(self, logFileName, expectedLog):
        ''' compare log file with the expected error '''
        logFile = open(os.path.join(self.CURRENT_PATH, logFileName)).read()
        self.assertEqual(logFile, expectedLog)
        os.remove(logFileName)

    def assertLogFileNotEmpty(self, logFileName):
        ''' compare log file with the expected error '''
        logFile = open(os.path.join(self.CURRENT_PATH, logFileName)).read()
        self.assertNotEqual(logFile, "")
        os.remove(logFileName)

    def printFile(self, FileName):
        ''' print on command line the content inside test.csv '''
        print "============= BEGIN TEST FILE  =================="
        print open(os.path(self.CURRENT_PATH, FileName)).read()
        print "============== END TEST FILE ===================="

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

        loadData([settings.GTFS_VERSION, 'busstop', self.TEST_FILE_NAME])

    def test_loadBusStopsWithProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''
        
        FILE_NAME = 'busstop.csv'
        self.createTestFile(FILE_NAME, addBadLine = True)

        LOG_FILE_NAME = 'test.log'
        loadData([settings.GTFS_VERSION, 'busstop', self.TEST_FILE_NAME], logFileName = LOG_FILE_NAME)
        
        self.assertLogFileNotEmpty(LOG_FILE_NAME)

    def test_loadEventsWithoutProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''

        FILE_NAME = 'events.csv'
        self.createTestFile(FILE_NAME)

        loadData([settings.GTFS_VERSION, 'event', self.TEST_FILE_NAME])

    def test_loadEventsWithProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''
        
        FILE_NAME = 'events.csv'
        self.createTestFile(FILE_NAME, addBadLine = True)

        LOG_FILE_NAME = 'test.log'
        loadData([settings.GTFS_VERSION, 'event', self.TEST_FILE_NAME], logFileName = LOG_FILE_NAME)
        
        self.assertLogFileNotEmpty(LOG_FILE_NAME)

    #def test_loadRoutesWithoutProblem(self):
    #    ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''
 
    #    FILE_NAME = 'routes.csv'
    #    self.createTestFile(FILE_NAME)

    #    loadData([settings.GTFS_VERSION, 'route', self.TEST_FILE_NAME])

    #def test_loadRoutesWithProblem(self):
    #    ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''
        
    #    FILE_NAME = 'routes.csv'
    #    self.createTestFile(FILE_NAME, addBadLine = True)

    #    LOG_FILE_NAME = 'test.log'
    #    loadData([settings.GTFS_VERSION, 'route', self.TEST_FILE_NAME], logFileName = LOG_FILE_NAME)
        
    #    EXPECTED_LOG = "=========================================\n"\
    #    "Exception: value too long for type character varying(11)\n"\
    #    "Loader: Route\n"\
    #    "Data columns: serviceCode,latitude,longitude,sequence\n"\
    #    "Values: HI!IAmAnError101I;-33.406175;-70.623244;1\n"\
    #    "=========================================\n"\

    #    self.compareLogFile(LOG_FILE_NAME, EXPECTED_LOG)

    def test_loadServiceLocationWithoutProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''

        # we need to load previous data:
        # busstop
        loadData([settings.GTFS_VERSION, 'busstop', os.path.join(self.FILE_PATH, 'busstop.csv')])

        FILE_NAME = 'servicelocation.csv'
        self.createTestFile(FILE_NAME)
        
        loadData([settings.GTFS_VERSION, 'servicelocation', self.TEST_FILE_NAME])

    def test_loadServiceLocationWithProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''
        
        FILE_NAME = 'servicelocation.csv'
        self.createTestFile(FILE_NAME, addBadLine = True)

        LOG_FILE_NAME = 'test.log'
        loadData([settings.GTFS_VERSION, 'servicelocation', self.TEST_FILE_NAME], logFileName = LOG_FILE_NAME)
        
        self.assertLogFileNotEmpty(LOG_FILE_NAME)

    def test_loadServicesWithoutProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''

        FILE_NAME = 'services.csv'
        self.createTestFile(FILE_NAME)

        loadData([settings.GTFS_VERSION, 'service', self.TEST_FILE_NAME])

    def test_loadServicesWithProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''
        
        FILE_NAME = 'services.csv'
        self.createTestFile(FILE_NAME, addBadLine = True)

        LOG_FILE_NAME = 'test.log'
        loadData([settings.GTFS_VERSION, 'service', self.TEST_FILE_NAME], logFileName = LOG_FILE_NAME)

        self.assertLogFileNotEmpty(LOG_FILE_NAME)

    def test_loadServicesByBusStopWithoutProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''

        # we need to load previous data:
        # services
        loadData([settings.GTFS_VERSION, 'service', os.path.join(self.FILE_PATH, 'services.csv')])
        # busstop
        loadData([settings.GTFS_VERSION, 'busstop', os.path.join(self.FILE_PATH, 'busstop.csv')])

        FILE_NAME = 'servicesbybusstop.csv'
        self.createTestFile(FILE_NAME)
        
        loadData([settings.GTFS_VERSION, 'servicesbybusstop', self.TEST_FILE_NAME])

    def test_loadServicesByBusStopWithProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''
        
        # we need to load previous data:
        # services
        loadData([settings.GTFS_VERSION, 'service', os.path.join(self.FILE_PATH, 'services.csv')])

        FILE_NAME = 'servicesbybusstop.csv'
        self.createTestFile(FILE_NAME, addBadLine = True)

        LOG_FILE_NAME = 'test.log'
        loadData([settings.GTFS_VERSION, 'servicesbybusstop', self.TEST_FILE_NAME], logFileName = LOG_FILE_NAME)
        
        self.assertLogFileNotEmpty(LOG_FILE_NAME)

    def test_loadServicesStopDistanceWithoutProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''

        # we need to load previous data:
        # busstop
        loadData([settings.GTFS_VERSION, 'busstop', os.path.join(self.FILE_PATH, 'busstop.csv')])

        FILE_NAME = 'servicestopdistance.csv'
        self.createTestFile(FILE_NAME)

        loadData([settings.GTFS_VERSION, 'servicestopdistance', self.TEST_FILE_NAME])

    def test_loadServicesStopDistanceWithProblem(self):
        ''' Create a little file with a chunck of $FILE_NAME file and use Loader to put into database '''
        
        FILE_NAME = 'servicestopdistance.csv'
        self.createTestFile(FILE_NAME, addBadLine = True)

        LOG_FILE_NAME = 'test.log'
        loadData([settings.GTFS_VERSION, 'servicestopdistance', self.TEST_FILE_NAME], logFileName = LOG_FILE_NAME)
        
        self.assertLogFileNotEmpty(LOG_FILE_NAME)
