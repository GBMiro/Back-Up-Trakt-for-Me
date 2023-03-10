import sqlite3
import json
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
        if (play['type'] == 'episode'):
            self.__InsertEpisode(play)
        else:
            self.__InsertMovie(play)

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
        
        message = "Play: {} - {}x{} {} {}".format(showTitle, season, number, episodeTitle, watchedAtLocal)
        self.__Log(message)


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
        
        message = "Play: {} ({}) {}".format(title, year, watchedAtLocal)
        self.__Log(message)


    def __ConvertToLocalTime(self, watchedAt):
        watchedAt = datetime.strptime(watchedAt, formatFrom)
        watchedAt = watchedAt.replace(tzinfo=tz.tzutc())
        watchedAt = watchedAt.astimezone(tz.tzlocal()).strftime(formatTo)
        return watchedAt

    def __CreateTables(self):
        if (not self.__TableCreated("episodes")):
            self.__CreateEpisodesTable()
        if (not self.__TableCreated("movies")):
            self.__CreateMoviesTable()

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
    
    def __Log(self, message):
        if (self.logger.GetStatus()):
            self.logger.ShowMessage(message)
        else:
            print(message)

    def __SaveChanges(self):
        self.connection.commit()