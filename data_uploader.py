import firebaseCommunicator
import json
import utils
import DataModel
import time

comp = DataModel.Competition()
comp.updateTeamsAndMatchesFromFirebase()
comp.updateTIMDsFromFirebase()

FBC = firebaseCommunicator.FirebaseCommunicator(comp)

dataFileName = raw_input('Input file name: ')
with open(dataFileName, 'r') as dataFile:
	jsonData = json.loads(dataFile.read())


timdsToUpload = {}
matchNumbers = []
for match in jsonData['Matches']:
	timdsToUpload[match['number']] = []
	matchNumbers.append(match['number'])

timdObjects = utils.makeTIMDsFromDicts(jsonData['TeamInMatchDatas'])
for timd in timdObjects:
	timdsToUpload[matchNumber].append(timd.matchNumber)

for matchNumber in matchNumbers:
	for timd in timdsToUpload[matchNumber]:
		FBC.updateFirebaseWithTIMD(timd)
	time.sleep(5)


