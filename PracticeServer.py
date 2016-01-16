# by Bryton Moeller (2015-2016)

import json
import sys

#Our Modules
import DataModel
import utils
import firebaseCommunicator

#print(firebaseCommunicator.getPythonObjectForFirebaseDataAtLocation("/Matches"))
c = DataModel.Competition()
c.updateTIMDsFromFirebase()
print c.TIMDs


''' # DEBUG
teams = []
for i in teams:
	updateFirebaseWithTeam(makeTeamObjectWithNumberAndName(i, "none"))
'''