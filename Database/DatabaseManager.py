import sqlite3
import json
import Utils.StatusCodes as StatusCodes
import Utils.Database as DB
from Utils.Logger import Logger
from datetime import datetime
from dateutil import tz

formatFrom="%Y-%m-%dT%H:%M:%S.000Z"
formatTo="%Y-%m-%d %H:%M:%S"

class DatabaseManager():

    def __init__(self, showLog):
        self.logger = Logger(showLog, "DATABASE")
        self.connection = ""
        self.cursor = ""
        self.__CheckTables()

    def OpenDatabase(self):
        self.connection = sqlite3.connect(".\\Database\\trakt_history.db")
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()


    def CloseDatabase(self):
        self.__SaveChanges()
        self.cursor.close()
        self.connection.close()

    def AddPlay(self, play):
        statusCode = StatusCodes.DATABASE_OK
        try:
            if (play['type'] == 'episode'):
                self.__InsertEpisode(play)
            else:
                self.__InsertMovie(play)
        except sqlite3.Error as err:
            statusCode = StatusCodes.DATABASE_ERROR
            message = "Error inserting play into database. {}".format(err)
            self.logger.ShowMessage(message)
        finally:
            return statusCode

    def __ExecuteQuery(self, query, params=()):
        statusCode = StatusCodes.DATABASE_OK
        try:
            self.cursor.execute(query, params)
            data = self.cursor.fetchall()
        except sqlite3.Error as err:
            self.logger.ShowMessage("An error occurred: {}".format(err))
            data = None
            statusCode = StatusCodes.DATABASE_ERROR
        finally:
            return data, statusCode

    def GetHistory(self):
        self.OpenDatabase()
        self.logger.ShowMessage("Selecting all plays")
        data, statusCode = self.__ExecuteQuery(DB.GET_HISTORY)
        self.CloseDatabase()
        return data, statusCode
    
    def GetMovies(self):
        self.OpenDatabase()
        self.logger.ShowMessage("Selecting movie plays")
        data, statusCode = self.__ExecuteQuery(DB.GET_MOVIES)
        self.CloseDatabase()
        return data, statusCode
        
    def GetEpisodes(self):
        self.OpenDatabase()
        self.logger.ShowMessage("Selecting episode plays")
        data, statusCode = self.__ExecuteQuery(DB.GET_EPISODES)
        self.CloseDatabase()
        return data, statusCode
    
    def GetTraktSettings(self):
        self.OpenDatabase()
        self.logger.ShowMessage("Loading trakt settings...")
        data, statusCode = self.__ExecuteQuery(DB.GET_TRAKT_SETTINGS)
        self.CloseDatabase()    
        return data, statusCode
    
    def SaveTraktSettings(self, clientID, clientSecret, accessToken, refreshToken):
        self.logger.ShowMessage("Saving trakt settings...")
        self.OpenDatabase()
        data, statusCode = self.__ExecuteQuery(DB.GET_TRAKT_SETTINGS)
        
        if (statusCode == StatusCodes.DATABASE_OK):  
            query = DB.UPDATE_SETTINGS if (len(data) != 0) else DB.INSERT_SETTINGS
            data, statusCode = self.__ExecuteQuery(query, (clientID, clientSecret, accessToken, refreshToken))
        self.CloseDatabase()
        return statusCode

    def __InsertEpisode(self, play):
        playID = play['id']
        type = play['type']
        watchedAt = play['watched_at']
        watchedAtLocal = self.__ConvertToLocalTime(watchedAt)
        season = play['episode']['season']
        number = play['episode']['number']
        episodeTitle = play['episode']['title']
        runtime = play['episode']['runtime']
        episodeIDs = play['episode']['ids']
        showTitle = play['show']['title']
        showYear = play['show']['year']
        showIDs = play['show']['ids']

        self.cursor.execute(DB.INSERT_EPISODE,
                            (playID, watchedAt, watchedAtLocal, type, season, number,
                            episodeTitle, json.dumps(episodeIDs), runtime, showTitle, showYear, json.dumps(showIDs)))
        
        message = "Processing: {} - {}x{} {} {}".format(showTitle, season, number, episodeTitle, watchedAtLocal)
        self.logger.ShowMessage(message)


    def __InsertMovie(self, play):
        playID = play['id']
        type = play['type']
        watchedAt = play['watched_at']
        watchedAtLocal = self.__ConvertToLocalTime(watchedAt)
        title = play['movie']['title']
        year = play['movie']['year']
        runtime = play['movie']['runtime']
        movieIDs = play['movie']['ids']

        self.cursor.execute(DB.INSERT_MOVIE,
                            (playID, watchedAt, watchedAtLocal, type, title, year, runtime, json.dumps(movieIDs)))
        
        message = "Processing: {} ({}) {}".format(title, year, watchedAtLocal)
        self.logger.ShowMessage(message)


    def __ConvertToLocalTime(self, watchedAt):
        watchedAt = datetime.strptime(watchedAt, formatFrom)
        watchedAt = watchedAt.replace(tzinfo=tz.tzutc())
        watchedAt = watchedAt.astimezone(tz.tzlocal()).strftime(formatTo)
        return watchedAt

    def __CheckTables(self):
        self.logger.ShowMessage("Checking tables...")
        self.OpenDatabase()
        self.__CreateTableIfNotExists(DB.EPISODES_TABLE, ("episodes"))
        self.__CreateTableIfNotExists(DB.MOVIES_TABLE, ("movies"))
        self.__CreateTableIfNotExists(DB.SETTINGS_TABLE, ("trakt_settings"))
        self.CloseDatabase()

    def __CreateTableIfNotExists(self, query, name):
        statusCode = StatusCodes.DATABASE_OK
        data, statusCode = self.__ExecuteQuery(DB.CHECK_TABLE, (name,))
        if (statusCode == StatusCodes.DATABASE_OK):
            createTable = False if (len(data) > 0) else True
            if (createTable):
                data, statusCode = self.__ExecuteQuery(query)
                if (statusCode != StatusCodes.DATABASE_OK):
                    message = "An error occurred creating {} table. Check previous logs".format(name)
                else:
                    message = "{} table created".format(name)
            else:
                message = "{} table found".format(name)
        else:
            message = "An error occurred checking {} table. Check previous logs".format(name)
        self.logger.ShowMessage(message)
                    
    def __SaveChanges(self):
        self.connection.commit()