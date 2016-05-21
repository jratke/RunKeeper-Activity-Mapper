#!/usr/bin/python

import pygmaps
import zipfile
import re
import argparse
import xml.parsers.expat
from xml.parsers.expat import ExpatError
from xml.dom import minidom

RED = "#FF0000"
GREEN = "#00FF00"
BLUE = "#0000FF"
ORANGE = "#FF8C00"

def activity_color(activity_type):
	if activity_type == "Cycling":
		return RED
	elif activity_type == "Walking":
		return GREEN
	elif activity_type == "Running":
		return BLUE
	else:
		return ORANGE

parser = argparse.ArgumentParser()
parser.add_argument("-i", required=True, help="zip file containing your activities")
args = parser.parse_args()

mymap = pygmaps.maps(40.645, -111.933, 16)

lastLat, lastLon = 0.0, 0.0
actCount = 0

with zipfile.ZipFile(args.i, "r") as zfile:
    for name in zfile.namelist():
	if not name.endswith(".gpx"):
		continue

	path = []

	# TODO: Setup layers for each activity type
	# TODO: Take flag from user input to only map certain activity types
	try:
		xmldoc = minidom.parse(zfile.open(name))
	except ExpatError as e:
		print "---Error code " + str(e.code) + " str: " + xml.parsers.expat.ErrorString(e.code)
		print " parsing " + name + " line: " + str(e.lineno) + " col: " + str(e.offset) + " , skipping"
		continue

	itemlist = xmldoc.getElementsByTagName('trkpt')
	
	activityName = xmldoc.getElementsByTagName('name')[0].firstChild.nodeValue
	activityType = re.search(r'^([\w]+)', activityName).group()
	print "Processing %s (%s)" % (name, activityType)
	
        lastlat, lastlon = 0.0, 0.0
	for s in itemlist:
		lat, lon = float(s.attributes['lat'].value), float(s.attributes['lon'].value)
		if lastlat != lat or lastlon != lon:
			path.append([lat, lon])
		lastlat, lastlon = lat, lon
	
	mymap.addpath(path, activity_color(activityType))
	#print "start lat & lon is %f %f" % (path[0][0], path[0][1])
	lastLat = path[0][0]
	lastLon = path[0][1]
	actCount += 1

print "Generating map... %d activities" % actCount
mymap.setcenter(lastLat, lastLon)
mymap.draw('./activityMap.html')
