# Data Validation Module, by Bryton Moeller, Feb 4, 2016
import DataModel
import firebaseCommunicator
import utils
import math

class DataValidator(object):
	"""docstring for DataValidator"""
	def __init__(self, competition):
		super(DataValidator, self).__init__()
		self.competition = competition
		self.defensesDict = {
		 	'a' : {'pc' : None, 'cdf' : None},
			'b' : {'mt' : None, 'rp' : None},
			'c' : {'db' : None, 'sp' : None},
			'd' : {'rw' : None, 'rt' : None},
			'e' : {'lb' : None}
		}
		self.valueNotUploaded = [-1, -1.0, "-1", ['-1'], self.defensesDict, False, {}, ['lb', '', '', '', ''], {1678: -1}, {"not0": "-1"}, None]
		self.exceptedKeys = ['name', 'number', 'calculatedData', 'teamInMatchDatas', 'matches', 'pit', 'selectedImageUrl']

	def validateFirebase(self):
		print("Teams Validation Problems: " + str(self.validateTeams(self.competition.teams, True)))
		print("Matches Validation Problems: " + str(self.validateMatches(self.competition.matches)))

	def someValuesNotUploaded(self, team):
		items = utils.makeDictFromTeam(team).items()
		notUploaded = lambda k, v: v in self.valueNotUploaded and k not in self.exceptedKeys and 'pit' not in k	
		return [p for (p,v) in items if notUploaded(p,v)] if sum([not notUploaded(p,v) for (p,v) in items]) < len(items) else []

	def validateTeams(self, teams, shouldValidateCalculatedTeamData):
		problems = []
		for team in teams:
			thereHasBeenunuploaded1 = False
			thereHasBeenuploaded = False
			unuploaded = ""
			uploaded = ""
			t = utils.makeDictFromTeam(team).items()
			for key, value in t:
				if key == "calculatedData" and shouldValidateCalculatedTeamData:
					ctdProblems = self.validateCalculatedTeamData(value, team.number)
					if ctdProblems != []:
						problems.append(ctdProblems)
				
				if key == "teamInMatchDatas":
					if value != None:
						for TIMD in value:
						 	timdProblems = self.validateTeamInMatchData(utils.makeDictFromTIMD(TIMD))
						 	if timdProblems != []:
						 		problems.append(timdProblems)
				if self.someValuesNotUploaded(team) != []: 
					problems.append(self.someValuesNotUploaded(team))		
		return problems

	def validateCalculatedTeamData(self, CTD, teamNumber):
		problems = []
		calcD = CTD.items()
		for key, value in calcD:
			# unuploaded and uploaded values
			thereHasBeenunuploaded1 = False
			thereHasBeenuploaded = False
			if (value in self.valueNotUploaded):
				thereHasBeenunuploaded1 = True
			else:
				thereHasBeenuploaded = True
			if thereHasBeenunuploaded1 and thereHasBeenuploaded:
				problems.append(str(teamNumber) + ": Has an unuploaded in one CALCULATED DATA value, but not in another.")
				#break I want to do more validation

			if isinstance(value, (float, int, long, complex)) and math.isnan(float(value)): problems.append(str(teamNumber) + "'s CALCULATED DATA: Has a nan for " + key)
			if 'percentage' in key and not (value >= 0.0 and value <= 1.0): problems.append(str(teamNumber) + "'s CALCULATED DATA has a value of " + key + " that is not between 0 and 1.")

		return problems



	def validateTeamInMatchData(self, TIMD):
		problems = []
		for key, value in TIMD.items():
			thereHasBeenunuploaded1 = False
			thereHasBeenuploaded = False
			if (value in self.valueNotUploaded) or key != "name" or key != "number":
				thereHasBeenunuploaded1 = True
			else:
				thereHasBeenuploaded = True
			
			if thereHasBeenunuploaded1 and thereHasBeenuploaded:
				problems.append(str(TIMD["teamNumber"]) + ": Has an unuploaded in one TEAM IN MATCH DATA value, but not in another.")
				break
		return problems





	def validateMatches(self, matches):
		problems = []
		# for matchL in matches:
		# 	matchNumbers = {}
		# 	for timd in self.competition.TIMDs:
		# 		if timd.matchNumber not in matchNumbers.keys(): 
		# 			matchNumbers[timd.matchNumber] = []
		# 		matchNumbers[timd.matchNumber].append(timd.teamNumber)
		# 	for key in matchNumbers.keys():
		# 		if len(matchNumbers[key]) > 6:
		# 			problems.append("There are more than 6 TIMDs for match " + str(key) + ". The teams are " + str(matchNumbers[key]) + ".")
		# 	match = utils.makeDictFromMatch(matchL)
		# 	if match["redScore"] > -0.5 or match["blueScore"] > -0.5:
		# 		for timd in match["TIMDs"]:
		# 			if timd.rankTorque < 0:
		# 				problems.append("TIMD: " + str(timd.teamNumber) + "Q" + str(timd.matchNumber) + " should be played but isn't.")
		return problems
