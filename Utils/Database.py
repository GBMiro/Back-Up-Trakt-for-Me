

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


# QUERYS

HISTORY = """SELECT type, play_ID, show_title as "title", episode_title, season, number, watched_at_local
                FROM episodes
                UNION
                SELECT type, play_ID, title, NULL, NULL, NULL, watched_at_local
                FROM movies
                ORDER BY watched_at_local DESC"""

EPISODES = """SELECT type, play_ID, show_title as "title", episode_title, season, number, watched_at_local
                FROM episodes
                ORDER BY watched_at_local DESC"""

MOVIES = """SELECT *
            FROM movies
            ORDER BY watched_at_local DESC"""


# INSERT QUERYS

INSERT_EPISODE = """INSERT INTO episodes VALUES (?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT (play_ID) DO NOTHING"""

INSERT_MOVIE = """INSERT INTO movies VALUES (?,?,?,?,?,?,?,?) ON CONFLICT (play_ID) DO NOTHING"""


# TABLES CHECK & CREATION

CHECK_TABLE = """SELECT name FROM sqlite_master WHERE type='table' AND name = ?"""

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