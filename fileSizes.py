import os
import utils
import json
from firebase import firebase as fb

(superSecret, url) = ('qVIARBnAD93iykeZSGG8mWOwGegminXUUGF2q0ee', 'https://1678-scouting-2016.firebaseio.com/')
# (superSecret, url) = ('j1r2wo3RUPMeUZosxwvVSFEFVcrXuuMAGjk6uPOc', 'https://1678-dev-2016.firebaseio.com/')
#(superSecret, url) = ('hL8fStivTbHUXM8A0KXBYPg2cMsl80EcD7vgwJ1u', 'https://1678-dev2-2016.firebaseio.com/')
#(superSecret, url) = ('AEduO6VFlZKD4v10eW81u9j3ZNopr5h2R32SPpeq', 'https://1678-dev3-2016.firebaseio.com/')
#(superSecret, url) = ('IMXOxXD3FjOOUoMGJlkAK5pAtn89mGIWAEnaKJhP', 'https://1678-strat-dev-2016.firebaseio.com/')
# (superSecret, url) = ('lGufYCifprPw8p1fiVOs7rqYV3fswHHr9YLwiUWh', 'https://1678-extreme-testing.firebaseio.com/') 


auth = fb.FirebaseAuthentication(superSecret, "1678programming@gmail.com", True, True)

firebase = fb.FirebaseApplication(url, auth)
j = utils.readJSONFromString(json.dumps(firebase.get("/Matches", None)))
k = utils.readJSONFromString(json.dumps(firebase.get("/TeamInMatchDatas", None)))
l = utils.readJSONFromString(json.dumps(firebase.get("/Teams", None)))

