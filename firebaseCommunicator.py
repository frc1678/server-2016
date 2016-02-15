import DataModel
import utils
import json
from firebase import firebase as fb
import unicodedata
import random
from os import listdir

#superSecret = "j1r2wo3RUPMeUZosxwvVSFEFVcrXuuMAGjk6uPOc" #dev
superSecret = "hL8fStivTbHUXM8A0KXBYPg2cMsl80EcD7vgwJ1u" #dev2
#superSecret = "AEduO6VFlZKD4v10eW81u9j3ZNopr5h2R32SPpeq" #dev3
#superSecret = "qVIARBnAD93iykeZSGG8mWOwGegminXUUGF2q0ee" #scouting

auth = fb.FirebaseAuthentication(superSecret, "1678programming@gmail.com", True, True)

firebase = fb.FirebaseApplication('https://1678-dev2-2016.firebaseio.com/', auth)

class FirebaseCommunicator(object):
	"""docstring for FirebaseCommunicator"""
	def __init__(self, competition):
		super(FirebaseCommunicator, self).__init__()
		self.JSONmatches = []
		self.JSONteams = []
		self.competition = competition

	def updateFirebaseWithTeam(self, team):
		teamDict = utils.makeDictFromTeam(team)
		#teamDict['name'] = unicodedata.normalize('NFKD', teamDict['name']).encode('ascii','ignore') # For some strange reason the names of the teams are all in unicode strings
		FBLocation = "/Teams"
		result = firebase.put(FBLocation, team.number, teamDict)

	def updateFirebaseWithMatch(self, match):
		matchDict = utils.makeDictFromMatch(match)
		FBLocation = "/Matches"
		tempA = []
		for number in matchDict["blueAllianceTeamNumbers"]:
			tempA.append(int(number.replace('frc', '')))
		matchDict["blueAllianceTeamNumbers"] = tempA
		tempA = []
		for number in matchDict["redAllianceTeamNumbers"]:
			tempA.append(int(number.replace('frc', '')))
		matchDict["redAllianceTeamNumbers"] = tempA
		result = firebase.put(FBLocation, match.number, matchDict)

	def updateFirebaseWithTIMD(self, timd):
		timdDict = utils.makeDictFromTIMD(timd)
		FBLocation = "/TeamInMatchDatas"
		print(str(timd.teamNumber) + "Q" + str(timd.matchNumber)) + "," ,
		result = firebase.put(FBLocation, str(timd.teamNumber) + "Q" + str(timd.matchNumber), timdDict)

	def addCalculatedTeamDataToFirebase(self, teamNumber, calculatedTeamData):
		calculatedTeamDataDict = utils.makeDictFromCalculatedTeamData(calculatedTeamData)
		FBLocation = "/Teams/" + str(teamNumber) 
		#print calculatedTeamDataDict
		result = firebase.put(FBLocation, 'calculatedData', calculatedTeamDataDict)

	def addCalculatedMatchDataToFirebase(self, matchNumber, calculatedMatchData):
		calculatedMatchDataDict = utils.makeDictFromCalculatedMatchData(calculatedMatchData)
		FBLocation = "/Matches/" + str(matchNumber)
		result = firebase.put(FBLocation, 'calculatedData', calculatedMatchDataDict)


	def addTeamsToFirebase(self): 
		print "\nDoing Teams..."
		for team in self.JSONteams:
			print str(team["team_number"]) + ",", # This is weird syntax, I'm aware. The comma on the end tells it not to print a new line, but to do a space instead
			#if team["team_number"] == 254: #DEBUG
			#	break
			t = DataModel.Team()
			t.number = team["team_number"]
			t.name = team["nickname"]
			self.updateFirebaseWithTeam(t)
		
	def addMatchesToFirebase(self):
		print "\nDoing Matches..."
		for match in self.JSONmatches:
			#if match["match_number"] == 14: #DEBUG
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
			self.updateFirebaseWithMatch(m)

	def addScorelessMatchesToFirebase(self):
		print "\nSetting Match Scores to -1..."
		for match in self.JSONmatches:
			#if match["match_number"] == 14: #DEBUG
			#	break
			if match["comp_level"] != "qm":
				continue # goes to next loop iteration
			m = DataModel.Match()
			alliancesDict = match["alliances"]
			m.number = match["match_number"]
			print str(m.number) + ",",
			m.blueScore = None
			m.redScore = None
			m.blueAllianceTeamNumbers = alliancesDict["blue"]["teams"]
			m.redAllianceTeamNumbers = alliancesDict["red"]["teams"]
			self.updateFirebaseWithMatch(m)

	def addTIMDsToFirebase(self, matches):
		print "\nDoing TIMDs..."
		for match in matches:
			for teamNum in match.redAllianceTeamNumbers:
				#teamNumber = int(teamNum.replace("frc", ""))
				timd = utils.makeTIMDFromTeamNumberAndMatchNumber(teamNum, match.number)
				self.updateFirebaseWithTIMD(timd)
			for teamNum in match.blueAllianceTeamNumbers:
				#teamNumber = int(teamNum.replace("frc", ""))
				timd = utils.makeTIMDFromTeamNumberAndMatchNumber(teamNum, match.number)
				self.updateFirebaseWithTIMD(timd)

	def addCompInfoToFirebase(self): #Doing these keys manually so less clicking in firebase is better and because just easier
		FBLocation = "/"
		result = firebase.put(FBLocation, 'code', self.competition.code)
		result = firebase.put(FBLocation, 'averageScore', self.competition.averageScore)
		
		self.competition.averageScore = -1

	def wipeDatabase(self):
		print "Wiping Firebase..."
		FBLocation = "/"
		firebase.put(FBLocation, 'Teams', [])
		firebase.put(FBLocation, 'Matches', [])
		firebase.put(FBLocation, 'TeamInMatchDatas', [])

	def cacheFirebase(self):
		numFiles = len(listdir("./CachedFirebases"))
		data = json.dumps(firebase.get("/", None))
		with open("./CachedFirebases/" + str(numFiles) + '.json', 'w') as f:
			f.write(data)
			f.close()


def getPythonObjectForFirebaseDataAtLocation(location):
	# The location will be a key path, like '/' for the root (entire) object.
	result = firebase.get(location, None)
	'''
	Supposedly you can add other request parameters
	But it was throwing errors when I tried it, soo...
	But they will be JSON formatted get request parameters. :)
	'''
	return utils.readJSONFromString(json.dumps(result))


