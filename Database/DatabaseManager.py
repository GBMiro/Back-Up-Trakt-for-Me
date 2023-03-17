import sqlite3
import json
import Utils.StatusCodes as StatusCodes
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
        self.__CreateTables()
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

        

    def GetHistory(self):
        self.logger.ShowMessage("Selecting all plays")
        statusCode = StatusCodes.DATABASE_OK
        try:
            self.cursor.execute("""SELECT type, play_ID, show_title as "title", episode_title, season, number, watched_at_local
                                FROM episodes
                                UNION
                                SELECT type, play_ID, title, NULL, NULL, NULL, watched_at_local
                                FROM movies
                                ORDER BY watched_at_local DESC""")
            data = self.cursor.fetchall()
        except sqlite3.Error as err:
            self.logger.ShowMessage("An error occurred: {}".format(err))
            data = None
            statusCode = StatusCodes.DATABASE_ERROR
        finally:
            return data, statusCode

    
    def GetMovies(self):
        self.logger.ShowMessage("Selecting movie plays")
        statusCode = StatusCodes.DATABASE_OK
        try:
            self.cursor.execute("""SELECT type, play_ID, title, NULL, NULL, NULL, watched_at_local
                                FROM movies
                                ORDER BY watched_at_local DESC""")
            data = self.cursor.fetchall()
        except sqlite3.Error as err:
            self.logger.ShowMessage("An error occurred: {}".format(err))
            data = None
            statusCode = StatusCodes.DATABASE_ERROR
        finally:
            return data, statusCode

    def GetEpisodes(self):
        self.logger.ShowMessage("Selecting episode plays")
        statusCode = StatusCodes.DATABASE_OK
        try:
            self.cursor.execute("""SELECT type, play_ID, show_title as "title", episode_title, season, number, watched_at_local
                            FROM episodes
                            ORDER BY watched_at_local DESC""")
            data = self.cursor.fetchall()
        except sqlite3.Error as err:
            self.logger.ShowMessage("An error occurred: {}".format(err))
            data = None
            statusCode = StatusCodes.DATABASE_ERROR
        finally:
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

        self.cursor.execute("INSERT INTO episodes VALUES (?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT (play_ID) DO NOTHING",
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

        self.cursor.execute("INSERT INTO movies VALUES (?,?,?,?,?,?,?,?) ON CONFLICT (play_ID) DO NOTHING",
                            (playID, watchedAt, watchedAtLocal, type, title, year, runtime, json.dumps(movieIDs)))
        
        message = "Processing: {} ({}) {}".format(title, year, watchedAtLocal)
        self.logger.ShowMessage(message)


    def __ConvertToLocalTime(self, watchedAt):
        watchedAt = datetime.strptime(watchedAt, formatFrom)
        watchedAt = watchedAt.replace(tzinfo=tz.tzutc())
        watchedAt = watchedAt.astimezone(tz.tzlocal()).strftime(formatTo)
        return watchedAt

    def __CreateTables(self):
        try:
            if (not self.__TableCreated("episodes")):
                self.__CreateEpisodesTable()
            if (not self.__TableCreated("movies")):
                self.__CreateMoviesTable()
        except sqlite3.Error as err:
            self.logger.ShowMessage("Error creating tables. {}".format(err))

    def __TableCreated(self, name):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (name,))
        return True if len(self.cursor.fetchall()) > 0 else False

    def __CreateEpisodesTable(self):
        self.cursor.execute("""
            CREATE TABLE "episodes" (
            "play_ID" INTEGER NOT NULL,
            "watched_at" TEXT NOT NULL,
            "watched_at_local" TEXT NOT NULL,
            "type" TEXT NOT NULL,
            "season" INTEGER NOT NULL,
            "number" INTEGER NOT NULL, 
            "episode_title" TEXT,
            "episode_IDs" TEXT NOT NULL,
            "runtime" INTEGER NOT NULL,
            "show_title" TEXT NOT NULL,
            "show_year" INTEGER NOT NULL,
            "show_IDs" TEXT NOT NULL,
            PRIMARY KEY("play_ID"))
        """)

        self.logger.ShowMessage("Episodes table created")


    def __CreateMoviesTable(self):
        self.cursor.execute("""
            CREATE TABLE "movies" (
            "play_ID" INTEGER NOT NULL,
            "watched_at" TEXT NOT NULL,
            "watched_at_local" TEXT NOT NULL,
            "type" TEXT NOT NULL,
            "title" TEXT NOT NULL,
            "year" INTEGER NOT NULL,
            "runtime" INTEGER NOT NULL,
            "movie_ids" TEXT NOT NULL,
            PRIMARY KEY("play_ID"))
        """)

        self.logger.ShowMessage("Movies table created")

    def __SaveChanges(self):
        self.connection.commit()