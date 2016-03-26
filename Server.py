# by Bryton Moeller (2015-2016)

import json
import sys

#Our Modules
import DataModel
import firebaseCommunicator
import Math
import unicodedata
import time
import DataValidator
import CSVExporter
import pdb
import scoutPerformance

shouldCacheJSONCopies = False

comp = DataModel.Competition()
comp.updateTeamsAndMatchesFromFirebase()
comp.updateTIMDsFromFirebase()

CSVExporter.TSVExportSAC(comp)
CSVExporter.TSVExportAll(comp)
CSVExporter.TSVExportMini(comp)
SPA = scoutPerformance.ScoutPerformance(comp)
SPA.analyzeScouts()
dv = DataValidator.DataValidator(comp)

FBC = firebaseCommunicator.FirebaseCommunicator(comp)
#FBC.wipeDatabase()
calculator = Math.Calculator(comp)

secsBetweenCalc = 0
shouldCacheSecsCounter = 0
cycle = 1

numHoursBetweenCaches = 1.0/360.0
print "s" + 2

while(cycle <= 1):
	print("\nCalcs Cycle " + str(cycle) + "...")
	if((shouldCacheSecsCounter / (numHoursBetweenCaches * 3600)) == 1):
		shouldCacheSecsCounter = 0
	if(shouldCacheSecsCounter == 0):
		FBC.cacheFirebase()
	shouldCacheSecsCounter += secsBetweenCalc
	dv.validateFirebase()
	comp.updateTeamsAndMatchesFromFirebase()
	comp.updateTIMDsFromFirebase()
	calculator.doCalculations(FBC)
	time.sleep(secsBetweenCalc)
	if len(calculator.getCompletedTIMDsInCompetition) == len(comp.timds): break 
	cycle += 1

elimsAlliances = []
for i in range(8):
	a, b, c = raw_input("Input team numbers for alliance " + str(i + 1)).split()
	elimsAlliances.append([a,b,c])



# # DEBUG
# teams = []
# for i in teams:
# 	updateFirebaseWithTeam(makeTeamObjectWithNumberAndName(i, "none"))
