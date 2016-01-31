import DataModel
import json
from StringIO import StringIO

########## Defining Util/Convenience Functions ############
''' If there were too many more of these, or if this 
were actual server code, I would make a module, but 
for fake database creation purposes it is not worth it'''

def jprint(JSON):
	print(json.dumps(JSON, sort_keys=True, indent=4))

def makeASCIIFromJSON(input):
    if isinstance(input, dict):
        return { makeASCIIFromJSON(key) : makeASCIIFromJSON(value) for key, value in input.iteritems() }
    elif isinstance(input, list):
        return [makeASCIIFromJSON(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def readJSONFromString(string):
	return makeASCIIFromJSON(json.load(StringIO(string)))


def readJSONFileToObj(fileName):
	fileInput = open(fileName, 'r')
	pythonObj = json.load(fileInput)
	return pythonObj


def makeMatchFromDict(d):
	match = DataModel.Match(**d) #I have no idea why this works
	match.calculatedData = DataModel.CalculatedMatchData(**d['calculatedData'])
	return match


def makeTeamFromDict(d):
	team = DataModel.Team(**d) #I have no idea why this works
	team.calculatedData = DataModel.CalculatedTeamData(**d['calculatedData'])
	return team


def makeTIMDFromDict(d):
	TIMD = DataModel.TeamInMatchData(**d)
	return TIMD


def makeTeamsFromDicts(dicts):
	teams = []
	for key in dicts.keys():
		teams.append(makeTeamFromDict(dicts[key]))
	return teams


def makeMatchesFromDicts(dicts):
	matches = []
	for match in dicts:
		if match == None:
			continue
		matches.append(makeMatchFromDict(match))
	return matches


def makeDictFromTeam(t):
	d = t.__dict__
	if not isinstance(t.calculatedData, dict):
		d["calculatedData"] = t.calculatedData.__dict__
	return d


def makeDictFromMatch(m):
	d = m.__dict__
	if not isinstance(m.calculatedData, dict):
		d["calculatedData"] = m.calculatedData.__dict__
	return d


def makeDictFromTIMD(timd):
	d = timd.__dict__
	return d


def makeDictFromCalculatedTeamData(calculatedData):
	return calculatedData.__dict__


def makeTIMDsFromDicts(timds):
	t = []
	for key in timds.keys():
		if key == None:
			continue
		t.append(makeTIMDFromDict(timds[key]))
	return t


def makeTeamObjectWithNumberAndName(number, name):
	team = Team()
	team.name = name
	team.number = number
	return team


def makeTIMDFromTeamNumberAndMatchNumber(teamNumber, matchNumber):
	timd = DataModel.TeamInMatchData()
	timd.teamNumber = teamNumber
	timd.matchNumber = matchNumber
	return timd


def makeArrayOfTeamNumAndMatchNum(teamNum):
	timds = []
	for timd in self.comp.TIMDs:
		if timd.teamNumber == teamNum:
			teamNumAndMatchNum = teamNum + "Q" + str(timd.matchNumber)			




