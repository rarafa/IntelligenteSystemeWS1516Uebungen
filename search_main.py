#!/usr/bin/python
# -*- coding: latin-1 -*-

# Usage python search.py DRS JFK
# Required data: airports.dat.txt , routes.dat.txt

import sys
import math
from math import sqrt

################################################################
#
# Read airports and routes
#
################################################################

def readAirports():
    print('')
    print("Data from openflights.org")
    print("Reading airports")
    for line in open("airports.dat.txt"):
        try:
            l = line.split(",")
            city = l[2].replace("\"","").strip()
            country = l[3].replace("\"","").strip()
            code = l[4].replace("\"","").strip()
            x = float(l[6].strip())
            y = float(l[7].strip())
            if len(code)==3:
                code2city[code] = city+", "+country
                code2country[code] = country
                code2xy[code] = (x,y)
        except:
            print("  Skipping ",line[:50]+"...")
    print(len(code2city.keys()),"airports")



# add flight connection if from and to exist in code2city
def addFlight(fr,to):
    if fr in code2city and to in code2city:
        if fr in conn:
            conn[fr].add(to)
        else:
            conn[fr] = set([to])
        if to in conn:
            conn[to].add(fr)
        else:
            conn[to] = set([fr])

def readRoutes():
    print('')                
    print("Reading routes")
    i = 0
    for line in open("routes.dat.txt"):
        i+= 1
        l = line.split(",")
        fr = l[2].replace("\"","").strip()
        to = l[4].replace("\"","").strip()
        addFlight(fr,to)    
    print(i," connections")

################################################################
#
# Distance between airports from long/lat coordinates on sphere
# See e.g. http://www.koordinaten.de/informationen/formel.shtml
#
################################################################

def distance(fr,to):
    if fr == to: return 0.0
    elif fr in code2xy and to in code2xy:
        (x1,y1) = code2xy[fr]
        (x2,y2) = code2xy[to]
        try:
            d = math.acos(math.sin(math.radians(x1))*math.sin(math.radians(x2)) + math.cos(math.radians(x1))*math.cos(math.radians(x2))*math.cos(math.radians(y2-y1)))*6378.137
        except ValueError:
            print("ValueError in distance calculation for ", fr,x1,y1, "to", to,x2,y2)
            d = 0.0
        return d


################################################################
#
# Main data structures
#
################################################################

# 3 letter code for airports is key to dictionaries
code2city = {} # city of airport
code2xy = {} # latitude and longitude of airport
code2country = {} # country of airport
conn = {} # connections of airport
countries = set() #added by Rafael


################################################################
#
# Functions defined by Rafael 
#
################################################################

def populateListOfCountries():
	global countries
	for i in code2country:
		countries.add(code2country[i])
	countries = set(countries)

def airportsSortedByNumberOfConnections():
	print("Airports sorted by the number of their connections")
	counter = 1  
	for x in sorted(conn, key=lambda x : len(conn[x]), reverse=True):
		print(counter, x)		
		if counter==10:
			break
		else:
			counter+=1
			
	
def airportsSortedByDistancesToConnectedAirports():	
	print("Airports sorted by the sum of distances of all their connections") #i.e. the sum of distance from the airport to all the airports it has a connection with (?)
	distances={}
	for airport in conn.keys():
		sumOfDistances=0.0
		for connectedAirport in conn[airport]:
			sumOfDistances += distance(airport, connectedAirport)
		distances[airport] = sumOfDistances
	counter = 1
	for i in sorted(distances.items(), key=lambda (a,b):b, reverse = True): #NOTE that if sorting distances instead of distances.items() another result is obtained (I don't know why)
	#for i in sorted(distances, key=distances.get, reverse = True): 	#this also works
		print(counter, i)		
		if counter == 10:
			break
		else:
			counter+=1

def airportsHavingOnlyOneConnection():
	print("Airports having exactly one connection")
	counter=0
	for x in conn:
		if len(conn[x])==1:
			print(counter, x)
			if counter==10:
				break
			else:
				counter += 1

def countriesSortedByNumberOfAirports():
	print("Countries sorted by number of airports")
	countries={}
	for i in code2country:
		countries[code2country[i]] = 0
	for i in code2country:
		countries[code2country[i]] += 1
	counter = 1
	for i in sorted(countries.items(), key=lambda x:x[1], reverse=True):
		print(counter, i)		
		if(counter == 10):
			break
		else:
			counter += 1
	
