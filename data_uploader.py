import firebaseCommunicator
import json
import utils
import DataModel
import time

comp = DataModel.Competition()
comp.updateTeamsAndMatchesFromFirebase()

matches = comp.matches

FBC = firebaseCommunicator.FirebaseCommunicator(comp)

startNumber = 0

dataFileName = raw_input('Input file name: ')
with open(dataFileName, 'r') as dataFile:
	jsonData = json.loads(dataFile.read())

matches = [m for m in matches if m.number >= startNumber]


timdsToUpload = {}
for match in matches:
	if match != None:
		timdsToUpload[match.number] = []
timdsToUpload[83] = []

timdObjects = utils.makeTIMDsFromDicts(jsonData['TeamInMatchDatas'])
timdObjects = [t for t in timdObjects if t.matchNumber >= startNumber]
for timd in timdObjects:
	if timd.matchNumber < 82:
		timdsToUpload[timd.matchNumber].append(timd)

for match in matches:
	if match.number < 82:
		# if match['number'] != 83:
		actualJsonMatches = [m for m in jsonData['Matches'] if m != None]
		jsonMatch = [m for m in actualJsonMatches if m['number'] == match.number][0]
		match.redAllianceTeamNumbers = [str(r) for r in match.redAllianceTeamNumbers]
		match.blueAllianceTeamNumbers = [str(b) for b in match.blueAllianceTeamNumbers]
		match.redAllianceDidBreach = jsonMatch['redAllianceDidBreach']
		match.blueAllianceDidBreach = jsonMatch['blueAllianceDidBreach']
		match.redAllianceDidCapture = jsonMatch['redAllianceDidCapture']
		match.blueAllianceDidCapture = jsonMatch['blueAllianceDidCapture']
		match.redScore = jsonMatch['redScore']
		match.blueScore = jsonMatch['blueScore']
		FBC.updateFirebaseWithMatch(match)
		for timd in timdsToUpload[match.number]:
			print 'Uploading Q' + str(timd.matchNumber) + ' for team ' + str(timd.teamNumber)
			FBC.updateFirebaseWithTIMD(timd)
		time.sleep(20)


