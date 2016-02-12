# CSV Exporter, by Bryton 2/10/16
import utils

def TSVExport(comp):
	s = ""
	firstTeam = True
	with open('./dataExport.tsv', 'w') as file:
		for team in comp.teams:
			cd = team.calculatedData.__dict__
			if firstTeam:
				firstTeam = False
				for key in cd.keys():
					s += key + "	"
				s += "\n"
			for value in cd.values():
				s += str(value) + "	"
			s += "\n"
		file.write(s)
		file.close()
