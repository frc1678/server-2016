import requests
import numpy as np
import firebase as fb
import Math

(superSecret, url) = ('lGufYCifprPw8p1fiVOs7rqYV3fswHHr9YLwiUWh', 'https://1678-extreme-testing.firebaseio.com/') 


auth = fb.FirebaseAuthentication(superSecret, "1678programming@gmail.com", True, True)

firebase = fb.FirebaseApplication(url, auth)
print firebase.get('/Teams', None).keys()