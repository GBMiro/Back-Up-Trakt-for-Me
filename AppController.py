from TraktAPI.TraktAPI import TraktAPI
import TraktAPI.APIStatusCodes as APIStatusCodes
import json


class AppController():
    
    def __init__(self):
        self.traktConfig = self.__loadTraktConfig()
        self.trakt = TraktAPI(self.traktConfig['clientID'])
    
    def backupWatchedHistory(self):
        print ("")

    def authorizeTraktUser(self):
        if not self.__traktUserAuthorized():
            result = self.trakt.authorizeUser(self.traktConfig['clientID'], self.traktConfig['clientSecret'])
            if (result['code'] == APIStatusCodes.SUCCESS):
                self.traktConfig['accessToken'] = result['accessToken']
                self.traktConfig['refreshToken'] = result['refreshToken']
                self.__saveConfig()
            return result['code']
        return APIStatusCodes.SUCCESS

    def __traktUserAuthorized(self):
        if (self.traktConfig['accessToken'] != ''):
            return True
        else:
            return False

    def __loadTraktConfig(self):
        with open('settings.json', 'r') as configFile:
            data = json.load(configFile)
            traktConfig = {
                'clientID' : data['clientID'],
                'clientSecret' : data['clientSecret'],
                'accessToken' : data['accessToken'],
                'refreshToken' : data['refreshToken']
            }

        return traktConfig

    def __saveConfig(self):
        with open('settings.json', 'w') as configFile:
            json.dump(self.traktConfig, configFile)