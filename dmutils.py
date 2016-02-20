import DataModel



comp = DataModel.Competition()

# Team utility functions
def getTeamForNumber(self, teamNumber):
	return [team for team in self.comp.teams if team.number == teamNumber][0]

def getMatchesForTeam(self, team):
	return [match for match in self.comp.matches if self.teamInMatch(team, match)]

def getCompletedMatchesForTeam(self, team):
	return filter(self.matchIsCompleted, self.getMatchesForTeam(team))

def getPlayedTIMDsForTeam(self, team):
	return [timd for timd in self.getTIMDsForTeamNumber(team.number) if self.timdIsPlayed(timd)]

def getCompletedTIMDsForTeam(self, team):
	return [timd for timd in self.getTIMDsForTeamNumber(team.number) if self.timdIsCompleted(timd)]

# Match utility functions
def getMatchForNumber(self, matchNumber):
	return [match for match in self.comp.matches if match.number == matchNumber][0]

def teamsInMatch(self, match):
	teamNumbersInMatch = match.redAllianceTeamNumbers
	teamNumbersInMatch.extend(match.blueAllianceTeamNumbers)
	return [self.getTeamForNumber(teamNumber) for teamNumber in teamNumbersInMatch]

def teamInMatch(self, team, match):
	return team in self.teamsInMatch(match)

def matchIsPlayed(self, match):
	return match.redScore != None or match.blueScore != None

def matchIsCompleted(self, match):
	return len(self.getCompletedTIMDsForMatchNumber(match.number)) == 6

def matchTIMDsForTeamAlliance(self, team, match):
	if team.number in match.blueAllianceTeamNumbers:
		return [self.getTIMDForTeamNumberAndMatchNumber(teamNum, match.number) for teamNum in match.blueAllianceTeamNumbers]
	if team.number in match.blueAllianceTeamNumbers:
		return map(self.getTIMDForTeamNumberAndMatchNumber(teamNum, match.number), match.blueAllianceTeamNumbers)

# TIMD utility functions
def getTIMDsForTeamNumber(self, teamNumber):
	return [timd for timd in self.comp.TIMDs if timd.teamNumber == teamNumber]

def getCompletedTIMDsForTeamNumber(self, teamNumber):
	return filter(self.timdIsCompleted, self.getTIMDsForTeamNumber(teamNumber))

def getCompletedTIMDsForTeam(self, team):
	return self.getCompletedTIMDsForTeamNumber(team.number)

def getPlayedTIMDsForTeamNumber(self, teamNumber):
	return filter(self.timdIsPlayed, self.getTIMDsForTeamNumber(teamNumber))

def getTIMDsForMatchNumber(self, matchNumber):
	return [timd for timd in self.comp.TIMDs if timd.matchNumber == matchNumber]

def getCompletedTIMDsForMatchNumber(self, matchNumber):
	return filter(self.timdIsCompleted, self.getTIMDsForMatchNumber(matchNumber))

def timdIsPlayed(self, timd):
	isPlayed = False 
	for key, value in utils.makeDictFromTIMD(timd).items():
		if value != None:
			isPlayed = True
	return isPlayed

exceptedKeys = ['calculatedData', 'ballsIntakedAuto', 'superNotes']

def timdIsCompleted(self, timd):
	isCompleted = True 
	for key, value in utils.makeDictFromTIMD(timd).items():
		if key not in self.exceptedKeys and value == None:
			isCompleted = False
	return isCompleted



	