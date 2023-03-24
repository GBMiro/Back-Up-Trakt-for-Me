from Utils.Logger import Logger
import Utils.UI as UI
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
                self.logger.ShowMessage("Go to {} in your browser and input the following code: {}".format(authorizationData['verification_url'], authorizationData['user_code']))

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
                    self.logger.ShowMessage("Response code: {}".format(tokenResponse.status_code))

                if (tokenResponse.status_code != StatusCodes.TRAKT_SUCCESS) : 
                    self.logger.ShowMessage("Could not authorize user. Code: {} {}".format(response.status_code, StatusCodes.statusMessages[response.status_code]), UI.ERROR_LOG)
                    return {'accessToken' : None, 'refresh_token' : None, 'code' : tokenResponse.status_code}
                else:
                    tokenData = tokenResponse.json()
                    return {'accessToken' : tokenData['access_token'], 'refresh_token' : tokenData['refresh_token'], 'code' : tokenResponse.status_code}
            else:
                self.logger.ShowMessage("Could not authorize user. Code: {} {}".format(response.status_code, StatusCodes.statusMessages[response.status_code]), UI.ERROR_LOG)
                return {'accessToken' : None, 'refresh_token' : None, 'code' : response.status_code}
            
        except requests.exceptions.RequestException as err:
            self.logger.ShowMessage("An error occurred in requests module: {}".format(err), UI.ERROR_LOG)
            return {'accessToken' : None, 'refresh_token' : None, 'code' : StatusCodes.REQUESTS_ERROR}

        

    def GetHistory(self, clientID, accessToken):
        self.logger.ShowMessage("Downloading history...")
        header = self.__BuildRequiredHeader(clientID, accessToken)
        # This Trakt API call has optional pagination. Call __GetURLWithPagination
        plays, statusCode = self.__GetURLWithPagination('/sync/history?extended=full&page={}&limit={}', header, "history")
        return plays, statusCode
        
    def GetRatings(self, type, clientID, accessToken):
        header = self.__BuildRequiredHeader(clientID, accessToken)
        self.logger.ShowMessage("Downloading {} ratings...".format(type))
        url = '/sync/ratings/{}'.format(type) + '?page={}&limit={}'
        # This Trakt API call has optional pagination. Call __GetURLWithPagination
        ratings, statusCode = self.__GetURLWithPagination(url, header, "{} ratings".format(type))

        return ratings, statusCode

    def GetCollection(self, type, clientID, accessToken):
        header = self.__BuildRequiredHeader(clientID, accessToken)
        self.logger.ShowMessage("Downloading {} collection...".format(type))
        url = '/sync/collection/{}?extended=metadata'.format(type)
        # This trakt API call does not have pagination. Call __GetURLWithNoPagination directly
        collection, statusCode = self.__GetURLWithNoPagination(url, header, "{} collection".format(type))

        return collection, statusCode
    
    def GetWatched(self, type, clientID, accessToken):
        header = self.__BuildRequiredHeader(clientID, accessToken)
        self.logger.ShowMessage("Downloading watched {}...".format(type))
        url = '/sync/watched/{}'.format(type)
        # This trakt API call does not have pagination. Call __GetURLWithNoPagination directly
        watched, statusCode = self.__GetURLWithNoPagination(url, header, "{} watched".format(type))

        return watched, statusCode
    
    def GetWatchlist(self, type, clientID, accessToken):
        header = self.__BuildRequiredHeader(clientID, accessToken)
        self.logger.ShowMessage("Downloading {} watchlist...".format(type))
        url = '/sync/watchlist/{}'.format(type) + '?page={}&limit={}'
        # This Trakt API call has optional pagination. Call __GetURLWithPagination
        watchlist, statusCode = self.__GetURLWithPagination(url, header,"{} watchlist".format(type))

        return watchlist, statusCode

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
            self.logger.ShowMessage("Downloading {}...".format(self.baseURL + url))
            statusCode = response.status_code
        except requests.exceptions.RequestException as err:
            self.logger.ShowMessage("An error occurred in requests module: {}".format(err), UI.ERROR_LOG)
            statusCode = StatusCodes.REQUESTS_ERROR
        finally:
            return response, statusCode
        
    def __GetURLWithPagination(self, url, headers, type):
        page = 1
        data = []
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
                self.logger.ShowMessage("Could not download {}. An error occurred: {} {}.".format(type, statusCode, StatusCodes.statusMessages[statusCode]), UI.ERROR_LOG)

        if (statusCode == StatusCodes.TRAKT_SUCCESS):
            self.logger.ShowMessage("{} downloaded".format(type), UI.SUCCESS_LOG)

        return data, statusCode
    
    def __GetURLWithNoPagination(self, url, headers, type):
        response, statusCode = self.__GetURL(url, headers)
        data = []

        if (statusCode == StatusCodes.TRAKT_SUCCESS):
            data = response.json()
            self.logger.ShowMessage("{} downloaded".format(type), UI.SUCCESS_LOG)
        else:
            self.logger.ShowMessage("Could not download {}. An error occurred: {} {}.".format(type, statusCode, StatusCodes.statusMessages[statusCode]), UI.ERROR_LOG)

        return data, statusCode