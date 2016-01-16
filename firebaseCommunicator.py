import DataModel
import utils
from firebase import firebase as fb

superSecret = "j1r2wo3RUPMeUZosxwvVSFEFVcrXuuMAGjk6uPOc"

auth = fb.FirebaseAuthentication(superSecret, "1678programming@gmail.com", True, True)
firebase = fb.FirebaseApplication('https://1678-dev-2016.firebaseio.com/', auth)

class FirebaseCommunicator(object):
	"""docstring for FirebaseCommunicator"""
	def __init__(self, arg=None):
		super(FirebaseCommunicator, self).__init__()
		self.arg = arg
		self.JSONmatches = []
		self.JSONteams = []

	def updateFirebaseWithTeam(self, team):
		teamDict = utils.makeDictFromTeam(team)
		FBLocation = "/Teams"
		result = firebase.put(FBLocation, team.number, teamDict)

	def updateFirebaseWithMatch(self, match):
		matchDict = utils.makeDictFromMatch(match)
		FBLocation = "/Matches"
		result = firebase.put(FBLocation, match.number, matchDict)

	def updateFirebaseWithTIMD(self, timd):
		timdDict = utils.makeDictFromTIMD(timd)
		FBLocation = "/TeamInMatchDatas"
		result = firebase.put(FBLocation, str(timd.teamNumber) + "Q" + str(timd.matchNumber), timdDict)


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

	def addTIMDsToFirebase(self, matches):
		print "Doing TIMDs...\n"
		for match in matches:
			print match.redAllianceTeamNumbers
			for team in match.redAllianceTeamNumbers:
				teamNumber = int(team.replace("frc", ""))
				timd = utils.makeTIMDFromTeamNumberAndMatchNumber(teamNumber, match.number)
				self.updateFirebaseWithTIMD(timd)
			for team in match.blueAllianceTeamNumbers:
				teamNumber = int(team.replace("frc", ""))
				timd = utils.makeTIMDFromTeamNumberAndMatchNumber(teamNumber, match.number)
				self.updateFirebaseWithTIMD(timd)

def getPythonObjectForFirebaseDataAtLocation(location):
	# The location will be a key path, like '/' for the root (entire) object.
	result = firebase.get(location, None)
	'''
	Supposedly you can add other request parameters
	But it was throwing errors when I tried it, soo...
	But they will be JSON formatted get request parameters. :)
	'''
	return result
