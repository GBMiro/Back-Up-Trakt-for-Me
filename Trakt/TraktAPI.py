from Utils.Logger import Logger
import Utils.Trakt as Trakt
import requests
import time


class TraktAPI:

    baseURL = "https://api.trakt.tv"
    traktAPIVersion = '2'

    def __init__(self, showLog, clientID):
        self.headers = {
            'Content-type': 'application/json',
            'trakt-api-key': clientID,
            'trakt-api-version': self.traktAPIVersion
        }
        self.logger = Logger(showLog, "TRAKT")

    def AuthorizeUser(self, clientID, clientSecret):

        authorizeHeader = {'Content-type': 'application/json'}

        postData = {"client_id" : clientID}

        response = requests.post(self.baseURL + '/oauth/device/code', json=postData, headers=authorizeHeader)

        if (response.status_code == Trakt.SUCCESS):
            authorizationData = response.json()
            message = "Go to " + authorizationData['verification_url'] + " in your browser and input the following code: " + authorizationData['user_code']
            self.logger.ShowMessage(message)

            tokenData = {
                "code" : authorizationData['device_code'],
                'client_id' : clientID,
                'client_secret' : clientSecret
            }

            url = self.baseURL + '/oauth/device/token'
            tokenResponse = requests.post(url , json=tokenData, headers=authorizeHeader)

            pullTime = 0

            while (tokenResponse.status_code != Trakt.SUCCESS and pullTime < authorizationData['expires_in']) :
                time.sleep(authorizationData['interval'])
                pullTime += authorizationData['interval']
                tokenResponse = requests.post(url, json=tokenData, headers=authorizeHeader)
                message = tokenResponse.status_code
                self.logger.ShowMessage(message)

            if (tokenResponse.status_code != Trakt.SUCCESS) : 
                message = "Could not authoriz user. Code: " + response.status_code + " " + Trakt.statusMessages[response.status_code]
                self.logger.ShowMessage(message)
                return {'accessToken' : None, 'refresh_token' : None, 'code' : tokenResponse.status_code}
            else:
                tokenData = tokenResponse.json()
                return {'accessToken' : tokenData['access_token'], 'refresh_token' : tokenData['refresh_token'], 'code' : tokenResponse.status_code}
   
    def GetHistoryPage(self, page, accessToken):

        message = "Requesting history page " + str(page)
        self.logger.ShowMessage(message)
        
        historyHeader = self.headers
        historyHeader['Authorization'] = "Bearer " + accessToken

        response = requests.get(self.baseURL + '/sync/history?extended=full&page={}&limit={}'.format(page, Trakt.SYNC_MAX_LIMIT), headers=historyHeader)

        if response.status_code == Trakt.SUCCESS :
            return response.status_code, response.json()
        else:
            message = "Could not download page. Code: " + response.status_code + " " + Trakt.statusMessages[response.status_code]
            self.logger.ShowMessage(message)
            return response.status_code, None