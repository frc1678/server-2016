import firebaseCommunicator
import json
import utils
import DataModel
import time

comp = DataModel.Competition()
comp.updateTeamsAndMatchesFromFirebase()

matches = comp.matches

FBC = firebaseCommunicator.FirebaseCommunicator(comp)

dataFileName = raw_input('Input file name: ')
with open(dataFileName, 'r') as dataFile:
	jsonData = json.loads(dataFile.read())

timdsToUpload = {}
for match in matches:
	if match != None:
		timdsToUpload[match.number] = []

timdObjects = utils.makeTIMDsFromDicts(jsonData['TeamInMatchDatas'])
for timd in timdObjects:
	timdsToUpload[timd.matchNumber].append(timd)

for match in matches:
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
	time.sleep(5)


