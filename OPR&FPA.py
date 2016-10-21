import requests 
import numpy as np
import firebase as fb
import matplotlib.pyplot as plt

(superSecret, url) = ('IMXOxXD3FjOOUoMGJlkAK5pAtn89mGIWAEnaKJhP', 'https://1678-strat-dev-2016.firebaseio.com/') 
basicURL = "http://www.thebluealliance.com/api/v2/"
headerKey = "X-TBA-App-Id"		
headerValue = "blm:OPRs:004"

auth = fb.FirebaseAuthentication(superSecret, "1678programming@gmail.com", True, True)

def zscore(lis, x):
	return (x - np.mean(lis)) / np.std(lis)

def oprFromZScore(lis, z):
	return (z * np.std(lis)) + np.mean(lis)

firebase = fb.FirebaseApplication(url, auth)
teams = map(lambda k: k.encode('utf-8'), firebase.get('/Teams', None).keys())
fpas = map(lambda k: np.log(firebase.get('/Teams/' + k + '/calculatedData', 'firstPickAbility')), teams)
o = requests.get(basicURL + "event/" + "2016casj" + "/stats" ,headers={headerKey:headerValue}).json()["oprs"]
oprs = map(lambda k: o[k], teams)
normalOPRs = map(lambda e: np.log10(e), oprs)
zscores = map(lambda a: zscore(fpas, a), fpas)
print zscores
zScoreToLogOPR = map(lambda a: oprFromZScore(normalOPRs, a), zscores)
fpaToOPR = map(lambda a: 10 ** a, zScoreToLogOPR)
print len(fpaToOPR), len(oprs)
print zip(oprs, fpaToOPR)
plt.hist(oprs, bins=10)
plt.hist(fpaToOPR, bins=12, alpha = 0.3)
plt.show()