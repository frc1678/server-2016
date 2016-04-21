# by Bryton Moeller (2015-2016)

import json
import sys
import traceback

#Our Modules
import DataModel
import firebaseCommunicator
import Math
import unicodedata
import time
import DataValidator
import CSVExporter
import utils
import pdb
import scoutPerformance
import CrashReporter

shouldCacheJSONCopies = False

comp = DataModel.Competition()
comp.updateTeamsAndMatchesFromFirebase()
comp.updateTIMDsFromFirebase()


dv = DataValidator.DataValidator(comp)

FBC = firebaseCommunicator.FirebaseCommunicator(comp)
#FBC.wipeDatabase()
calculator = Math.Calculator(comp)
calculator.adjustSchedule()
secsBetweenCalc = 0
shouldCacheSecsCounter = 0
cycle = 1
shouldEmail = False

numHoursBetweenCaches = 1.0/360.0
emailer = CrashReporter.EmailThread()

while(True):
	print("\nCalcs Cycle " + str(cycle) + "...")
	CSVExporter.TSVExportCMP(comp)

	if((shouldCacheSecsCounter / (numHoursBetweenCaches * 3600)) == 1):
		shouldCacheSecsCounter = 0
	if(shouldCacheSecsCounter == 0):
		FBC.cacheFirebase()
	shouldCacheSecsCounter += secsBetweenCalc
	dv.validateFirebase()
	comp.updateTeamsAndMatchesFromFirebase()
	comp.updateTIMDsFromFirebase()
	if shouldEmail:
		try:
			calculator.doCalculations(FBC)
		except:
			emailer.reportServerCrash(traceback.format_exc())
			sys.exit(0)
	else: 
		calculator.doCalculations(FBC)
	time.sleep(secsBetweenCalc)
	cycle += 1

# elimsAlliances, i = {}, 1
# while i <= 8:
# 	a,b,c = raw_input("Input team numbers for alliance " + str(i) + ": ").split()
# 	if all(x in map(lambda x: x.number, comp.teams) for x in [int(a), int(b), int(c)]): 
# 		elimsAlliances[i] = [int(a),int(b),int(c)]
# 		i += 1

# FBC.addElimsAlliances(elimsAlliances)


# # DEBUG
# teams = []
# for i in teams:
# 	updateFirebaseWithTeam(makeTeamObjectWithNumberAndName(i, "none"))
