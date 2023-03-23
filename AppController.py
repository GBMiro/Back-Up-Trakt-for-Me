from Trakt.TraktAPI import TraktAPI
from Database.DatabaseManager import DatabaseManager
from Exporter.ExporterJSON import ExporterJSON
from Utils.Logger import Logger
import Utils.Exporting as Folders
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
        self.exporter = ExporterJSON(showLog)


    def AuthorizeTraktUser(self):
        if not self.__TraktUserAuthorized():
            result = self.trakt.AuthorizeUser(self.traktConfig['clientID'], self.traktConfig['clientSecret'])
            if (result['code'] == StatusCodes.TRAKT_SUCCESS):
                self.traktConfig['accessToken'] = result['accessToken']
                self.traktConfig['refreshToken'] = result['refreshToken']
                self.__SaveConfig()
            return result['code']
        else:
            self.logger.ShowMessage("User already authorized", UI.SUCCESS_LOG)

        return StatusCodes.TRAKT_SUCCESS
    
    def BackupTrakt(self):
        self.logger.ShowMessage("Starting backup process...")
        self.exporter.CreateExportFolders()
        self.__BackupHistory()
        self.__BackupRatings()
        self.logger.ShowMessage("Backup finished. Check any red logs for errors")
    
    def __BackupHistory(self):
        if (not self.__TraktUserAuthorized()):
            self.logger.ShowMessage("User is not authorized (missing trakt settings). Error: {} {}".format(StatusCodes.TRAKT_UNAUTHORIZED, StatusCodes.statusMessages[StatusCodes.TRAKT_UNAUTHORIZED]), UI.ERROR_LOG)
            return StatusCodes.TRAKT_UNAUTHORIZED
        
        self.logger.ShowMessage("Starting history backup...")

        playsFound = 0
        playsProcessed = 0

        plays, statusCode = self.trakt.GetHistory(self.traktConfig['clientID'], self.traktConfig['accessToken'])

        # Backup history data to database
        if (statusCode == StatusCodes.TRAKT_SUCCESS):
            playsFound = len(plays)
            playsProcessed = self.__ProcessTraktPlays(plays)

        if (playsProcessed != playsFound):
            self.logger.ShowMessage("History backup to database finished with errors. Plays found: {}. Plays successfully stored: {}. Check previous logs for more info".format(playsFound, playsProcessed), UI.ERROR_LOG)
        else:
            self.logger.ShowMessage("History backup to database finished. Plays found: {} Plays successfully stored: {}".format(playsFound, playsProcessed), UI.SUCCESS_LOG)
            statusCode = StatusCodes.CONTROLLER_OK

        self.logger.ShowMessage("Exporting history data to json...")

        # Backup history data to json file
        statusCode = self.exporter.ExportData(plays, Folders.HISTORY_FOLDER, 'trakt history')
        if (statusCode != StatusCodes.EXPORTER_OK):
            self.logger.ShowMessage("Exporting history data to json file failed. Check previous logs", UI.ERROR_LOG)
        else:
            self.logger.ShowMessage("History data successfully exported to json file", UI.SUCCESS_LOG)
    
    def __BackupRatings(self):
        self.logger.ShowMessage("Starting backup of ratings...")
        errors = ''
        statusCode = self.__BackupRatingsByType("movies")
        if (statusCode != StatusCodes.EXPORTER_OK):
            errors = errors + 'movies'

        statusCode = self.__BackupRatingsByType("episodes")
        if (statusCode != StatusCodes.EXPORTER_OK):
            errors = errors + 'episodes'

        statusCode = self.__BackupRatingsByType("seasons")
        if (statusCode != StatusCodes.EXPORTER_OK):
            errors = errors + 'seasons'

        statusCode = self.__BackupRatingsByType("shows")
        if (statusCode != StatusCodes.EXPORTER_OK):
            errors = errors + 'shows'

        if (len(errors) != 0):
            self.logger.ShowMessage("Ratings backup finished with errors. Not exported: {}. Check previous logs".format(errors), UI.ERROR_LOG)
        else:
            self.logger.ShowMessage("Ratings backup finished", UI.SUCCESS_LOG)

    def __BackupRatingsByType(self, type):
        folder = Folders.RATINGS_FOLDER
        ratings, statusCode = self.trakt.GetRatings(type ,self.traktConfig['clientID'], self.traktConfig['accessToken'])
        if (statusCode == StatusCodes.TRAKT_SUCCESS):
            self.logger.ShowMessage("Exporting data to json...")
            statusCode = self.exporter.ExportData(ratings, folder, type)
            if (statusCode != StatusCodes.EXPORTER_OK):
                self.logger.ShowMessage("Error exporting {} ratings to json file. Check previous logs".format(type), UI.ERROR_LOG)
            else:
                self.logger.ShowMessage("{} ratings successfully exported to json file".format(type), UI.SUCCESS_LOG)
        else:
            self.logger.ShowMessage("Error getting {} ratings from trakt. Check previous logs".format(type), UI.ERROR_LOG)

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
            self.logger.ShowMessage("Request finished with an error. Check previous logs", UI.ERROR_LOG)
        else:
            statusCode = StatusCodes.CONTROLLER_OK

        return plays, statusCode
    
    def __ProcessTraktPlays(self, plays):

        episodes = []
        movies = []

        # Parse json objects
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
                self.logger.ShowMessage("Trakt settings loaded from database")
            else:
                self.logger.ShowMessage("No trakt settings found")
        else:
            self.logger.ShowMessage("An error occurred when loading trakt settings. Check previous logs", UI.ERROR_LOG)

        return traktConfig

    def __SaveConfig(self):
        statusCode = self.database.SaveTraktSettings(self.traktConfig['clientID'], self.traktConfig['clientSecret'], self.traktConfig['accessToken'], self.traktConfig['refreshToken'])
        if (statusCode == StatusCodes.DATABASE_OK):
            self.logger.ShowMessage("Settings saved to database", UI.SUCCESS_LOG)
        else:
            self.logger.ShowMessage("Could not save settings to database. Check previous logs", UI.ERROR_LOG)