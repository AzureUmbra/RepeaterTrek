from bs4 import BeautifulSoup as bs
import requests
import re
from gmplot import gmplot as gm
import pickle
from math import sqrt
from geopy.distance import distance
from copy import deepcopy as dc
#gpsvisualizer.com, paste route URL, plain text, comma seperated

def _dataToString(data):
    """
    PRIVATE
    Converts dictionary of repeater data into html parsable string.

    Args:
    data -- dictionary; contains repeater data

    Return:
    string -- string; parsed string
    """
    if data['Use'] == 'STARTPOINT' or data['Use'] == 'ENDPOINT':
        string = 'Address: ' + data['Address'] + '\\n'
        string += 'Distance: ' + data['Distance'] + '\\n'
        string += 'Time: ' + data['Time']
    else:
        string = 'Location: ' + data['Location'] + '\\n'
        if "Distance" in data:
            string += 'Distance: ' + str(round(data['Distance'],2)) + ' Miles\\n'
            string += "Beginning At: " + str(data["Begin"]) + '\\n'
            string += "Ending At: " + str(data["End"]) + '\\n'
            string += "Closest Approach At: " + str(data["Closest"]) + '\\n'
            string += "For A Total Of: " + str(round(data["RouteLength"],2)) + ' Miles\\n'
        string += 'Frequency: ' + data['Frequency'] + '\\n'
        string += 'Offset: ' + data['Offset/shift'] + '\\n'
        string += 'Tone: ' + data['Tone'] + '\\n'
        string += 'Call: ' + data['Call'] + '\\n'
        string += 'Use: ' + data['Use'] + '\\n'
        string += 'Lat: ' + data['Lat'] + '\\n'
        string += 'Long: ' + data['Lng'] + '\\n'
        string += 'State: ' + data['state/province'] + '\\n'
        string += 'County: ' + data['County']
    
    return string


def parseFromWeb(fileName,URL,wideArea=False,header='https://www.repeaterbook.com/repeaters/',collect=True,getCoords=True,URLs=[]):
    """
    PUBLIC
    Requests and parses repeater data from repeaterbook link.

    Args:
    fileName  -- string; name of file to save data
    URL       -- string; link to make request
    header    -- string,default; prefix of each repeater's individual page
    wideArea  -- bool,default; if this should be saved as a wide area file
    collect   -- bool,default; if data should be requested and parsed
    getCoords -- bool,default; if data in 'URLs' should have Lat/Long embedded
    URLs      -- list,of dicts,default; when not collecting data, allows repeater dicts to be passed for embedding Lat/Long

    Return:
    URLs -- list,of dict; repeater dicts passed when not using both parts of code
    None -- nothing is returned if 'collect' and 'getCoords' are True, 'URLs' is saved as 'fileName'.rd
    """
    
    if collect:
        # Requests URL HTML and parses all repeaters out
        print("Requesting Repeater List")
        req = requests.get(URL)
        soup = bs(req.text,"html.parser")
        pieces = soup.findAll('a',href=re.compile('details\.php\?'))
        print("Repeaters Collected")

        # BS4 was not working well, so prepare yourself
        print("Parsing Repeater Information")
        keys = ['Link','Frequency','Offset/shift','Tone','Location','County','state/province','Call','Use']
        URLs = []
        for i in pieces:
            # Stores the link grabbed directly with BS4, initializes each loop
            temp = {'Link':header + i['href']}
            tempList = []
            x=i #I don't know, OK...this made it work...
            # Could not jump with BS4 Children or Siblings, so 40 iterations got it all
            for j in range(40):
                tempList.append(str(x))
                x = x.next
            # Removes all tags and random newlines from the list
            z = [j.strip() for j in [k for k in tempList if '<' not in k] if j !='\n']
            # This tag never made it in the list, so assign its value manually
            temp['Frequency'] = z.pop(0)
            # Everything that is left are key:value pairs, so build them
            while len(z) > 0:
                key = z.pop(0)
                val = z.pop(0)
                # Some repeaters are missing some data. When that happens,
                # assign it none and grab the next item, fixing the pattern
                if val in keys:
                    temp[key] = 'None'
                    temp[val] = z.pop(0)
                else:
                    temp[key] = val
            URLs.append(temp)

        # Update the list 'Use' with the wide area repeaters
        if wideArea:
            URLs = _wideAreaBuild(URLs,parseFromWeb(fileName+'WARLtemp',wideArea,getCoords=False))

        # Destroys all evidence of the previous disaster
        del pieces
        del soup
        print("Repeaters Parsed and Sorted")
        
        # If called by 'updateFromWeb' will pass repeater dicts back without coordinates and stop here
        if collect and not getCoords:
            return URLs

    # This is slow, on account of having to visit each repeaters individual page
    if getCoords:
        print(str(len(URLs)) + " Repeaters Found")
        print("Beginning Location Collection")
        # No BS4 here, I was tired of its crap
        for i in range(len(URLs)):
            print("Getting Repeater Number " + str(i) + ' of ' + str(len(URLs)))
            URL = URLs[i]
            # Goes to the URL and parses out the Lat/Long for that repeater, adding it to its dict
            soup = str(requests.get(URL['Link']).text)
            coords = (soup.split('LatLng')[1].split(';')[0]).strip('()').split(',')
            URLs[i]['Lat'] = coords[0]
            URLs[i]['Lng'] = coords[1]
        print("All Coordinates Received")
        
        # If called by 'updateFromWeb' will pass repeater dicts back with coordinates, otherwise save
        if getCoords and not collect:
            return URLs

        if wideArea:
            extension = 'WA.rl'
        else:
            extension = '.rl'
        pickle.dump(URLs,open(fileName+extension,'wb'))
        print("Saved in File: " + fileName+extension)


