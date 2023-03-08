from TraktAPI.TraktAPI import TraktAPI
from Database.DatabaseManager import DatabaseManager
import TraktAPI.TraktAPIUtils as TraktAPIUtils
import json


class AppController():
    
    def __init__(self):
        self.traktConfig = self.__LoadTraktConfig()
        self.trakt = TraktAPI(self.traktConfig['clientID'])
        self.database = DatabaseManager()


    def AuthorizeTraktUser(self):
        if not self.__TraktUserAuthorized():
            result = self.trakt.AuthorizeUser(self.traktConfig['clientID'], self.traktConfig['clientSecret'])
            if (result['code'] == TraktAPIUtils.SUCCESS):
                self.traktConfig['accessToken'] = result['accessToken']
                self.traktConfig['refreshToken'] = result['refreshToken']
                self.__SaveConfig()
            return result['code']
        return TraktAPIUtils.SUCCESS
    
    def BackupWatchedHistory(self):
        page = 1
        syncing = True
        statusCode = TraktAPIUtils.SUCCESS
        while (syncing and statusCode == TraktAPIUtils.SUCCESS):
            statusCode, data = self.trakt.GetHistoryPage(page, self.traktConfig['accessToken'])
            if (statusCode == TraktAPIUtils.SUCCESS):
                syncing, statusCode = self.__ProcessTraktPlays(data)
            page += 1
        
        self.database.CloseDatabase()
        return statusCode
    
    def GetAccessToken(self):
        return self.traktConfig['accessToken']
    
    def GetRefreshToken(self):
        return self.traktConfig['refreshToken']
    
    def GetClientID(self):
        return self.traktConfig['clientID']
    
    def GetClientSecret(self):
        return self.traktConfig['clientSecret']
    
    def SaveTraktConfig(self):
        self.__SaveConfig()
    
    def __ProcessTraktPlays(self, plays):

        for play in plays:
            self.database.AddPlay(play)
            print(str(play['id']) + " " + str(play['type']) + " " + str(play['watched_at']))

        syncing = True if len(plays) == TraktAPIUtils.SYNC_MAX_LIMIT else False

        return syncing, TraktAPIUtils.SUCCESS

    def __TraktUserAuthorized(self):
        if (self.traktConfig['accessToken'] != ''):
            return True
        else:
            return False

    def __LoadTraktConfig(self):
        with open('settings.json', 'r') as configFile:
            data = json.load(configFile)
            traktConfig = {
                'clientID' : data['clientID'],
                'clientSecret' : data['clientSecret'],
                'accessToken' : data['accessToken'],
                'refreshToken' : data['refreshToken']
            }

        return traktConfig

    def __SaveConfig(self):
        with open('settings.json', 'w') as configFile:
            json.dump(self.traktConfig, configFile)