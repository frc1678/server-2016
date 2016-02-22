import DataModel
import utils
import pdb

defenseDictionary = {'a' : ['pc', 'cdf'],
			'b' : ['mt', 'rp'],
			'c' : ['sp', 'db'],
			'd' : ['rw', 'rt'],
			'e' : ['lb']
		}

defensesList = ['pc', 'cdf', 'mt', 'rp', 'sp', 'db', 'rw', 'rt', 'lb']

def setCompetition(competition):
	comp = competition

def getDefenseRetrievalFunctionForDefense(retrievalFunction, defenseKey):
	return lambda t: retrievalFunction(t)[defenseKey]
	return getDefenseRetrievalFunctionForCategoryAndDefenseForRetrievalFunction(retrievalFunction, defenseKey)

def getDefenseRetrievalFunctions(retrievalFunction):
	return map(lambda dKey: getDefenseRetrievalFunctionForDefense(retrievalFunction, dKey), defensesList)

def getValuedDefenseRetrievalFunctionsForTeam(team, retrievalFunction):
	return filter(lambda f: f(team) != None, getDefenseRetrievalFunctions(retrievalFunction))

# Team utility functions
def getTeamForNumber(teamNumber):
	return [team for team in comp.teams if team.number == teamNumber][0]

def teamsWithCalculatedData():
	return filter(lambda t: calculatedDataHasValues(t.calculatedData), comp.teams)

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

def getColorFromTeamAndMatch(team, match):
	blue = map(getTeamForNumber, match.blueAllianceTeamNumbers)
	red = map(getTeamForNumber, match.redAllianceTeamNumbers)
	return blue if team in blue else red

def getOppColorFromTeamAndMatch(team, match):
	blue = map(getTeamForNumber, match.blueAllianceTeamNumbers)
	red = map(getTeamForNumber, match.redAllianceTeamNumbers)
	return blue if team in red else red

def getAllTeamMatchAlliances(team):
	return [getColorFromTeamAndMatch(team, match) for match in getCompletedMatchesForTeam(team)]

def getAllTeamOppositionAlliances(team):
	return [getOppColorFromTeamAndMatch(team, match) for match in getCompletedMatchesForTeam(team)]

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

def matchesThatHaveBeenCompleted():
	return [match for match in comp.matches if matchIsCompleted(match)]

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

def getCompletedTIMDsForMatchNumber(matchNumber):
	return filter(timdIsCompleted, getTIMDsForMatchNumber(matchNumber))

def getTIMDForTeamNumberAndMatchNumber(teamNumber, matchNumber):
	return [timd for timd in getTIMDsForTeamNumber(teamNumber) if timd.matchNumber == matchNumber][0]	

def getCompletedTIMDsInCompetition():
	return [timd for timd in comp.TIMDs if timdIsCompleted(timd)]

def calculatedDataHasValues(calculatedData):
	hasValues = False 
	for key, value in utils.makeDictFromObject(calculatedData).items():
		if value != None and not 'Defense' in key and not 'defense' in key and not 'second' in key:
			hasValues = True
	return hasValues

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

def timdIsCompleted(timd):
	isCompleted = True 
	for key, value in utils.makeDictFromTIMD(timd).items():
		if key not in exceptedKeys and value == None:
			isCompleted = False
	return isCompleted