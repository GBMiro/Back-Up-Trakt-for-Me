from Trakt.TraktAPI import TraktAPI
from Database.DatabaseManager import DatabaseManager
from Utils.Logger import Logger
import Utils.Database as DB
import Utils.UI as UI
import Utils.StatusCodes as StatusCodes
import json


class AppController():
    
    def __init__(self, showLog=True):
        self.logger = Logger(showLog, "CONTROLLER")
        self.database = DatabaseManager(showLog)
        self.traktConfig = self.__LoadConfig()
        self.trakt = TraktAPI(showLog)


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
            message = "User is not authorized (missing trakt settings). Error: {} {}".format(StatusCodes.TRAKT_UNAUTHORIZED, StatusCodes.statusMessages[StatusCodes.TRAKT_UNAUTHORIZED])
            self.logger.ShowMessage(message)
            return StatusCodes.TRAKT_UNAUTHORIZED
        
        self.logger.ShowMessage("Starting backup process...")
        page = 1
        syncing = True
        statusCode = StatusCodes.CONTROLLER_OK
        totalPlays = 0
        self.database.OpenDatabase()
        while (syncing and statusCode == StatusCodes.CONTROLLER_OK):
            statusCode, data = self.trakt.GetHistoryPage(page, self.traktConfig['clientID'], self.traktConfig['accessToken'])
            if (statusCode == StatusCodes.TRAKT_SUCCESS):
                message = "Processing plays from page {}".format(page)
                self.logger.ShowMessage(message)
                syncing, statusCode = self.__ProcessTraktPlays(data)
                
                if (statusCode == StatusCodes.CONTROLLER_OK):
                    totalPlays += len(data)
                    page += 1
        
        self.database.CloseDatabase()
        if (statusCode != StatusCodes.CONTROLLER_OK):
            message = "Backup history finished with an error. Pages processed: {}. Plays stored: {}. Check previous logs for more info".format(page - 1, totalPlays)
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
        self.logger.ShowMessage("Querying database for {} plays...".format(sender))
        plays = []

        if (sender == UI.SHOW_HISTORY):
            plays, statusCode = self.database.GetHistory()
        elif (sender == UI.SHOW_EPISODES):
            plays, statusCode = self.database.GetEpisodes()
        else:
            plays, statusCode = self.database.GetMovies()

        if (statusCode != StatusCodes.DATABASE_OK):
            self.logger.ShowMessage("Request finished with an error. Check previous logs")
        else:
            statusCode = StatusCodes.CONTROLLER_OK

        return plays, statusCode
    
    def __ProcessTraktPlays(self, plays):

        statusCode = None

        for play in plays:
            statusCode = self.database.AddPlay(play)
            if (statusCode != StatusCodes.DATABASE_OK):
                return False, statusCode

        syncing = True if len(plays) == self.trakt.GetSyncLimit() else False

        return syncing, StatusCodes.CONTROLLER_OK

    def __TraktUserAuthorized(self):
        if (len(self.traktConfig['accessToken']) == 64):
            return True
        else:
            return False
        
    def __LoadConfig(self):
        data, statusCode = self.database.GetTraktSettings()

        traktConfig = {'clientID' : "", 'clientSecret' : "", 'accessToken' : "", 'refreshToken' : ""}

        if (statusCode == StatusCodes.DATABASE_OK):
            if (len(data) != 0):
                traktConfig = {
                    'clientID' : data[0][DB.CLIENT_ID_COLUMN],
                    'clientSecret' : data[0][DB.CLIENT_SECRET_COLUMN],
                    'accessToken' : data[0][DB.ACCESS_TOKEN_COLUMN],
                    'refreshToken' : data[0][DB.REFRESH_TOKEN_COLUMN]
                }
                message = "Trakt settings loaded from database"
            else:
                message = "No trakt settings found"
        else:
            message = "An error occurred when loading trakt settings. Check previous logs"
        
        self.logger.ShowMessage(message)

        return traktConfig

    def __SaveConfig(self):
        statusCode = self.database.SaveTraktSettings(self.traktConfig['clientID'], self.traktConfig['clientSecret'], self.traktConfig['accessToken'], self.traktConfig['refreshToken'])
        if (statusCode == StatusCodes.DATABASE_OK):
            message = "Settings saved to database"
        else:
            message = "Could not save settings to database. Check previous logs"

        self.logger.ShowMessage(message)