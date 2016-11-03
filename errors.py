from firebaseCommunicator import FirebaseCommunicator
import DataModel
from TBACommunicator import TBACommunicator
from schemaUtils import SchemaUtils
from Math import Calculator

comp = DataModel.Competition()
comp.updateTeamsAndMatchesFromFirebase()
comp.updateTIMDsFromFirebase()
fb = FirebaseCommunicator(comp)
su = SchemaUtils(comp)
calc = Calculator(comp)
err = 0
tbac = TBACommunicator()
currentMatch = 1
while currentMatch < len(comp.matches) - 1: 
	comp.updateTeamsAndMatchesFromFirebase()
	comp.updateTIMDsFromFirebase()
	if len(su.findTeamsWithMatchesCompleted()) == len(comp.teams):
		m = comp.matches[currentMatch + 1]
		pr = m.calculatedData.predictedRedScore
		ar = tbac.makeSingleMatchRequest(m.number)['alliances']["red"]["score"]
		pb = m.calculatedData.predictedBlueScore
		ab = tbac.makeSingleMatchRequest(m.number)['alliances']["blue"]["score"]
		print abs(pr-ar)
		err += (abs(pr - ar)) + (abs(pb - ab))
		currentMatch += 1

print err

