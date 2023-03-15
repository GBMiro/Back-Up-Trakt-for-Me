from Trakt.TraktAPI import TraktAPI
from Database.DatabaseManager import DatabaseManager
from Utils.Logger import Logger
import Utils.UI as UI
import Utils.StatusCodes as StatusCodes
import json


class AppController():
    
    def __init__(self, showLog=True):
        self.logger = Logger(showLog, "CONTROLLER")
        self.traktConfig = self.__LoadTraktConfig()
        self.trakt = TraktAPI(showLog)
        self.database = DatabaseManager(showLog)


    def AuthorizeTraktUser(self):
        if not self.__TraktUserAuthorized():
            result = self.trakt.AuthorizeUser(self.traktConfig['clientID'], self.traktConfig['clientSecret'])
            if (result['code'] == StatusCodes.TRAKT_SUCCESS):
                self.traktConfig['accessToken'] = result['accessToken']
                self.traktConfig['refreshToken'] = result['refreshToken']
                self.__SaveConfig()
            return result['code']
        else:
            message = "User already authorized"
            self.logger.ShowMessage(message)

        return StatusCodes.TRAKT_SUCCESS
    
    def BackupWatchedHistory(self):
        if (not self.__TraktUserAuthorized()):
            message = "User is not authorized (missing access token). Error: {} {}".format(StatusCodes.TRAKT_UNAUTHORIZED, StatusCodes.statusMessages[StatusCodes.TRAKT_UNAUTHORIZED])
            self.logger.ShowMessage(message)
            return StatusCodes.TRAKT_UNAUTHORIZED
        
        page = 1
        syncing = True
        statusCode = StatusCodes.TRAKT_SUCCESS
        totalPlays = 0
        self.database.OpenDatabase()
        while (syncing and statusCode == StatusCodes.TRAKT_SUCCESS):
            statusCode, data = self.trakt.GetHistoryPage(page, self.traktConfig['clientID'], self.traktConfig['accessToken'])
            if (statusCode == StatusCodes.TRAKT_SUCCESS):
                message = "Processing plays from page {}".format(page)
                self.logger.ShowMessage(message)
                syncing, statusCode = self.__ProcessTraktPlays(data)
                totalPlays += len(data)
                page += 1
        
        self.database.CloseDatabase()
        if (statusCode != StatusCodes.TRAKT_SUCCESS):
            message = "Backup history finished with an error. {} pages were processed. Check previous logs for more info".format(page - 1)
        else:
            message = "Backup history finished. Pages processed: {}. Total plays found: {}".format(page - 1, totalPlays)
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
    
    def SetTraktConfig(self, id, secret):
        self.traktConfig['clientID'] = id
        self.traktConfig['clientSecret'] = secret
        self.__SaveConfig()

    def GetHistoryData(self, sender):
        self.database.OpenDatabase()
        plays = []
        message = "Getting {} plays from database".format(sender)
        if (sender == UI.SHOW_HISTORY):
            plays = self.database.GetHistory()
        elif (sender == UI.SHOW_EPISODES):
            plays = self.database.GetEpisodes()
        else:
            plays = self.database.GetMovies()
        self.database.CloseDatabase()
        self.logger.ShowMessage(message)
        return plays
    
    def __ProcessTraktPlays(self, plays):

        for play in plays:
            self.database.AddPlay(play)

        syncing = True if len(plays) == self.trakt.GetSyncLimit() else False

        return syncing, StatusCodes.TRAKT_SUCCESS

    def __TraktUserAuthorized(self):
        if (len(self.traktConfig['accessToken']) == 64):
            return True
        else:
            return False

    def __LoadTraktConfig(self):
        try:
            with open('settings.json', 'r') as configFile:
                data = json.load(configFile)
                traktConfig = {
                    'clientID' : data['clientID'],
                    'clientSecret' : data['clientSecret'],
                    'accessToken' : data['accessToken'],
                    'refreshToken' : data['refreshToken']
                }
            message = "Trakt config loaded"
        except Exception as err:
            message = "An error occurred when loading the settings file. {}".format(err)
            traktConfig = {'clientID' : "", 'clientSecret' : "", 'accessToken' : "", 'refreshToken' : ""}
        finally:
            self.logger.ShowMessage(message)
            return traktConfig

    def __SaveConfig(self):
        try:
            with open('settings.json', 'w') as configFile:
                json.dump(self.traktConfig, configFile)
            message = "Trakt config saved"
        except Exception as err:
            message = "An error occurred when saving the settings file. {}".format(err)
        finally:
            self.logger.ShowMessage(message)