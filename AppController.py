from Trakt.TraktAPI import TraktAPI
from Database.DatabaseManager import DatabaseManager
from Utils.Logger import Logger
import Utils.Database as DB
import Utils.UI as UI
import Utils.StatusCodes as StatusCodes
from datetime import datetime
from dateutil import tz
import json

formatFrom="%Y-%m-%dT%H:%M:%S.000Z"
formatTo="%Y-%m-%d %H:%M:%S"

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
        playsFound = 0
        playsProcessed = 0
        self.database.OpenDatabase()
        while (syncing and statusCode == StatusCodes.CONTROLLER_OK):
            data, statusCode, syncing = self.trakt.GetHistoryPage(page, self.traktConfig['clientID'], self.traktConfig['accessToken'])
            if (statusCode == StatusCodes.TRAKT_SUCCESS):
                message = "Processing plays from page {}".format(page)
                self.logger.ShowMessage(message)
                processed = self.__ProcessTraktPlays(data)
                playsProcessed += processed
                playsFound += len(data)
                page += 1
                statusCode = StatusCodes.CONTROLLER_OK
        
        self.database.CloseDatabase()
        if (statusCode != StatusCodes.CONTROLLER_OK or playsProcessed != playsFound):
            message = "Backup history finished with errors. Pages processed: {}. Plays found: {} Plays successfully stored: {}. Check previous logs for more info".format(page - 1, playsFound, playsProcessed)
        else:
            message = "Backup history finished. Pages processed: {}. Plays found: {} Plays successfully stored: {}".format(page - 1, playsFound, playsProcessed)
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

        episodes = []
        movies = []

        for play in plays:
            playID = play['id']
            type = play['type']
            watchedAt = play['watched_at']
            watchedAtLocal = self.__ConvertToLocalTime(watchedAt)

            if (type == 'episode'):
                season = play['episode']['season']
                number = play['episode']['number']
                episodeTitle = play['episode']['title']
                runtime = play['episode']['runtime']
                episodeIDs = play['episode']['ids']
                showTitle = play['show']['title']
                showYear = play['show']['year']
                showIDs = play['show']['ids']

                # Order matches the episodes table columns
                episodes.append([playID, watchedAt, watchedAtLocal, type, season, number, episodeTitle,
                                json.dumps(episodeIDs), runtime, showTitle, showYear, json.dumps(showIDs)])
            else:
                title = play['movie']['title']
                year = play['movie']['year']
                runtime = play['movie']['runtime']
                movieIDs = play['movie']['ids']

                # Order matches movies table columns
                movies.append([playID, watchedAt, watchedAtLocal, type, title, year, runtime, json.dumps(movieIDs)])
        
        totalInserted = 0
        self.logger.ShowMessage("Processing episodes...")
        totalInserted += self.database.AddPlays(episodes, 'episode')
        self.logger.ShowMessage("Processing movies...")
        totalInserted += self.database.AddPlays(movies, 'movie')

        return totalInserted
    
    def __ConvertToLocalTime(self, watchedAt):
        watchedAt = datetime.strptime(watchedAt, formatFrom)
        watchedAt = watchedAt.replace(tzinfo=tz.tzutc())
        watchedAt = watchedAt.astimezone(tz.tzlocal()).strftime(formatTo)
        return watchedAt

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