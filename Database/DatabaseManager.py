import sqlite3
import Utils.StatusCodes as StatusCodes
import Utils.Database as DB
from Utils.Logger import Logger


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
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def AddPlays(self, params, type):
        self.OpenDatabase()
        statusCode = StatusCodes.DATABASE_OK
        query = DB.INSERT_EPISODE if (type == 'episode') else DB.INSERT_MOVIE
        totalInserted = 0
        
        # Indexes match table column order
        movieMessage = "Play: {4} ({5}) {3}"
        episodeMessage = "Play: {9} - {4}x{5} {6} {2}"

        for play in params:
            data, statusCode = self.__ExecuteQuery(query, play)
            message = movieMessage.format(*play) if (query == DB.INSERT_MOVIE) else episodeMessage.format(*play)
            if (statusCode == StatusCodes.DATABASE_OK):
                self.logger.ShowMessage(message)
                totalInserted += 1
            else:
                self.logger.ShowMessage("Failed to add play. {}. Check previous logs.".format(message))
        self.CloseDatabase()
        return totalInserted

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