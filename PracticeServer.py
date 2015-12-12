# by Bryton Moeller (Sept 27, 2015 to Dec 11, 2015 to ...)

import json
from firebase import firebase
import urllib3
from StringIO import StringIO


firebase = firebase.FirebaseApplication('https://sizzling-heat-1224.firebaseio.com/', None)

teams = []
matches = []
teamInMatchDatas = []

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

class CalculatedTeamData(object):
	"""The calculatedData for an FRC Team object"""
	def __init__(self):
		super(CalculatedTeamData, self).__init__()
		self.driverAbility = -1

		

class Team(object):
	"""An FRC Team object"""

	def __init__(self, **args):
		super(Team, self).__init__()
		self.name = "noName"
		self.number = -1
		self.matches = []
		self.teamInMatchDatas = []
		self.calculatedData = CalculatedTeamData()
		self.__dict__.update(args)

class Match(object):
	"""An FRC Match Object"""
	def __init__(self, **args):
		super(Match, self).__init__()
		self.number = -1
		self.redAllianceTeamNumbers = []
		self.blueAllianceTeamNumbers = []
		self.redScore = -1
		self.blueScore = -1
		self.__dict__.update(args)
		
class TeamInMatchData(object):
	"""An FRC TeamInMatchData Object"""
	def __init__(self, **args):
		super(TeamInMatchData, self).__init__()
		self.teamNumber = -1
		self.matchNumber = -1
		self.__dict__.update(args)

		

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












basicURL = "http://www.thebluealliance.com/api/v2/"

headerKey = "X-TBA-App-Id"
headerValue = "blm:serverProof1678:003" # set to "<your initials>:TBA_communicator:0"


def makeYearEventKeyRequestURL(year, event, key):
	return basicURL + 'event/' + str(year) + event + '/' + key + '?' + headerKey + '=' + headerValue


def makeRequest(url):
	http = urllib3.PoolManager()
	r = http.request('GET', url)
	return r.data

def makeTIMDFromTeamNumberAndMatchNumber(teamNumber, matchNumber):
	timd = TeamInMatchData()
	timd.teamNumber = teamNumber
	timd.matchNumber = matchNumber
	teamInMatchDatas.append(timd)
	return timd

def getEventTeamsRequestKey(competition, year):
	return "event/{year}{competition}/teams".format(competition = competition, year = year)

def makeEventTeamsRequest(competition, year):
	return makeRequest(makeYearEventKeyRequestURL(year, competition, 'teams'))

#Teams
print "Doing Teams...\n"
casj2015TeamsArray = readJSONFromString(makeEventTeamsRequest('casj', 2015))
teamObjectsBeingCreated = []
for team in casj2015TeamsArray:
	print team["team_number"]
	if team["team_number"] == 254:
		break
	t = Team()
	t.number = team["team_number"]
	t.name = team["nickname"]
	teamObjectsBeingCreated.append(t)
	updateFirebaseWithTeam(t)
	teams.append(t)


#Matches
print "Doing Matches...\n"
casj2015MatchesArray = readJSONFromString(makeRequest(makeYearEventKeyRequestURL(2015, 'casj', 'matches')))
matchObjectsBeingCreated = []
for match in casj2015MatchesArray:
	#if match["match_number"] == 10:
	#	break
	if match["comp_level"] != "qm":
		next
	m = Match()
	alliancesDict = match["alliances"]
	m.number = match["match_number"]
	m.blueScore = alliancesDict["blue"]["score"]
	m.redScore = alliancesDict["red"]["score"]
	m.blueAllianceTeamNumbers = alliancesDict["blue"]["teams"]
	m.redAllianceTeamNumbers = alliancesDict["red"]["teams"]
	updateFirebaseWithMatch(m)
	matches.append(m)

#TeamInMatchDatas
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


'''
teams = []
for i in teams:
	updateFirebaseWithTeam(makeTeamObjectWithNumberAndName(i, "none"))
'''