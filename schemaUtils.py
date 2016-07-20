import DataModel
import pdb

class SchemaUtils(object):
    """docstring for SchemaUtils"""
    def __init__(self, comp):
        super(SchemaUtils, self).__init__()
        self.comp = comp
        
     # Team utility functions
    def getTeamForNumber(self, teamNumber):
        try: return [team for team in self.comp.teams if team.number == teamNumber][0]
        except: 
            print str(teamNumber) + " doesn't exist."
            return None

    def teamsWithCalculatedData(self):
        return filter(lambda t: self.teamCalculatedDataHasValues(t.calculatedData), self.comp.teams)

    def getCompletedMatchesForTeam(self,team):
        return filter(self.matchIsCompleted, team.matches)

    def findTeamsWithMatchesCompleted(self):
        return filter(lambda team: len(self.getCompletedMatchesForTeam(team)) > 0, self.comp.teams)

    def teamCalculatedDataHasValues(self, calculatedData):
        return calculatedData.siegeAbility != None

    def replaceWithAverageIfNecessary(self, team):
        return team if self.teamCalculatedDataHasValues(team.calculatedData) else averageTeam

    # Match utility functions
    def getMatchForNumber(self, matchNumber):
        return [match for match in self.comp.matches if match.number == matchNumber][0]

    def teamsInMatch(self, match):
        return match.redTeams + match.blueTeams

    def teamInMatch(self, team, match):
        return team in self.teamsInMatch(match)
        
    def matchIsCompleted(self, match):
        return len(self.getCompletedTIMDsForMatch(match)) == 6 and self.matchHasValuesSet(match)   

    def getCompletedMatchesInCompetition(self):
        return filter(self.matchIsCompleted, self.comp.matches)

    def teamsAreOnSameAllianceInMatch(self, team1, team2, match):
        return team2 in self.getAllianceForTeamInMatch(team1, match)

    def teamsForTeamNumbersOnAlliance(self, alliance):
        return map(self.getTeamForNumber, alliance)

    def getAllianceForMatch(self, match, allianceIsRed):
        return match.redTeams if allianceIsRed else match.blueTeams

    def getAllianceForTeamInMatch(self, team, match):
        return self.getAllianceForMatch(match, self.getTeamAllianceIsRedInMatch(team, match))

    def getFieldsForAllianceForMatch(self, allianceIsRed, match):
        return (match.redScore, match.redAllianceDidBreach, match.redAllianceDidCapture) if allianceIsRed else (
            match.blueScore, match.blueAllianceDidBreach, match.blueAllianceDidCapture)

    def getTeamAllianceIsRedInMatch(self, team, match):
        if team.number == -1 or team in match.redTeams: return True
        if team in match.blueTeams: return False
        else: 
            raise ValueError(str(team.number) not in "Q" + str(match.number))

    # TIMD utility function

    def getCompletedTIMDsForTeam(self, team):
        return filter(self.timdIsCompleted, team.timds)

    def getTIMDsForMatchForAllianceIsRed(self, match, allianceIsRed):
        return filter(lambda t: t.team in match.redTeams, match.timds) if allianceIsRed else filter(lambda t: t.team in match.blueTeams, match.timds) 

    def getCompletedTIMDsForMatchForAllianceIsRed(self, match, allianceIsRed):
        return filter(self.timdIsCompleted, self.getTIMDsForMatchForAllianceIsRed(match, allianceIsRed))

    def getCompletedTIMDsForTeam(self, team):
        return filter(self.timdIsCompleted, team.timds)

    def getCompletedTIMDsForMatch(self, match):
        return filter(self.timdIsCompleted, match.timds)

    def getTIMDForTeamAndMatch(self, team, match):
        return filter(lambda t: t.team == team and t.match == match, self.comp.TIMDs)

    def getCompletedTIMDsInCompetition(self):
        return filter(self.timdIsCompleted, self.comp.TIMDs)

    def TIMCalculatedDataHasValues(self, calculatedData):
        return calculatedData.drivingAbility != None 

    def timdIsCompleted(self, timd):
        return timd.rankTorque != None and timd.numHighShotsMadeTele != None 

    def matchHasValuesSet(self, match):
        return match.redScore != None and match.blueScore != None

    def retrieveCompletedTIMDsForTeam(self, team):
        return self.getCompletedTIMDsForTeam(team)

    def isSurrogate(self, team, match):
        timd = self.getTIMDForTeamNumberAndMatchNumber(team.number, match.number)
        return timd in surrogateTIMDs