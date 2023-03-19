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
        self.OpenDatabase()
        self.__CheckTables()
        self.CloseDatabase()

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

    def __Get(self, query):
        statusCode = StatusCodes.DATABASE_OK
        try:
            self.cursor.execute(query)
            data = self.cursor.fetchall()
        except sqlite3.Error as err:
            self.logger.ShowMessage("An error occurred: {}".format(err))
            data = None
            statusCode = StatusCodes.DATABASE_ERROR
        finally:
            return data, statusCode

    def GetHistory(self):
        self.logger.ShowMessage("Selecting all plays")
        data, statusCode = self.__Get(DB.HISTORY)
        return data, statusCode
    
    def GetMovies(self):
        self.logger.ShowMessage("Selecting movie plays")
        data, statusCode = self.__Get(DB.MOVIES)
        return data, statusCode
        
    def GetEpisodes(self):
        self.logger.ShowMessage("Selecting episode plays")
        data, statusCode = self.__Get(DB.EPISODES)
        return data, statusCode

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
        try:
            if (not self.__TableCreated("episodes")):
                self.__CreateTable(DB.EPISODES_TABLE)
                self.logger.ShowMessage("Episodes table created")
            if (not self.__TableCreated("movies")):
                self.__CreateTable(DB.MOVIES_TABLE)
                self.logger.ShowMessage("Movies table created")
        except sqlite3.Error as err:
            self.logger.ShowMessage("Error creating tables. {}".format(err))

    def __CreateTable(self, query):
        self.cursor.execute(query)

    def __TableCreated(self, name):
        self.cursor.execute(DB.CHECK_TABLE, (name,))
        return True if len(self.cursor.fetchall()) > 0 else False

    def __SaveChanges(self):
        self.connection.commit()