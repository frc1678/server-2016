# by Bryton Moeller (2015-2016)

import json
from firebase import firebase as fb
import urllib3
from StringIO import StringIO
import DataModel

superSecret = "j1r2wo3RUPMeUZosxwvVSFEFVcrXuuMAGjk6uPOc"

auth = fb.FirebaseAuthentication(superSecret, "1678programming@gmail.com", True, True)
firebase = fb.FirebaseApplication('https://1678-dev-2016.firebaseio.com/', auth)

teams = []
matches = []
teamInMatchDatas = []


########## Defining Util/Convenience Functions ############
''' If there were too many more of these, or if this 
were actual server code, I would make a module, but 
for fake database creation purposes it is not worth it'''

def jprint(JSON):
	print(json.dumps(JSON, sort_keys=True, indent=4))

def readJSONFromString(string):
	return json.load(StringIO(string))

def readJSONFileToObj(fileName):
	fileInput = open(fileName, 'r')
	pythonObj = json.load(fileInput)
	return pythonObj

def getPythonObjectForFirebaseDataAtLocation(location):
	# The location will be a key path, like '/' for the root (entire) object.
	result = firebase.get(location, None)
	'''
	Supposedly you can add other request parameters
	But it was throwing errors when I tried it, soo...
	But they will be JSON formatted get request parameters. :)
	'''
	return result

def makeTeamFromDict(d):
	team = Team(**d) #I have no idea why this works
	return team

def makeDictFromTeam(t):
	d = t.__dict__
	if not isinstance(t.calculatedData, dict):
		d["calculatedData"] = t.calculatedData.__dict__
	return d
def makeDictFromMatch(m):
	d = m.__dict__
	return d

def makeDictFromTIMD(timd):
	d = timd.__dict__
	return d

def makeTeamObjectWithNumberAndName(number, name):
	team = Team()
	team.name = name
	team.number = number
	return team

def makeTIMDFromTeamNumberAndMatchNumber(teamNumber, matchNumber):
	timd = DataModel.TeamInMatchData()
	timd.teamNumber = teamNumber
	timd.matchNumber = matchNumber
	teamInMatchDatas.append(timd)
	return timd

def updateFirebaseWithTeam(team):
	teamDict = makeDictFromTeam(team)
	FBLocation = "/Teams"
	result = firebase.put(FBLocation, team.number, teamDict)

def updateFirebaseWithMatch(match):
	matchDict = makeDictFromMatch(match)
	FBLocation = "/Matches"
	result = firebase.put(FBLocation, match.number, matchDict)

def updateFirebaseWithTIMD(timd):
	timdDict = makeDictFromTIMD(timd)
	FBLocation = "/TeamInMatchDatas"

	result = firebase.put(FBLocation, str(timd.teamNumber) + "Q" + str(timd.matchNumber), timdDict)


############# Getting TBA Data ###################
basicURL = "http://www.thebluealliance.com/api/v2/"
headerKey = "X-TBA-App-Id"
headerValue = "blm:serverProof1678:003" # set to "<your initials>:TBA_communicator:0"


def makeYearEventKeyRequestURL(year, event, key):
	return basicURL + 'event/' + str(year) + event + '/' + key + '?' + headerKey + '=' + headerValue

def makeRequest(url):
	http = urllib3.PoolManager()
	r = http.request('GET', url)
	return r.data

def getEventTeamsRequestKey(competition, year):
	return "event/{year}{competition}/teams".format(competition = competition, year = year)

def makeEventTeamsRequest(competition, year):
	return makeRequest(makeYearEventKeyRequestURL(year, competition, 'teams'))



def addTeamsToFirebaseForEventCodeAndYear(eventCode, year): 
	print "\nDoing Teams..."
	casj2015TeamsArray = readJSONFromString(makeEventTeamsRequest(eventCode, year))
	teamObjectsBeingCreated = []
	for team in casj2015TeamsArray:
		print str(team["team_number"]) + ",", # This is weird syntax, I'm aware. The comma on the end tells it not to print a new line, but to do a space instead
		#if team["team_number"] == 254: #DEBUG
		#	break
		t = DataModel.Team()
		t.number = team["team_number"]
		t.name = team["nickname"]
		teamObjectsBeingCreated.append(t)
		updateFirebaseWithTeam(t)
		teams.append(t)
	


def addMatchesToFirebaseForEventCodeAndYear(eventCode, year):
	print "\nDoing Matches..."
	casj2015MatchesArray = readJSONFromString(makeRequest(makeYearEventKeyRequestURL(year, eventCode, 'matches')))
	matchObjectsBeingCreated = []
	for match in casj2015MatchesArray:
		#if match["match_number"] == 10: #DEBUG
		#	break
		if match["comp_level"] != "qm":
			continue # goes to next loop iteration
		m = DataModel.Match()
		alliancesDict = match["alliances"]
		m.number = match["match_number"]
		print str(m.number) + ",",
		m.blueScore = alliancesDict["blue"]["score"]
		m.redScore = alliancesDict["red"]["score"]
		m.blueAllianceTeamNumbers = alliancesDict["blue"]["teams"]
		m.redAllianceTeamNumbers = alliancesDict["red"]["teams"]
		updateFirebaseWithMatch(m)
		matches.append(m)

def addTIMDsToFirebase():
	print "Doing TIMDs...\n"
	for match in matches:
		for team in match.redAllianceTeamNumbers:
			teamNumber = int(team.replace("frc", ""))
			timd = makeTIMDFromTeamNumberAndMatchNumber(teamNumber, match.number)
			updateFirebaseWithTIMD(timd)
		for team in match.blueAllianceTeamNumbers:
			teamNumber = int(team.replace("frc", ""))
			timd = makeTIMDFromTeamNumberAndMatchNumber(teamNumber, match.number)
			updateFirebaseWithTIMD(timd)

def makeFakeDatabase(eventCode='casj', year=2015):
	addTeamsToFirebaseForEventCodeAndYear(eventCode, year)
	addMatchesToFirebaseForEventCodeAndYear(eventCode, year)
	addTIMDsToFirebase()

makeFakeDatabase()
print teamInMatchDatas
''' # DEBUG
teams = []
for i in teams:
	updateFirebaseWithTeam(makeTeamObjectWithNumberAndName(i, "none"))
'''