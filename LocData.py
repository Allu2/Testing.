#!/usr/bin/python
#  -*- coding: utf-8 -*-
__author__ = 'Aleksi Palomäki'
import math
from datetime import datetime
class LocData:

    def __init__(self, database, user):
        self.db = database
        self.userID = user

    '''
    getInCircle(radius, center_location)
     This function will lookup information from the database for cases matching circle generated from center_location and radius.
     This process is done in two steps.
        1) We make a square that surrounds the generated circle. We use this to filter most locations that are outside out target.
        2) We compare the distance of each data point from the center, and if they are larger then the radius given, we ignore them.
     This should yield list of data inside the wanted area.
     Since this is for demonstration we ignore the fact world is not flat for now and use longitude and latitude as if coordinates on flat grid. This will probably not give accurate results.
    '''
    def getInCircle(self, radius, center_location):
        print("We want to get from a circle.")
        print("Radius is {}".format(radius))
        print("Center is {}".format(center_location))
        center_x = center_location[0]
        center_z = center_location[2]
        square_corner1 = [center_x-radius, 0, center_z-radius]  # Ignore height
        square_corner2 = [center_x+radius, 0,center_z+radius]   # Ignore height
        print("Square surrounding the Circle has corners in {} and {}".format(square_corner1,square_corner2))
        possible_hits = self.getInRectangle(square_corner1, square_corner2)
        hits = []
        for location in possible_hits:
            distance = math.sqrt((center_x-location[0][0])**2 + (center_x-location[0][1])**2)
            if distance <=radius:
                hits.append(location)
        return hits



    '''
    getInRectangle(corner1, corner2)
     This function fetches location data from given database (Current format it expects is [[float(x),float(z)],date, name]) that matches the rectangular area defined by 2 corners.
     Corner1 is expected to be lower left corner, Corner2 the upper right corner.
     Since this is for demonstration we ignore the fact world is not flat for now and use longitude and latitude as if coordinates on flat grid. This will not give accurate results.
    '''
    def getInRectangle(self, corner1, corner2):

        print("We want to get from a rectangle.")
        corner3 = (corner1[0], corner2[2])
        corner4 = (corner1[2], corner2[0])
        print("Corner1 is {} and Corner2 is {}".format((corner1[0],corner1[2]),(corner2[0],corner2[2])))
        higest_x = corner2[0]
        lowest_x = corner1[0]
        higest_z = corner2[2]
        lowest_z = corner1[2]
        results = []
        for stuff in self.db:
            #print("x:{}, z:{}".format(stuff[0][0],stuff[0][1]))
            if  (stuff[0][0]>= lowest_x
                and stuff[0][0]<= higest_x):
                if (stuff[0][1]>= lowest_z
                    and stuff[0][1]<=higest_z):
                    results.append(stuff)
        return results


    '''
    getData(between, area)
     This function is thought to be called to fetch relevant data from database
     Data in database is expected to be some kind of location data(GPS?) with date information.
     User can query the database and filter it with time and area on map. Area filters support Circle and Rectangle.

     TODO: I probably have to worry about scope of the query, but first I want to have something that works for basic stuff.
    '''
    def getData(self, between, area):   # Format: between[datetime(),datetime()], area[Corner1,Corner2,start_location]
        start_date = between[0]         # None if from start of data till the end_date, otherwise date.
        end_date = between[1]           # None if till the latest data.
        result_data = None
        corner1 = area[0]               # None if we want to use Circle
        corner2 = area[1]               # Second corner or radius if area[0] is None
        center_location = area[2]       # None if we use Rectangle area, center of the circle if we use the Circle area.
        self.readData()                 # Read the database and format it to our use.
        # Determine the type of area.
        # We know for sure we want Circle in this case.
        if (center_location is not None) and ( (corner2 is not None)  and (corner1 is None) ):
            result_data = self.getInCircle(corner2, center_location)

        # We know for sure we want Rectangle in this case.
        elif (center_location is None) and ( (corner2 is not None) and (corner1 is not None) ):
            result_data = self.getInRectangle(corner1, corner2)

        # We must want all data.
        else:
            print("We want to get everything!")
            result_data = self.db

        #Determine the time scope we are looking at. When we eventually deal with real databases it would make
        #   sense to use their methods for searching time and such. But meanwhile I don't have database with
        #   test data to use this will have to do.

        temp_result = [] #Stores the time aware results.
        if(start_date is None and end_date is None):            # We must want from beginning to the end.
            pass
        elif (start_date is None and end_date is not None):     # We must want from beginning to end_date.
            for hit in result_data:
                if hit[1]<=end_date:
                    temp_result.append(hit)
            result_data = temp_result

        elif (start_date is not None and end_date is not None): # We must want between start_date and end_date.
            for hit in result_data:
                if hit[1]>=start_date and hit[1]<=end_date:
                    temp_result.append(hit)
            result_data = temp_result
        elif (start_date is not None and end_date is None):     # We must want from start_date till the end.
            for hit in result_data:
                if hit[1]>=start_date:
                    temp_result.append(hit)
            result_data = temp_result
        return result_data
    '''
    readData(database)
     This function reads the data we want to handle and formats it appropriately for the rest of the functions.
     When porting to new databases, ideally  we just have to edit this function.
    '''
    def readData(self):
        data = []
        # Parsing the file to include latitude, longitude, date and name of the place. Though we could add new fields towards the end as need dictates.
        for line in self.db.readlines():
            line = line.split("FI")
            coordpart = line[0].split("\t")
            try:
                x = coordpart[-5]
                z = coordpart[-4]
                date = line[1].split("\t")[-1].rstrip("\n").split("-")
                date = datetime(int(date[0]), int(date[1].lstrip("0")), int(date[2].lstrip("0")))
                name = coordpart[1]
                data.append([(float(x),float(z)), date, name])
            except: # Few Airports and such have different format and are irrelevant for this test case.
                pass
        self.db = data


    '''
    And this is for testing the class and its functions.
    '''
    # File FI.txt is from http://download.geonames.org/export/dump/FI.zip
    def tests(self):
        self.db = open("FI.txt",'r', encoding="UTF-8")    # We parse this in readData()
        between = [datetime(2014, 2, 1),datetime(2015, 3, 1)]
        area= [[60.852269,0,21.632595],[60.891876,0,21.74263], None]
        print("Tulokset")
        hits = self.getData(between, area)
        for x in hits:
            print(x)
        pass
        return hits
#Uncomment for testing.
#loc = LocData("lol", "1372")
#loc.tests()


