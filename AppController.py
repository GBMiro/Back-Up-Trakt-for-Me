from Trakt.TraktAPI import TraktAPI
from Database.DatabaseManager import DatabaseManager
from Exporter.ExporterJSON import ExporterJSON
from Utils.Logger import Logger
import Utils.Exporting as Folders
import Utils.Database as DB
import Utils.UI as UI
import Utils.Settings as Settings
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
        self.settings = self.__LoadConfig()
        self.trakt = TraktAPI(showLog)
        self.exporter = ExporterJSON(showLog, self.settings[Settings.BACKUP_FOLDER])


    def AuthorizeTraktUser(self):
        if not self.__TraktUserAuthorized():
            result = self.trakt.AuthorizeUser(self.settings[Settings.CLIENT_ID], self.settings[Settings.CLIENT_SECRET])
            if (result['code'] == StatusCodes.TRAKT_SUCCESS):
                self.settings[Settings.ACCESS_TOKEN] = result[Settings.ACCESS_TOKEN]
                self.settings[Settings.REFRESH_TOKEN] = result[Settings.REFRESH_TOKEN]
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
        self.__BackupCollection()
        self.__BackupWatched()
        self.__BackupWatchlist()
        self.logger.ShowMessage("Backup finished. Check any red logs for errors")
    
    def __BackupHistory(self):
        if (not self.__TraktUserAuthorized()):
            self.logger.ShowMessage("User is not authorized (missing trakt settings). Error: {} {}".format(StatusCodes.TRAKT_UNAUTHORIZED, StatusCodes.statusMessages[StatusCodes.TRAKT_UNAUTHORIZED]), UI.ERROR_LOG)
            return StatusCodes.TRAKT_UNAUTHORIZED
        
        self.logger.ShowMessage("Starting history backup...")

        playsFound = 0
        playsProcessed = 0

        plays, statusCode = self.trakt.GetHistory(self.settings[Settings.CLIENT_ID], self.settings[Settings.ACCESS_TOKEN])

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
        statusCode = self.exporter.ExportData(plays, Folders.WATCHED_FOLDER, 'history')
        if (statusCode != StatusCodes.EXPORTER_OK):
            self.logger.ShowMessage("Exporting history data to json file failed. Check previous logs", UI.ERROR_LOG)
        else:
            self.logger.ShowMessage("History data successfully exported to json file", UI.SUCCESS_LOG)
    
    def __BackupRatings(self):
        self.logger.ShowMessage("Starting backup of ratings...")
        errors = ''
        statusCodeMovies = self.__BackupTraktItemsByType("movies", Folders.RATINGS_FOLDER)
        statusCodeEpisodes = self.__BackupTraktItemsByType("episodes", Folders.RATINGS_FOLDER)
        statusCodeSeasons = self.__BackupTraktItemsByType("seasons", Folders.RATINGS_FOLDER)
        statusCodeShows = self.__BackupTraktItemsByType("shows", Folders.RATINGS_FOLDER)


        if (statusCodeMovies != StatusCodes.EXPORTER_OK or statusCodeEpisodes != StatusCodes.EXPORTER_OK
            or statusCodeSeasons != StatusCodes.EXPORTER_OK or statusCodeShows != StatusCodes.EXPORTER_OK):

            self.logger.ShowMessage("Ratings backup finished with errors. Check previous logs".format(errors), UI.ERROR_LOG)
        else:
            self.logger.ShowMessage("Ratings data successfully exported to json file", UI.SUCCESS_LOG)

    def __BackupCollection(self):
        self.logger.ShowMessage("Starting backup of collection...")
        statusCodeMovies = self.__BackupTraktItemsByType("movies", Folders.COLLECTION_FOLDER)
        statusCodeShows = self.__BackupTraktItemsByType("shows", Folders.COLLECTION_FOLDER)

        if (statusCodeMovies != StatusCodes.EXPORTER_OK or statusCodeShows != StatusCodes.EXPORTER_OK):
            self.logger.ShowMessage("Collection backup finished with errors. Check previous logs", UI.ERROR_LOG)
        else:
            self.logger.ShowMessage("Collection data successfully exported to json file", UI.SUCCESS_LOG)
        

    def __BackupWatchlist(self):
        self.logger.ShowMessage("Starting backup of watchlist...")
        statusCodeMovies = self.__BackupTraktItemsByType("movies", Folders.WATCHLIST_FOLDER)
        statusCodeShows = self.__BackupTraktItemsByType("shows", Folders.WATCHLIST_FOLDER)

        if (statusCodeMovies != StatusCodes.EXPORTER_OK and statusCodeShows != StatusCodes.EXPORTER_OK):
            self.logger.ShowMessage("Watchlist backup finished with errors. Check previous logs", UI.ERROR_LOG)
        else:
            self.logger.ShowMessage("Watchlist data successfully exported to json file", UI.SUCCESS_LOG)

    def __BackupWatched(self):
        self.logger.ShowMessage("Starting backup of watched...")
        statusCodeMovies = self.__BackupTraktItemsByType("movies", Folders.WATCHED_FOLDER)
        statusCodeShows = self.__BackupTraktItemsByType("shows", Folders.WATCHED_FOLDER)

        if (statusCodeMovies != StatusCodes.EXPORTER_OK and statusCodeShows != StatusCodes.EXPORTER_OK):
            self.logger.ShowMessage("Watched backup finished with errors. Check previous logs", UI.ERROR_LOG)
        else:
            self.logger.ShowMessage("Watched data successfully exported to json file", UI.SUCCESS_LOG)
    
    def __BackupTraktItemsByType(self, type, folder):
        clientID = self.settings[Settings.CLIENT_ID]
        accessToken = self.settings[Settings.ACCESS_TOKEN]

        if (folder == Folders.COLLECTION_FOLDER):
            data, statusCode = self.trakt.GetCollection(type, clientID, accessToken)
        elif (folder == Folders.RATINGS_FOLDER):
            data, statusCode = self.trakt.GetRatings(type, clientID, accessToken)
        elif (folder == Folders.WATCHED_FOLDER):
            data, statusCode = self.trakt.GetWatched(type, clientID, accessToken)
        elif (folder == Folders.WATCHLIST_FOLDER):
            data, statusCode = self.trakt.GetWatchlist(type, clientID, accessToken)

        if (statusCode == StatusCodes.TRAKT_SUCCESS):
            self.logger.ShowMessage("Exporting data to json...")
            statusCode = self.exporter.ExportData(data, folder, type)
            if (statusCode != StatusCodes.EXPORTER_OK):
                self.logger.ShowMessage("Error exporting {} {} to json file. Check previous logs".format(type, folder), UI.ERROR_LOG)
            else:
                self.logger.ShowMessage("{} {} successfully exported to json file".format(type, folder), UI.SUCCESS_LOG)
        else:
            self.logger.ShowMessage("Error getting {} {} from trakt. Check previous logs".format(type, folder), UI.ERROR_LOG)
        
        return statusCode
        
    def GetAccessToken(self):
        return self.settings[Settings.ACCESS_TOKEN]
    
    def GetRefreshToken(self):
        return self.settings[Settings.REFRESH_TOKEN]
    
    def GetClientID(self):
        return self.settings[Settings.CLIENT_ID]
    
    def GetClientSecret(self):
        return self.settings[Settings.CLIENT_SECRET]
    
    def GetBackupFolder(self):
        return self.settings[Settings.BACKUP_FOLDER]
    
    def SetTraktConfig(self, clientID, clientSecret):
        self.settings[Settings.CLIENT_ID] = clientID
        self.settings[Settings.CLIENT_SECRET] = clientSecret
        self.__SaveConfig()

    def SetBackupFolder(self, folder):
        self.settings[Settings.BACKUP_FOLDER] = folder
        self.exporter.SetBackupFolder(folder)
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
    
    def RefreshTraktToken(self):
        self.logger.ShowMessage("Refreshing access token...")
        accessToken, refreshToken, statusCode = self.trakt.RefreshToken(self.settings[Settings.CLIENT_ID], self.settings[Settings.CLIENT_SECRET], self.settings[Settings.REFRESH_TOKEN])
        if (statusCode == StatusCodes.TRAKT_SUCCESS):
            self.settings[Settings.ACCESS_TOKEN] = accessToken
            self.settings[Settings.REFRESH_TOKEN] = refreshToken
            self.__SaveConfig()
        else:
            self.logger.ShowMessage("Could not refresh token. Check previous logs", UI.ERROR_LOG)
    
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
        if (len(self.settings[Settings.ACCESS_TOKEN]) == 64):
            return True
        else:
            return False
        
    def __LoadConfig(self):
        data, statusCode = self.database.GetSettings()

        settings = {Settings.CLIENT_ID : "", Settings.CLIENT_SECRET : "", Settings.ACCESS_TOKEN : "", Settings.REFRESH_TOKEN : "", Settings.USER : "", Settings.BACKUP_FOLDER : ""}

        if (statusCode == StatusCodes.DATABASE_OK):
            if (len(data) != 0):
                settings = {
                    'clientID' : data[0][DB.CLIENT_ID_COLUMN],
                    'clientSecret' : data[0][DB.CLIENT_SECRET_COLUMN],
                    'accessToken' : data[0][DB.ACCESS_TOKEN_COLUMN],
                    'refreshToken' : data[0][DB.REFRESH_TOKEN_COLUMN],
                    'user' : data[0][DB.USER_COLUMN],
                    'backupFolder' : data[0][DB.BACKUP_FOLDER_COLUMN]
                }
                self.logger.ShowMessage("Settings loaded from database")
            else:
                self.logger.ShowMessage("No settings found")
        else:
            self.logger.ShowMessage("An error occurred when loading settings. Check previous logs", UI.ERROR_LOG)

        return settings

    def __SaveConfig(self):
        statusCode = self.database.SaveSettings(self.settings[Settings.CLIENT_ID], self.settings[Settings.CLIENT_SECRET], self.settings[Settings.ACCESS_TOKEN], self.settings[Settings.REFRESH_TOKEN], self.settings[Settings.USER], self.settings[Settings.BACKUP_FOLDER])
        if (statusCode == StatusCodes.DATABASE_OK):
            self.logger.ShowMessage("Settings saved to database", UI.SUCCESS_LOG)
        else:
            self.logger.ShowMessage("Could not save settings to database. Check previous logs", UI.ERROR_LOG)