

# EPISODE TABLE COLUMN NAMES

SEASON_COLUMN = "season"
NUMBER_COLUMN = "number"
EPISODE_TITLE_COLUMN = "episode_title"
EPISODE_IDS_COLUMN = "episode_IDs"
SHOW_COLUMN = "show_title"
SHOW_YEAR_COLUMN = "show_year"
SHOW_IDS_COLUMN = "show_IDs"

# MOVIES TABLE COLUMN NAMES

TITLE_COLUMN = "title"
MOVIE_IDS_COLUMN = "movie_ids"
YEAR_COLUMN = "year"


#  SHARED COLUMN NAMES

ID_COLUMN = "play_ID"
TRAKT_DATE_COLUMN = "watched_at"
DATE_COLUMN = "watched_at_local"
TYPE_COLUMN = 'type'
RUNTIME_COLUMN = "runtime"

# SETTINGS COLUMNS

CLIENT_ID_COLUMN = "client_id"
CLIENT_SECRET_COLUMN = "client_secret"
ACCESS_TOKEN_COLUMN = "access_token"
REFRESH_TOKEN_COLUMN = "refresh_token"
BACKUP_FOLDER_COLUMN = "backup_folder"


# GET DATA QUERYS

GET_HISTORY = """SELECT type, play_ID, show_title as "title", episode_title, season, number, watched_at_local
                FROM episodes
                WHERE watched_at_local like "%{}%"
                UNION
                SELECT type, play_ID, title, NULL, NULL, NULL, watched_at_local
                FROM movies
                WHERE watched_at_local like "%{}%"
                ORDER BY watched_at_local DESC"""

GET_EPISODES = """SELECT type, play_ID, show_title as "title", episode_title, season, number, watched_at_local
                FROM episodes
                WHERE watched_at_local like "%{}%"
                ORDER BY watched_at_local DESC"""

GET_MOVIES = """SELECT *
            FROM movies
            WHERE watched_at_local like "%{}%"
            ORDER BY watched_at_local DESC"""

GET_HISTORY_YEARS = """ SELECT strftime('%Y', watched_at_local) as year
                        FROM episodes
						GROUP BY year
                        UNION
                        SELECT strftime('%Y', watched_at_local)
                        FROM movies
                        GROUP BY strftime('%Y', watched_at_local)
                        ORDER BY strftime('%Y', watched_at_local) DESC
                        """

GET_SETTINGS = """SELECT * FROM settings"""



# INSERT QUERYS

INSERT_EPISODE = """INSERT INTO episodes VALUES (?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT (play_ID) DO NOTHING"""

INSERT_MOVIE = """INSERT INTO movies VALUES (?,?,?,?,?,?,?,?) ON CONFLICT (play_ID) DO NOTHING"""

INSERT_SETTINGS = """INSERT INTO settings VALUES (?,?,?,?,?) ON CONFLICT (client_id, client_secret) DO NOTHING"""

# UPDATE QUERYS

UPDATE_SETTINGS = """UPDATE settings
                        SET client_id = ?, client_secret = ?, access_token = ?, refresh_token = ?, backup_folder = ?"""

DELETE_TOKENS = """ UPDATE settings
                    SET access_token = "", refresh_token = "" """

# TABLES CHECK & CREATION

CHECK_TABLE = """SELECT name FROM sqlite_master WHERE type='table' AND name = ?"""

SETTINGS_TABLE = """
            CREATE TABLE "settings" (
            "client_id" TEXT,
            "client_secret" TEXT,
            "access_token" TEXT,
            "refresh_token" TEXT,
            "backup_folder" TEXT,
            PRIMARY KEY("client_id", "client_secret"))
        """

EPISODES_TABLE = """
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
        """

MOVIES_TABLE = """
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
        """