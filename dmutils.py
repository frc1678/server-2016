import DataModel
import utils

comp = DataModel.Competition()

comp.updateTeamsAndMatchesFromFirebase()
comp.updateTIMDsFromFirebase()


# Team utility functions
def getTeamForNumber(teamNumber):
	return [team for team in comp.teams if team.number == teamNumber][0]

def getMatchesForTeam(team):
	return [match for match in comp.matches if teamInMatch(team, match)]

def getCompletedMatchesForTeam(team):
	return filter(matchIsCompleted, getMatchesForTeam(team))

def getPlayedTIMDsForTeam(team):
	return [timd for timd in getTIMDsForTeamNumber(team.number) if timdIsPlayed(timd)]

def getCompletedTIMDsForTeam(team):
	return [timd for timd in getTIMDsForTeamNumber(team.number) if timdIsCompleted(timd)]

def teamsWithMatchesCompleted():
	return [team for team in comp.teams if len(getCompletedTIMDsForTeam(team)) > 0]

# Match utility functions
def getMatchForNumber(matchNumber):
	return [match for match in comp.matches if match.number == matchNumber][0]

def teamsInMatch(match):
	teamNumbersInMatch = match.redAllianceTeamNumbers
	teamNumbersInMatch.extend(match.blueAllianceTeamNumbers)
	return [getTeamForNumber(teamNumber) for teamNumber in teamNumbersInMatch]

def teamInMatch(team, match):
	return team in teamsInMatch(match)

def matchIsPlayed(match):
	return match.redScore != None or match.blueScore != None

def matchIsCompleted(match):
	return len(getCompletedTIMDsForMatchNumber(match.number)) == 6

def matchTIMDsForTeamAlliance(team, match):
	if team.number in match.blueAllianceTeamNumbers:
		return map(getTIMDForTeamNumberAndMatchNumber(teamNum, match.number), match.blueAllianceTeamNumbers)
	if team.number in match.redAllianceTeamNumbers:
		return map(getTIMDForTeamNumberAndMatchNumber(teamNum, match.number), match.redAllianceTeamNumbers)

def getAllTIMDsForMatch(match):
	return [timd for timd in comp.TIMDs if timd.matchNumber == match.number]

def matchHasAllTeams(match):
	return len(getAllTIMDsForMatch(match)) == 6		

def matchesThatHaveBeenPlayed():
	return [match for match in comp.matches if matchHasAllTeams(match)]

# TIMD utility functions
def getTIMDsForTeamNumber( teamNumber):
	return [timd for timd in comp.TIMDs if timd.teamNumber == teamNumber]

def getCompletedTIMDsForTeamNumber( teamNumber):
	return filter(timdIsCompleted, getTIMDsForTeamNumber(teamNumber))

def getCompletedTIMDsForTeam( team):
	return getCompletedTIMDsForTeamNumber(team.number)

def getPlayedTIMDsForTeamNumber( teamNumber):
	return filter(timdIsPlayed, getTIMDsForTeamNumber(teamNumber))

def getTIMDsForMatchNumber( matchNumber):
	return [timd for timd in comp.TIMDs if timd.matchNumber == matchNumber]

def getCompletedTIMDsForMatchNumber( matchNumber):
	return filter(timdIsCompleted, getTIMDsForMatchNumber(matchNumber))

def getTIMDForTeamNumberAndMatchNumber(teamNumber, matchNumber):
	return [timd for timd in getTIMDsForTeamNumber(teamNumber) if timd.matchNumber == matchNumber][0]	

def timdIsPlayed( timd):
	isPlayed = False 
	for key, value in utils.makeDictFromTIMD(timd).items():
		if value != None:
			isPlayed = True
	return isPlayed

def teamsAreOnSameAllianceInMatch(team1, team2, match):
		areInSameMatch = False
		alliances = [match.redAllianceTeamNumbers, match.blueAllianceTeamNumbers]
		for alliance in alliances:
			if team1.number in alliance and team2.number in alliance:
				areInSameMatch = True
		return areInSameMatch

exceptedKeys = ['calculatedData', 'ballsIntakedAuto', 'superNotes']

def timdIsCompleted( timd):
	isCompleted = True 
	for key, value in utils.makeDictFromTIMD(timd).items():
		if key not in exceptedKeys and value == None:
			isCompleted = False
	return isCompleted