def updateFromWeb(fileName,URL,header='https://www.repeaterbook.com/repeaters/',wideArea=False):
    """
    PUBLIC
    Requests and parses repeater data from repeaterbook link to update current data utilizing 'parseFromWeb'.

    Args:
    fileName  -- string; name of file to save data
    URL       -- string; link to make request
    header    -- string,default; prefix of each repeater's individual page
    wideArea  -- bool,default; if this is a wide area repeater file

    Return:
    None -- nothing is returned, 'new' is saved as fileName.rl
    """

    # Gets the main page of the requested update and parses it all out
    keys = ['Link','Frequency','Offset/shift','Tone','Location','County','state/province','Call','Use']
    
    if wideArea:
        extension = 'WA.rl'
    else:
        extension = '.rl'
    current = _loadFile(fileName,fileType=extension)

    update = parseFromWeb(fileName,URL,getCoords=False,wideArea=wideArea)
    new = []
    needsCoords = []

    # Compares every new record to the saved ones via keys
    # If it matches, add it to 'new'
    # If not, add the new record to 'needsCoords'
    for i in update:
        match = False
        for j in current:
            thisOne = True
            for k in keys:
                if i[k] != j[k]:
                    thisOne = False
                    break
            if thisOne:
                new.append(j)
                match = True
                break
        if not match:
            needsCoords.append(i)

    # Throws away anything that didnt match, requests coordinates and adds them
    print(str(len(update)) + ' Repeaters Found of ' + str(len(current)) + ' in File')
    print(str(len(current)-len(new)) + ' Repeaters Outdated')
    print(str(len(needsCoords)) + ' New Repeaters to Download')
    if input('Enter "Y" to Delete Outdated and Download New: ').lower() == 'y':
        if len(needsCoords) > 0:
            updated = parseFromWeb(fileName,URL,collect=False,URLs=needsCoords,wideArea=wideArea)
            new += updated
        pickle.dump(new,open(fileName+extension,'wb'))
        print(fileName + extension + ' Updated to ' + str(len(new)) + ' Repeaters')
    else:
        print('No Changes Have Been Made')
    # tl;dr: don't update records, just pitch the old non-matches,
    # keep the matches, and request coordinates for the new non-matches
        

