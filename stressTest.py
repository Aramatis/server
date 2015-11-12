
import requests, json
from random import uniform
import datetime
import threading
import time

minP = -33.519893, -70.740650
maxP = -33.403286, -70.573249
serverIP = "172.17.77.240"
serverPort = "80"


class StadisticHello(object):

	def __init__(self):
		self.getTokenTime = 0
		self.trajectoryTime = 0
		self.endRouteTime = 0
		self.succes = False
		self.failrequest = 0
		self.requestsCount = 0

def nearbyBuses( pData):#/android/sendTrajectoy
	
	dt = datetime.datetime.now()

	times = str(dt.hour) + ':' + str(dt.minute) + ':' + str(dt.second)
	date = str(dt.year) + '-' + str(dt.month) + '-' + str(dt.day)
	
	# get a token
	url = "http://" + serverIP + ":" + serverPort + "/android/requestToken/334/AA6"

	start = time.time()
	response = requests.get(url=url)
	end = time.time()

	pData.getTokenTime = end - start
	pData.requestsCount += 1
	#print	url
	print 'response: ' + response.text
	data = json.loads(response.text)

		
	# send a trajectory
	token = data['token']
	#print token

	trajectoryTime = 0.0
	nIter = 30
	try:
		for cont in range(nIter):

			lat1 = uniform(minP[0],maxP[0])
			lon1 = uniform(minP[1],maxP[1])

			lat2 = uniform(minP[0],maxP[0])
			lon2 = uniform(minP[1],maxP[1])

			lat3 = uniform(minP[0],maxP[0])
			lon3 = uniform(minP[1],maxP[1])

			lat4 = uniform(minP[0],maxP[0])
			lon4 = uniform(minP[1],maxP[1])

			lat5 = uniform(minP[0],maxP[0])
			lon5 = uniform(minP[1],maxP[1])

			testPoses = {"poses":[\
			{"latitud":-33.458771,"longitud" : -70.676266, "timeStamp":date + " " + times, "inVehicleOrNot":"vehicle"},\
			{"latitud":-33.458699,"longitud" : -70.675708, "timeStamp":date + " " + times, "inVehicleOrNot":"vehicle"},\
			{"latitud":-33.458646,"longitud" : -70.674678, "timeStamp":date + " " + times, "inVehicleOrNot":"vehicle"},\
			{"latitud":-33.458646,"longitud" : -70.673799, "timeStamp":date + " " + times, "inVehicleOrNot":"vehicle"},\
			{"latitud":-33.458413,"longitud" : -70.671631, "timeStamp":date + " " + times, "inVehicleOrNot":"vehicle"},\
			{"latitud":-33.457983,"longitud" : -70.669035, "timeStamp":date + " " + times, "inVehicleOrNot":"vehicle"},\
			{"latitud":-33.457518,"longitud" : -70.666718, "timeStamp":date + " " + times, "inVehicleOrNot":"vehicle"},\
			{"latitud":-33.457196,"longitud" : -70.664636, "timeStamp":date + " " + times, "inVehicleOrNot":"vehicle"},\
			{"latitud":-33.457070,"longitud" : -70.660559, "timeStamp":date + " " + times, "inVehicleOrNot":"vehicle"}]}

			
			trajectoryJson = json.dumps(testPoses)
			url = "http://" + serverIP + ":" + serverPort +  "/android/sendTrajectory/" + token + '/' + trajectoryJson
			
			start = time.time()
			response = requests.get(url=url)
			end = time.time()

			pData.requestsCount += 1
			trajectoryTime = trajectoryTime + end - start
			#print url
			if response.status_code == 500:
				print "fail: ", response.url
			#print url
			#print 'response: ' + response.text
			#time.sleep(0.02)#uniform(0.02,1)
	except requests.ConnectionError:
		pData.failrequest += 1

	pData.trajectoryTime = trajectoryTime/pData.requestsCount
	pData.succes = True

	# end trip
	url = "http://" + serverIP + ":" + serverPort + "/android/endRoute/" + token 
	
	#print url
	start = time.time()
	response = requests.get(url=url)
	end = time.time()
	print 'response: ' + response.text

	pData.requestsCount += 1
	pData.endRouteTime = end - start



def main():
	threads = list()
	threadsNumber = 30
	info = []
	generalTime = time.time()
	for i in range(threadsNumber):
		dataS = StadisticHello()
		t = threading.Thread(target=nearbyBuses, args=(dataS,) )
		threads.append(t)
		info.append(dataS)
		t.start()
		time.sleep(uniform(0.001,0.01))

	for i in range(threadsNumber):
		threads[i].join()

	generalTime = time.time() - generalTime
	generalRequest = 0
	generalFailRequest = 0
	generalNotFail = True
	generalAverage = 0

	for val in info:
		print '----'
		print val.getTokenTime
		print val.trajectoryTime
		print val.endRouteTime
		print val.succes
		print val.requestsCount
		print val.failrequest
		generalRequest += val.requestsCount
		generalNotFail += val.failrequest
		generalAverage += val.trajectoryTime


	print "allTime: " ,generalTime
	print "requests per second: ", generalRequest/generalTime
	print "fail request per second: ", generalFailRequest/generalTime
	print "Average send trajectory request per second: ", generalAverage/generalTime

if __name__ == "__main__":
	main()




