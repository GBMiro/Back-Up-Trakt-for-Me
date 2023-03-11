from Trakt.TraktAPI import TraktAPI
from Database.DatabaseManager import DatabaseManager
from Utils.Logger import Logger
import Utils.Trakt as Trakt
import json


class AppController():
    
    def __init__(self, showLog=True):
        self.logger = Logger(showLog, "CONTROLLER")
        self.traktConfig = self.__LoadTraktConfig()
        self.trakt = TraktAPI(showLog, self.traktConfig['clientID'])
        self.database = DatabaseManager(showLog)


    def AuthorizeTraktUser(self):
        if not self.__TraktUserAuthorized():
            result = self.trakt.AuthorizeUser(self.traktConfig['clientID'], self.traktConfig['clientSecret'])
            if (result['code'] == Trakt.SUCCESS):
                self.traktConfig['accessToken'] = result['accessToken']
                self.traktConfig['refreshToken'] = result['refreshToken']
                self.__SaveConfig()
            return result['code']
        return Trakt.SUCCESS
    
    def BackupWatchedHistory(self):
        page = 1
        syncing = True
        statusCode = Trakt.SUCCESS
        self.database.OpenDatabase()
        while (syncing and statusCode == Trakt.SUCCESS):
            statusCode, data = self.trakt.GetHistoryPage(page, self.traktConfig['accessToken'])
            if (statusCode == Trakt.SUCCESS):
                syncing, statusCode = self.__ProcessTraktPlays(data)
            page += 1
        
        self.database.CloseDatabase()
        message = "Process finished. Code result: " + str(statusCode) + " " + Trakt.statusMessages[statusCode]
        self.logger.ShowMessage(message)

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

        syncing = True if len(plays) == Trakt.SYNC_MAX_LIMIT else False

        return syncing, Trakt.SUCCESS

    def __TraktUserAuthorized(self):
        if (self.traktConfig['accessToken'] != ''):
            message = "User already authorized"
            self.logger.ShowMessage(message)
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

            message = "Trakt config loaded"
            self.logger.ShowMessage(message)

        return traktConfig

    def __SaveConfig(self):
        with open('settings.json', 'w') as configFile:
            json.dump(self.traktConfig, configFile)

        message = "Trakt config saved"
        self.logger.ShowMessage(message)