from TraktAPI.TraktAPI import TraktAPI
import TraktAPI.TraktAPIUtils as TraktAPIUtils
import json


class AppController():
    
    def __init__(self):
        self.traktConfig = self.__loadTraktConfig()
        self.trakt = TraktAPI(self.traktConfig['clientID'])
    
    def backupWatchedHistory(self):
        self.trakt.getHistory(self.traktConfig['accessToken'])

    def authorizeTraktUser(self):
        if not self.__traktUserAuthorized():
            result = self.trakt.authorizeUser(self.traktConfig['clientID'], self.traktConfig['clientSecret'])
            if (result['code'] == TraktAPIUtils.SUCCESS):
                self.traktConfig['accessToken'] = result['accessToken']
                self.traktConfig['refreshToken'] = result['refreshToken']
                self.__saveConfig()
            return result['code']
        return TraktAPIUtils.SUCCESS

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