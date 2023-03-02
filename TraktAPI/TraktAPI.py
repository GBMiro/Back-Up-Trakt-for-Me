import requests
import time
import TraktAPI.TraktAPIUtils as TraktAPIUtils

class TraktAPI:

    baseURL = "https://api.trakt.tv"
    traktAPIVersion = '2'

    def __init__(self, clientID):
        self.headers = {
            'Content-type': 'application/json',
            'trakt-api-key': clientID,
            'trakt-api-version': self.traktAPIVersion
        }

    def AuthorizeUser(self, clientID, clientSecret):

        authorizeHeader = {'Content-type': 'application/json'}

        postData = {"client_id" : clientID}

        response = requests.post(self.baseURL + '/oauth/device/code', json=postData, headers=authorizeHeader)

        if (response.status_code == TraktAPIUtils.SUCCESS):
            authorizationData = response.json()
            print ("Go to " + authorizationData['verification_url'] + " in your browser and input the following code: " + authorizationData['user_code'])

            tokenData = {
                "code" : authorizationData['device_code'],
                'client_id' : clientID,
                'client_secret' : clientSecret
            }

            url = self.baseURL + '/oauth/device/token'
            tokenResponse = requests.post(url , json=tokenData, headers=authorizeHeader)

            pullTime = 0

            while (tokenResponse.status_code != TraktAPIUtils.SUCCESS and pullTime < authorizationData['expires_in']) :
                time.sleep(authorizationData['interval'])
                pullTime += authorizationData['interval']
                tokenResponse = requests.post(url, json=tokenData, headers=authorizeHeader)
                print (tokenResponse.status_code)

            if (tokenResponse.status_code != TraktAPIUtils.SUCCESS) : 
                return {'accessToken' : None, 'refresh_token' : None, 'code' : tokenResponse.status_code}
            else:
                tokenData = tokenResponse.json()
                return {'accessToken' : tokenData['access_token'], 'refresh_token' : tokenData['refresh_token'], 'code' : tokenResponse.status_code}
   
    def GetHistoryPage(self, page, accessToken):
        
        historyHeader = self.headers
        historyHeader['Authorization'] = "Bearer " + accessToken

        response = requests.get(self.baseURL + '/sync/history?extended=full&page={}&limit={}'.format(page, TraktAPIUtils.SYNC_MAX_LIMIT), headers=historyHeader)

        if response.status_code == TraktAPIUtils.SUCCESS :
            return response.status_code, response.json()
        else:
            return response.status_code, None