def _loadFile(fileName,fileType='.rl'):
    """
    PRIVATE
    Loads repeater dict files.

    Args:
    fileName  -- string; name of file to load data
    fileType  -- string,default; file extension

    Return:
    URLs -- list,of dict; repeater dicts passed
    """
    
    print('Opening File ' + fileName + fileType)
    URLs = pickle.load(open(fileName+fileType,'rb'))
    return URLs


def plotMap(fileName,multi=False,gmap=False,route=False):
    """
    PUBLIC
    Draws and saves repeater locations onto a Google Map.

    Args:
    fileName  -- string; name of file to save and load data
    multi     -- bool,default; if enabled, no map is generated and data is added to 'gmap'
    gmap      -- gmap,default; used to pass gmap object when 'multi' is used
    route     -- bool,default; if this is a trip to be plotted

    Return:
    gmap -- gmap; map file with newly added repeaters
    None -- nothing is returned if 'multi' is True, 'gmap' is saved as 'fileName'.html
    """

    # If this is a single instance, generate a map
    if not multi:
        print('Generating Map')
        gmap = gm.GoogleMapPlotter(38.521136,-98.429388,5)
        gmap.coloricon = "http://www.googlemapsmarkers.com/v1/%s/"

    # Plots routes; zip used as gmap takes a lat group/long group,
    # not lat/long groups
    if route:
        URLs, route = _loadFile(fileName,fileType='.trip')
        lats,longs = zip(*route)
        gmap.plot(lats,longs,'green',edge_width=5)
    else:
        URLs = _loadFile(fileName)

    

    # Sets colors for different repeater status
    for i in URLs:
        if i['Use'] == 'OPEN':
            gmap.marker(float(i['Lat']),float(i['Lng']),'blue',title=_dataToString(i))
        elif i['Use'] == 'WIDE AREA':
            gmap.marker(float(i['Lat']),float(i['Lng']),'orange',title=_dataToString(i))
        elif i['Use'] == 'STARTPOINT':
            gmap.marker(float(i['Lat']),float(i['Lng']),'green',title=_dataToString(i))
        elif i['Use'] == 'ENDPOINT':
            gmap.marker(float(i['Lat']),float(i['Lng']),'red',title=_dataToString(i))
        else:
            gmap.marker(float(i['Lat']),float(i['Lng']),'yellow',title=_dataToString(i))


    # Pass the map back if more is to be added, otherwise save
    if not multi:
        gmap.draw(fileName + '.html')
        print('Map Saved as ' + fileName + '.html')
    else:
        return gmap


def blendMaps(fileNames,mapName):
    """
    PUBLIC
    Combines two or more repeater dicts and draws them to a map.

    Args:
    fileNames -- list,of strings; names of files to draw to map
    mapName   -- string; name of finished map file

    Return:
    None -- 'gmap' is saved as 'mapName'.html
    """

    # Generates a map and keeps passing to 'plotMap' to write on it
    print('Generating Map')
    gmap = gm.GoogleMapPlotter(38.521136,-98.429388,5)
    gmap.coloricon = "http://www.googlemapsmarkers.com/v1/%s/"
    for i in fileNames:
        gmap = plotMap(i,multi=True,gmap=gmap)
    gmap.draw(mapName + '.html')
    print('Map Saved as ' + mapName + '.html')

