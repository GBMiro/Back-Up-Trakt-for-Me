import requests
import time
import TraktAPI.APIStatusCodes as APIStatusCodes

class TraktAPI:

    baseURL = "https://api.trakt.tv"
    traktAPIVersion = '2'

    def __init__(self, clientID):
        self.traktConfig = {}
        self.headers = {
            'Content-type': 'application/json',
            'trakt-api-key': clientID,
            'trakt-api-version': self.traktAPIVersion
        }

    def authorizeUser(self, clientID, clientSecret):

        authorizeHeader = {'Content-type': 'application/json'}

        postData = {"client_id" : clientID}

        response = requests.post(self.baseURL + '/oauth/device/code', json=postData, headers=authorizeHeader)

        if (response.status_code == APIStatusCodes.SUCCESS):
            authorizationData = response.json()
            print ("Go to " + authorizationData['verification_url'] + " in your browser and input the following code: " + authorizationData['user_code'])

            tokenData = {
                "code" : authorizationData['device_code'],
                'client_id' : clientID,
                'client_secret' : clientSecret
            }

            url = self.baseURL + '/oauth/device/token'
            tokenResponse = requests.post(url , json=tokenData, headers=authorizeHeader)

            tryingToGetTokenTime = 0

            while (tokenResponse.status_code != APIStatusCodes.SUCCESS and tryingToGetTokenTime < authorizationData['expires_in']) :
                time.sleep(authorizationData['interval'])
                tryingToGetTokenTime += authorizationData['interval']
                tokenResponse = requests.post(url, json=tokenData, headers=authorizeHeader)
                print (tokenResponse.status_code)

            if (tokenResponse.status_code != APIStatusCodes.SUCCESS) : 
                return {'accessToken' : None, 'refresh_token' : None, 'code' : tokenResponse.status_code}
            else:
                tokenData = tokenResponse.json()
                return {'accessToken' : tokenData['access_token'], 'refresh_token' : tokenData['refresh_token'], 'code' : tokenResponse.status_code}

            
    def getHistory(self):
        self.headers['Authorization'] = "Bearer " + self.traktConfig['accessToken']
        response = requests.get(self.baseURL + '/sync/history/?page=1&limit=10000', headers=self.headers)

        if response.status_code == APIStatusCodes.SUCCESS :
            data = response.json()
            return data, response.status_code
        else:
            return None, response.status_code