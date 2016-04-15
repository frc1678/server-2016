import DataModel
import utils
import json
from firebase import firebase as fb
import unicodedata
from os import listdir
import pdb
import math
import datetime

(superSecret, url) = ('j1r2wo3RUPMeUZosxwvVSFEFVcrXuuMAGjk6uPOc', 'https://1678-dev-2016.firebaseio.com/')
# (superSecret, url) = ('hL8fStivTbHUXM8A0KXBYPg2cMsl80EcD7vgwJ1u', 'https://1678-dev2-2016.firebaseio.com/')
#(superSecret, url) = ('AEduO6VFlZKD4v10eW81u9j3ZNopr5h2R32SPpeq', 'https://1678-dev3-2016.firebaseio.com/')
# (superSecret, url) = ('IMXOxXD3FjOOUoMGJlkAK5pAtn89mGIWAEnaKJhP', 'https://1678-strat-dev-2016.firebaseio.com/')
# (superSecret, url) = ('qVIARBnAD93iykeZSGG8mWOwGegminXUUGF2q0ee', 'https://1678-scouting-2016.firebaseio.com/')
# 
auth = fb.FirebaseAuthentication(superSecret, "1678programming@gmail.com", True, True)

firebase = fb.FirebaseApplication(url, auth)

class FirebaseCommunicator(object):
	"""docstring for FirebaseCommunicator"""
	def __init__(self, competition):
		super(FirebaseCommunicator, self).__init__()
		self.JSONmatches = []
		self.JSONteams = []
		self.competition = competition

	def updateFirebaseWithTeam(self, team):
		teamDict = utils.makeDictFromTeam(team)
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

	def addCalculatedTeamDataToFirebase(self, team):
		print "Writing team " + str(team.number) + " to Firebase..."
		calculatedTeamDataDict = utils.makeDictFromCalculatedTeamData(team.calculatedData)
		FBLocation = "/Teams/" + str(team.number) 
		result = firebase.put(FBLocation, 'calculatedData', calculatedTeamDataDict)

	def addCalculatedTIMDataToFirebase(self, timd):
		print "Writing team " + str(timd.teamNumber) + " in match " + str(timd.matchNumber) + " to Firebase..."
		calculatedTIMDataDict = utils.makeDictFromCalculatedTIMData(timd.calculatedData)
		FBLocation = "/TeamInMatchDatas/" + str(timd.teamNumber) + "Q" + str(timd.matchNumber)
		result = firebase.put(FBLocation, 'calculatedData', calculatedTIMDataDict)

	def addCalculatedMatchDataToFirebase(self, match):
		print "Writing match " + str(match.number) + " to Firebase..."
		calculatedMatchDataDict = utils.makeDictFromCalculatedMatchData(match.calculatedData)
		'''for (key, value) in calculatedMatchDataDict:
			if math.isnan(value):
				d[key] = None'''
		FBLocation = "/Matches/" + str(match.number)
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
			t.teamInMatchDatas = []
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
			m.TIMDs = []
			self.updateFirebaseWithMatch(m)

	def addScorelessMatchesToFirebase(self):
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
			m.blueScore = None
			m.redScore = None
			m.blueAllianceTeamNumbers = alliancesDict["blue"]["teams"]
			m.redAllianceTeamNumbers = alliancesDict["red"]["teams"]
			m.TIMDs = []
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
		
		self.competition.averageScore = None

	def wipeDatabase(self):
		map(utils.printWarningForSeconds, range(10, 0, -1))
		print "\nWARNING: Wiping Firebase..."
		FBLocation = "/"
		firebase.put(FBLocation, 'Teams', [])
		firebase.put(FBLocation, 'Matches', [])
		firebase.put(FBLocation, 'TeamInMatchDatas', [])

	def addScoutScoresToFirebase(self, scoutScores):
		print "Writing Scout Scores to Firebase"
		FBLocation = "/"
		result = firebase.put(FBLocation, 'Scout Scores', scoutScores)


	def cacheFirebase(self):
		numFiles = len(listdir("CachedFirebases"))
		data = json.dumps(firebase.get("/", None))
		now = str(datetime.datetime.now())
		with open("./CachedFirebases/" + now + '.json', 'w') as f:
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


