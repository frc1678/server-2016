# To get TBA photos, put them on dropbox, and link them in firebase
# By Bryton, 2016

# Imgur example: https://i.imgur.com/zYtPwly.jpg

''' /api/v2/team/frc971/2016/media
[
  {
    "type": "imgur",
    "details": {},
    "foreign_key": "zYtPwly"
  },
  {
    "type": "youtube",
    "details": {},
    "foreign_key": "CMX4ynSQsyI"
  }
]
'''


import TBACommunicator
import utils
import json
import os

def pythonObjForJSON(JSON):
	return utils.readJSONFromString(json.dumps(JSON))

def mediaRequest(key):
	return TBAC.makeTeamMediaRequest(key, 2016)

def imgurURL(key):
	return "https://i.imgur.com/" + key + ".jpg"

TBAC = TBACommunicator.TBACommunicator()
TBAC.eventCode = 'hop'
TBAC.eventCodeYear = '2016hop'


#teamKeys = [pythonObjForJSON(team)['key'] for team in pythonObjForJSON(TBAC.makeEventTeamsRequest())]
#teamMediaInfo = map(mediaRequest, teamKeys)

teamMediaInfo = eval(pythonObjForJSON(open("/Users/brytonmoeller/Desktop/mobileCodeProjects/server-2016/hopper2016media", 'r').read()))
#print teamMediaInfo
imgurs = []
for team in teamMediaInfo:
	for media in pythonObjForJSON(team):
		if media["type"] == "imgur":
			imgurs.append(imgurURL(media["foreign_key"]))
'''
for i in range(0, len(imgurs) - 1):
	os.system("curl " + imgurs[i] + " >> ~/Desktop/prepit/" + str(i) + ".jpg")
'''
ranges = []

for team in teamMediaInfo:
	r = 0
	for media in pythonObjForJSON(team):	
		if media["type"] == "imgur":
			r += 1
	ranges.append(r)

teamNums = [pythonObjForJSON(team)['team_number'] for team in pythonObjForJSON(TBAC.makeEventTeamsRequest())]

nameMap = {}
s = 0
for i in range(0, len(ranges) - 1):
	rang = ranges[i]
	a = []
	for r in range(0, rang):
		a.append(s)
		s += 1
	nameMap[teamNums[i]] = a

urlMap = {}

def nameForNumber(num):
	return str(num) + '.jpg'

for num in nameMap:
	for i in range(0, len(nameMap[num]) ):
		n = nameMap[num][i]
		fileName = nameForNumber(n)
		print fileName
		os.system("cp ~/Desktop/prepit/" + fileName + " ~/Desktop/output/" + str(num) + "_" + str(i) + ".png")


# go from 0 to the first item in ranges - 1 for the first team.

