import DataModel
import json
from StringIO import StringIO
import time
import math
import numpy as np
import pdb

########## Defining Util/Convenience Functions ############
''' If there were too many more of these, or if this 
were actual server code, I would make a module, but 
for fake database creation purposes it is not worth it'''

# def assign(object, retrievalFunction, value):
# 	retrievalFunction(object) = value

def sumStdDevs(stdDevs):
	return sum(map(lambda x: x ** 2, stdDevs)) ** 0.5

def convertFirebaseBoolean(fbBool):
	return True if fbBool == 'true' else False

def rms(values):
	if len(values) == 0: return None
	return math.sqrt(np.mean(map(lambda x: x**2, values)))

def convertNoneToIdentity(x, identity):
	return identity if x == None else x

def dictOperation(dict1, dict2, dictOp, identity):
	newDict = {}
	map(lambda k: setDictionaryValue(newDict, k, dictOp(convertNoneToIdentity(dict1[k], identity), convertNoneToIdentity(dict2[k], identity))), dict1)
	return newDict

def dictSum(dict1, dict2):
	return dictOperation(dict1, dict2, lambda x, y: x + y, 0)

def dictDifference(dict1, dict2):
	return dictOperation(dict1, dict2, lambda x, y: x - y, 0)

def dictProduct(dict1, dict2):
	return dictOperation(dict1, dict2, lambda x, y: x * y, 1)

def dictQuotient(dict1, dict2):
	return dictOperation(dict1, dict2, lambda x, y: float(x) / float(y) if float(y) != 0.0 else None, 1.0)

def dictPercentage(dict1, dict2):
	print dictSum(dict1, dict2)
	return dictQuotient(dict1, dictSum(dict1, dict2))

def dictDivideConstant(dict, constant):
	returnDict = {}
	for key, value in dict.iteritems():
		returnDict[key] = float(value) / constant
	return returnDict

def stdDictSum(dict1, dict2):
	return dictOperation(dict1, dict2, lambda x, y: sumStdDevs([x, y]))

def setDictionaryValue(dict, key, value):
	dict[key] = value

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
	if 'calculatedData' in d.keys():
		match.calculatedData = DataModel.CalculatedMatchData(**d['calculatedData'])
	return match


def makeTeamFromDict(d):
	team = DataModel.Team(**d) #I have no idea why this works
	if 'calculatedData' in d.keys():
		team.calculatedData = DataModel.CalculatedTeamData(**d['calculatedData'])
		d = DataModel.Team(**d)
		d.calculatedData = DataModel.CalculatedTeamData(**d.calculatedData)
	# print("tn: " + str(team.number) + str(d['number']))
	return team


def makeTIMDFromDict(d):
	timd = DataModel.TeamInMatchData(**d) #I have no idea why this works
	if 'calculatedData' in d.keys():
		timd.calculatedData = DataModel.CalculatedTeamInMatchData(**d['calculatedData'])
	return timd


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

'''
def makeDictFromTeamOld(t):
	d = t.__dict__
	if not isinstance(t.calculatedData, dict):
		d["calculatedData"] = t.calculatedData.__dict__
	return d
'''
def makeDictFromObject(o):
	if isinstance(o, dict): 
		for k, v in o.iteritems():
			if v.__class__ in [DataModel.CalculatedTeamData, DataModel.CalculatedMatchData, DataModel.CalculatedTeamInMatchData]:
				o[k] = v.__dict__
		return o
	return dict((key, value) for key, value in o.__dict__.iteritems() if not callable(value) and not key.startswith('__'))

def readValueFromObjectDict(objectDict, key):
	return objectDict[key]

def makeDictFromTeam(t):
	d = makeDictFromObject(t)
	d['calculatedData'] = makeDictFromObject(d['calculatedData'])
	return d
'''
def makeDictFromMatchOld(t):
 	d = t.__dict__
 	if not isinstance(t.calculatedData, dict):
 		d["calculatedData"] = t.calculatedData.__dict__
 	return d
 '''
def makeDictFromMatch(t):
	d = makeDictFromObject(t)
	d['calculatedData'] = makeDictFromObject(d['calculatedData'])
	return d

def makeDictFromTIMD(timd):
	d = makeDictFromObject(timd)
	d["calculatedData"] = makeDictFromObject(d['calculatedData'])
	return d


def makeDictFromCalculatedTeamData(calculatedData):
	return calculatedData.__dict__

def makeDictFromCalculatedMatchData(calculatedData):
	return calculatedData.__dict__

def makeDictFromCalculatedTIMData(calculatedData):
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

def printWarningForSeconds(numSeconds):
		print str(numSeconds) + ' SECONDS UNTIL FIREBASE WIPES'
		time.sleep(1)


