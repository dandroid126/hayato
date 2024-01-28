import sqlite3
from sqlite3 import Error

from src import constants
from src import logger

global connection
global cursor

# Keeping these here for reference, but don't use them because formatted strings in queries are bad.
# TABLE_DB_SCHEMA = 'db_schema'
# COLUMN_ROWID = 'rowid'
# COLUMN_VERSION = 'version'

TAG = 'DbManager'


class DbManager:

    def __init__(self, path_to_db):
        """
        Initialize the Database object.

        Args:
            path_to_db (str): The path to the SQLite database file.
        """
        self.DB_SCHEMA_VERSION = 1
        self.path_to_db = path_to_db
        self.connection = None
        self.cursor = None

        try:
            self.connection = sqlite3.connect(path_to_db)
            self.cursor = self.connection.cursor()
            logger.i(TAG, "__init__(): Connection to SQLite DB successful")
        except Error as e:
            logger.e(TAG, "__init__(): Error occurred", e)

        self.upgrade_db_schema()

    def create_tables(self):
        """
        Creates tables in the database if they don't already exist.

        Note: This function assumes that a database connection has already been established.
        """
        logger.w(TAG, "create_tables(): create_tables: creating tables")

        # Create posts table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS announcements(
                id INTEGER PRIMARY KEY NOT NULL,
                time TEXT NOT NULL,
                channel INTEGER NOT NULL,
                message TEXT NOT NULL
            )
            """
        )

        # Create db_schema table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS db_schema(
                rowid INTEGER PRIMARY KEY NOT NULL,
                version INTEGER NOT NULL
            )
            """
        )

    def set_db_schema_version(self, version: int) -> bool:
        """
        Sets the database schema version.

        Args:
            version (int): The version number to set.

        Returns:
            bool: True if the version was successfully set, False otherwise.
        """
        # Prepare the query and parameters
        query = "INSERT OR REPLACE INTO db_schema VALUES(0, ?)"
        params = (version,)

        # Execute the query and commit the changes
        self.cursor.execute(query, params)
        self.connection.commit()

        return True

    def get_db_schema_version(self) -> int:
        """
        Get the version of the database schema.

        Returns:
            int: The version of the database schema.
        """
        query = "SELECT version FROM db_schema WHERE rowid = '0'"
        logger.i(TAG, f"get_db_schema_version(): executing: {query}")
        try:
            val = self.cursor.execute(query).fetchone()
            if val is not None:
                return val[0]
        except sqlite3.OperationalError:
            logger.i(TAG, "get_db_schema_version(): db_schema table not found. Assuming db_schema version is 0")
            return 0
        return 0

    def upgrade_db_schema(self):
        """
        Upgrades the database schema to the latest version.

        This function iterates through the database schema versions starting from the current version
        and performs the necessary upgrades to reach the latest version.
        """

        from_version = self.get_db_schema_version()

        while from_version < self.DB_SCHEMA_VERSION:
            upgrade = {
                # When upgrading the db schema version, increase DB_SCHEMA_VERSION, then add a function here with what to do to upgrade to that version.
                # The key is the db schema version being upgraded to.
                # The value is the name of the upgrade function.
                # Do not add parentheses, or it will get executed every time.
                1: self.create_tables,
            }

            upgrade.get(from_version + 1, lambda: None)()
            from_version += 1

        self.set_db_schema_version(self.DB_SCHEMA_VERSION)


db_manager = DbManager(constants.DB_PATH)
