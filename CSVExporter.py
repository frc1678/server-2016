# CSV Exporter, by Bryton 2/10/16
import utils


def TSVExportAll(comp):
	s = ""
	firstTeam = True
	with open('./dataExportAll.tsv', 'w') as file:
		for team in comp.teams:
			cd = team.calculatedData.__dict__
			if firstTeam:
				firstTeam = False
				s += "number" + "	"
				for key in cd.keys():
					s += key + "	"
				s += "\n"
			s += str(team.number) + "	"
			for value in cd.values():
				s += str(value) + "	"
			s += "\n"
		file.write(s)
		file.close()

def TSVExportCVR(comp):
	s = ""
	CVRKeys = ["RScoreDrivingAbility",	"disabledPercentage",	"numAutoPoints",	"sdLowShotsTele",	"sdHighShotsTele",	"actualSeed",	"incapacitatedPercentage",	"avgShotsBlocked",	"highShotAccuracyTele",	"sdShotsBlocked",	"siegeConsistency",	"disfunctionalPercentage",	"sdSiegeAbility",	"overallSecondPickAbility"]
	firstTeam = True
	with open('./dataExportCVR.tsv', 'w') as file:
		for team in comp.teams:
			cd = team.calculatedData.__dict__
			if firstTeam:
				firstTeam = False
				s += "number" + "	"
				for key in CVRKeys:
					s += key + "	"
				s += "\n"
			s += str(team.number) + "	"
			for key in CVRKeys:
				s += str(cd[key]) + "	"
			s += "\n"
		file.write(s)
		file.close()

def TSVExportMini(comp):
	s = ""
	MiniKeys = ["numAutoPoints", "actualSeed",	"siegeConsistency",	"disfunctionalPercentage", "avgDrivingAbility"]
	firstTeam = True
	with open('./dataExportMini.tsv', 'w') as file:
		for team in comp.teams:
			cd = team.calculatedData.__dict__
			if firstTeam:
				firstTeam = False
				s += "number" + "	"
				for key in MiniKeys:
					s += key + "	"
				s += "\n"
			s += str(team.number) + "	"
			for key in MiniKeys:
				s += str(cd[key]) + "	"
			s += "\n"
		file.write(s)
		file.close()