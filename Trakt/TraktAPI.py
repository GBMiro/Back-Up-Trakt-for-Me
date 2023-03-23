from Utils.Logger import Logger
import Utils.StatusCodes as StatusCodes
import requests
import time


class TraktAPI:

    baseURL = "https://api.trakt.tv"
    traktAPIVersion = '2'
    
    TRAKT_SYNC_LIMIT = 1000

    def __init__(self, showLog):
        self.logger = Logger(showLog, "TRAKT")

    def AuthorizeUser(self, clientID, clientSecret):

        authorizeHeader = {'Content-type': 'application/json'}

        postData = {"client_id" : clientID}
        try:
            response = requests.post(self.baseURL + '/oauth/device/code', json=postData, headers=authorizeHeader)

            if (response.status_code == StatusCodes.TRAKT_SUCCESS):
                authorizationData = response.json()
                message = "Go to {} in your browser and input the following code: {}".format(authorizationData['verification_url'], authorizationData['user_code'])
                self.logger.ShowMessage(message)

                tokenData = {
                    "code" : authorizationData['device_code'],
                    'client_id' : clientID,
                    'client_secret' : clientSecret
                }

                url = self.baseURL + '/oauth/device/token'
                tokenResponse = requests.post(url , json=tokenData, headers=authorizeHeader)

                pullTime = 0

                while (tokenResponse.status_code != StatusCodes.TRAKT_SUCCESS and pullTime < authorizationData['expires_in']) :
                    time.sleep(authorizationData['interval'])
                    pullTime += authorizationData['interval']
                    tokenResponse = requests.post(url, json=tokenData, headers=authorizeHeader)
                    message = "Response code: {}".format(tokenResponse.status_code)
                    self.logger.ShowMessage(message)

                if (tokenResponse.status_code != StatusCodes.TRAKT_SUCCESS) : 
                    message = "Could not authorize user. Code: {} {}".format(response.status_code, StatusCodes.statusMessages[response.status_code])
                    self.logger.ShowMessage(message)
                    return {'accessToken' : None, 'refresh_token' : None, 'code' : tokenResponse.status_code}
                else:
                    tokenData = tokenResponse.json()
                    return {'accessToken' : tokenData['access_token'], 'refresh_token' : tokenData['refresh_token'], 'code' : tokenResponse.status_code}
            else:
                message = "Could not authorize user. Code: {} {}".format(response.status_code, StatusCodes.statusMessages[response.status_code])
                self.logger.ShowMessage(message)
                return {'accessToken' : None, 'refresh_token' : None, 'code' : response.status_code}
            
        except requests.exceptions.RequestException as err:
            message = "An error occurred in requests module: {}".format(err)
            self.logger.ShowMessage(message)
            return {'accessToken' : None, 'refresh_token' : None, 'code' : StatusCodes.REQUESTS_ERROR}

        

    def GetHistory(self, clientID, accessToken):
        self.logger.ShowMessage("Downloading history...")
        header = self.__BuildRequiredHeader(clientID, accessToken)
        plays, statusCode = self.__GetURLWithPagination('/sync/history?extended=full&page={}&limit={}', header, "history")
        return plays, statusCode
        
    def GetRatings(self, type, clientID, accessToken):
        header = self.__BuildRequiredHeader(clientID, accessToken)
        self.logger.ShowMessage("Downloading {} ratings...".format(type))
        url = '/sync/ratings/{}'.format(type) + '?page={}&limit={}'
        ratings, statusCode = self.__GetURLWithPagination(url, header, "{} ratings".format(type))

        return ratings, statusCode

    def GetSyncLimit(self):
        return self.TRAKT_SYNC_LIMIT
        
    def __BuildRequiredHeader(self, clientID, accessToken):
        header = {
            'Content-type': 'application/json',
            'trakt-api-key': clientID,
            'trakt-api-version': self.traktAPIVersion,
            'Authorization': "Bearer " + accessToken
        }   
        return header
    
    def __GetURL(self, url, headers):
        response = None
        try:
            response = requests.get(self.baseURL + url, headers=headers)
            message = "Downloading {} ...".format(self.baseURL + url)
            statusCode = response.status_code
        except requests.exceptions.RequestException as err:
            message = "An error occurred in requests module: {}".format(err)
            statusCode = StatusCodes.REQUESTS_ERROR
        finally:
            self.logger.ShowMessage(message)
            return response, statusCode
        
    def __GetURLWithPagination(self, url, headers, type):
        page = 1
        data = []
        message = ''
        statusCode = StatusCodes.TRAKT_SUCCESS
        syncing = True

        while (syncing and statusCode == StatusCodes.TRAKT_SUCCESS):
            
            response, statusCode = self.__GetURL(str(url).format(page, self.TRAKT_SYNC_LIMIT), headers)
            
            if (statusCode == StatusCodes.TRAKT_SUCCESS):
                # Check if we have pages left to download
                syncing = False if (page >= int(response.headers['X-Pagination-Page-Count'])) else True
                responseData = response.json()
                data += responseData
                page += 1
            else:
                message = "Could not download {}. An error occurred: {} {}.".format(type, statusCode, StatusCodes.statusMessages[statusCode])

        if (statusCode == StatusCodes.TRAKT_SUCCESS):
            message = "{} downloaded".format(type)

        self.logger.ShowMessage(message)
        return data, statusCode