# Quite slow due to massive comparisons; black magic math was thrown away
def tripPlanner(tripName,fileNames,dist,wideAreaDist=0,smallestCoverage=0):
    """
    PUBLIC
    Plots repeaters along a route at a given distance and saves the repeater list

    Args:
    tripName  -- string; name to use to save the trip
    fileNames -- list,of strings; names of repeater dicts to check
    dist      -- int; distance in miles of route to be included

    Return:
    None -- trip is saved as 'tripName'.trip, 'plotMap' saves a map with repeaters and route
    """

    if wideAreaDist == 0:
        wideAreaDist = dist
    # Grabs all repeaters and points that make up the trip
    repeaters = []
    for i in fileNames:
        repeaters += _loadFile(i)
    routePoints, validRepeaters = _getPoints(tripName)

    # Check each repeater against all trip points
    # If it works, stop iterating and move on
    for i in range(len(repeaters)):
        distCheck = wideAreaDist if repeaters[i]['Use'] == 'WIDE AREA' else dist
        print('Checking Repeater ' + str(i) + ' of ' + str(len(repeaters)))
        startingPt = False
        endingPt = False
        closest = 100000
        closestPt = False
        for j in routePoints:
            reptDist = distance((float(repeaters[i]['Lat']),float(repeaters[i]['Lng'])),j).miles
            if reptDist <= distCheck:
                endingPt = j
                if not startingPt:
                    startingPt = j
                if reptDist < closest:
                    closest = reptDist
                    closestPt = j
        if startingPt:
            temp = dc(repeaters[i])
            temp["Distance"] = closest
            temp["Begin"] = startingPt
            temp["End"] = endingPt
            temp["Closest"] = closestPt
            temp["RouteLength"] = distance(startingPt, endingPt).miles
            if temp["RouteLength"] >= smallestCoverage:
                validRepeaters.append(temp)

    # Stores the selected repeaters so we never have to deal with that again
    # Calls 'plotMap' to generate the trip map
    pickle.dump((validRepeaters,routePoints),open(tripName+'.trip','wb'))
    print('Found ' + str(len(validRepeaters)) + ' Valid Repeaters')
    print('Trip Saved as ' + tripName + '.trip')
    plotMap(tripName,route=True)


def _getPoints(file):
    """
    PRIVATE
    Parses a text file of waypoints for a route from gpsvisualizer.com, created from Google Maps directions.

    Args:
    file -- string; name of the .txt file to open

    Return:
    points    -- list,of tuples; lat/long tuples that indicate the given route
    endPoints -- list,of dicts; dicts with 'Use', 'Lat', and 'Lng' flags, plus endpoint data
    """

    # Grabs psuedo-CSV file and tries to combobulate it
    print('Getting Route Points')
    points = []
    with open(file+'.txt', 'r') as f:
        lines = f.readlines()
    start = {'Use':'STARTPOINT','Lat':float(lines[1].split(',')[1]),'Lng':float(lines[1].split(',')[2]),'Address':lines[1].split('"')[1]}
    end = {'Use':'ENDPOINT','Lat':float(lines[2].split(',')[1]),'Lng':float(lines[2].split(',')[2]),'Address':lines[2].split('"')[1]}

    # Throws away first lines and gets data from the one rando line
    lines = lines[5:]
    first = lines.pop(0)
    points.append((float(first.split(',')[1]),float(first.split(',')[2])))
    first = first.split('"')[3].split(',')
    start['Distance'] = first[0]
    start['Time'] = first[1].strip()
    end['Distance'] = first[0]
    end['Time'] = first[1].strip()
    endPoints = [start,end]

    # Then just iterate nicely, loading the points into the list
    for line in lines:
        line = line.replace('T,','').replace(',,\n','').split(',')
        points.append((float(line[0]),float(line[1])))
    return points, endPoints


def _wideAreaBuild(regular,wideArea):
    fullList = []

    for i in regular:
        found = False
        for j in wideArea:
            if i == j:
                found = True
                j['Use'] = 'WIDE AREA'
                fullList.append(j)
                break
        if not found:
            fullList.append(i)
                
    return fullList
    

if __name__ == "__main__":
    #parseFromWeb('Louisiana','https://www.repeaterbook.com/repeaters/msResult.php?state_id%5B%5D=22&band=14&freq=&loc=&call=&features=%25&emcomm=%25&coverage=%25&status_id=1&order=%60freq%60%2C+%60state_abbrev%60+ASC',wideArea='https://www.repeaterbook.com/repeaters/msResult.php?state_id%5B%5D=22&band=14&freq=&loc=&call=&features=%25&emcomm=%25&coverage=wide&status_id=1&order=%60freq%60%2C+%60state_abbrev%60+ASC')
    tripPlanner('DibervilleToNOLA',['MississippiWA','LouisianaWA'],15,30,10)