def countriesSortedBySumOfDistancesOfDomesticConnections():
	print("Countries sorted by sum of distances of domestic connections") #i.e. connections not going abroad
	#get list of countries
	populateListOfCountries()
	#get the sum of distances of domestic flights of each country
	sumOfDistancesOfDomesticFlights = {}
	for country in countries:
		sumOfDistancesOfDomesticFlights[country] = 0.0
		airportsOfCountry = []
		#get the airports of current country
		for airport in code2country:
			#check whether the airport is located in the current working country
			if code2country[airport] == country:
				airportsOfCountry.append(airport)
		for airportA in airportsOfCountry:
			for airportB in airportsOfCountry:
				if airportA != airportB:					
					connectionDistance = distance(airportA, airportB)
					sumOfDistancesOfDomesticFlights[country] += connectionDistance
		#divide by two because each connection was counted twice
		sumOfDistancesOfDomesticFlights[country] /= 2
	#sort descending
	counter = 1
	for country in sorted(sumOfDistancesOfDomesticFlights, key=sumOfDistancesOfDomesticFlights.get, reverse=True):
		print country, ";", sumOfDistancesOfDomesticFlights[country]
		if counter == 10:
			break
		else:
			counter += 1
	
def numberOfConnectionsSharedByEachPairOfAirports():
	print("Number of connections shared by each pair of airports")
	sharedConnections = {} #a map from pairs of airports to the number of connections they share
	for airportA in conn:
		for airportB in conn:
			if airportA != airportB:
				shared = conn[airportA] & conn[airportB]
				sharedConnections[(airportA, airportB)] = len(shared)
	#print first 10 results
	counter = 1
	for pairOfAirports in sorted(sharedConnections, key=sharedConnections.get, reverse=True):
		print pairOfAirports[0], code2country[pairOfAirports[0]], pairOfAirports[1], code2country[pairOfAirports[1]], sharedConnections[pairOfAirports]
		if counter == 10:
			break
		else:
			counter += 1
		
def numberOfConnectionsSharedByEachPairOfCountries():
	"""not considering the connections between each pair of countries"""
	print("Number of international connections shared by each pair of countries")
	populateListOfCountries()
	sharedConnections={} #pair of countries, number of shared connections
	for countryA in countries:
		for countryB in countries:
			airportsOfCountryA = []
			airportsOfCountryB = []
			foreignAirportsReachableFromCountryA = set()
			foreignAirportsReachableFromCountryB = set()
			sharedConnections[(countryA, countryB)] = 0
			#get list of airports of each country
			for airport in code2country:
				if code2country[airport] == countryA:
					airportsOfCountryA.append(airport)
				elif code2country[airport] == countryB:
					airportsOfCountryB.append(airport)
			#check which international destinations are reached from each of the two countries
			for airport in airportsOfCountryA:
				if airport in conn: #from the example data, there are some airports with no connections
					for destination in conn[airport]:
						#discard domestic connections and connections with the other country
						if code2country[destination] != countryA and code2country[destination] != countryB:
							foreignAirportsReachableFromCountryA.add(destination)
			for airport in airportsOfCountryB:
				if airport in conn: #the example data suggested me that this verification is needed
					for destination in conn[airport]:							
						#discard domestic connections and connections with the other country
						if code2country[destination] != countryB and code2country[destination] != countryA:
							foreignAirportsReachableFromCountryB.add(destination)			
			#get the number of shared connections for the current pair of countries, intersecting sets
			numberOfSharedConnections = len(foreignAirportsReachableFromCountryA & foreignAirportsReachableFromCountryB)
			sharedConnections[(countryA, countryB)] = numberOfSharedConnections
	#print first results
	counter = 1
	for i in sorted(sharedConnections, key=sharedConnections.get, reverse=True):
		if sharedConnections[i] != 0:						
			print i, sharedConnections[i]
			if counter == 20:
				break
			else:
				counter+=1
		
def Exercise1():
	print("***** Exercise 1 *****")
	print("\n\n\nTask 1");
	airportsSortedByNumberOfConnections()
	print("\n\n\nTask 2");
	airportsSortedByDistancesToConnectedAirports()
	print("\n\n\nTask 3");
	airportsHavingOnlyOneConnection()
	print("\n\n\nTask 4");
	countriesSortedByNumberOfAirports()
	print("\n\n\nTask 5");
	countriesSortedBySumOfDistancesOfDomesticConnections()
	print("\n\n\nTask 6");
	numberOfConnectionsSharedByEachPairOfAirports()
	print("\n\n\nTask 7");
	numberOfConnectionsSharedByEachPairOfCountries()

def readingData():
	# load data
	readAirports()
	readRoutes()

	codes = conn.keys()
	if  len(sys.argv)==3:
		fr = sys.argv[1]
		to = sys.argv[2]
		if not fr in conn:
			print("Code %s not valid or no connections for code. But found" %fr)
		if not to in conn:
			print("Code %s not valid or no connections for code. But found" % to)
	else:
		import random
		random_codes = random.sample(conn.keys(), 2)
		fr = random_codes[0]
		to = random_codes[1]
		print("Usage example: python search.py " + fr + ' ' + to)
				
	############################################################
	#
	# Search examples BFS, Greedy (require search_functions.py)
	#
	############################################################
	#bfs(fr,to)
	#greedy(fr,to)
	

readingData()
Exercise1()


